from model.tasks.arc import ARCTask
from model.models import *
import pandas as pd
import ast
import openai
import os
import re
import json
import numpy as np
from tqdm import tqdm
import traceback
import time
import gzip
import pickle

START = 1
END = 2
PROMPT_TESTING_MODE = False
EXCLUDING_COMPLETE_STEP = True

openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

input_price = 0.005 / 1_000
output_price = 0.015 / 1_000

if not os.path.exists(f'result/llm_dsl_understanding'):
    os.mkdir(f'result/llm_dsl_understanding')

for num_iter in range(START,END+1):
    iter_dir = f'result/llm_dsl_understanding/{num_iter}'
    if not os.path.exists(iter_dir):
        os.mkdir(iter_dir)
    for user_mode in ['optimal', 'C', 'E', 'G', 'F']:
        target_file_name = f'result/filtered_final_merged_logs_{user_mode}.csv'
        save_dir = f'{iter_dir}/{user_mode}'
        df_full_dsl = pd.read_csv(target_file_name)
        problem_list = df_full_dsl['problem'].unique()
        count = 0
        json_error_count = 0
        finish_reason_error_count = 0
        task = ARCTask()
        prompt_testing_problem_list = [1, 20, 95] #[1, 4, 100, 6, 103, 10, 20, 250, 62, 95]
        prompt_testing_mode = PROMPT_TESTING_MODE
        excluding_complete_step = EXCLUDING_COMPLETE_STEP

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        for i in ['full']: # ['no', 'comments', 'functions', 'full']
            given_dsl_txt = i #'comments'
            dsl_file = f'' if given_dsl_txt == 'no' else f'data/new_dsl_{given_dsl_txt}.txt'
            finish_reason_error_csv_file_path = f'{save_dir}/[finish_reason_error]checking_test-{prompt_testing_mode}_dsl-{given_dsl_txt}.csv'
            json_error_csv_file_path = f'{save_dir}/[json_error]checking_test-{prompt_testing_mode}_dsl-{given_dsl_txt}.csv'
            result_csv_file_path = f'{save_dir}/[total-result]checking_test-{prompt_testing_mode}_dsl-{given_dsl_txt}.csv'
            except_error_csv_file_path = f'{save_dir}/[except_error]checking_test-{prompt_testing_mode}_dsl-{given_dsl_txt}.csv'

            if prompt_testing_mode:
                problem_list = prompt_testing_problem_list

            if os.path.isfile(result_csv_file_path):
                previous_result_df = pd.read_csv(result_csv_file_path, encoding='iso-8859-1')
                previous_problem_list = previous_result_df['problem'].unique()
                problem_list = list(set(problem_list) - set(previous_problem_list))

            fixed_prompt = '''
            Do you know ARC problem?
            
            ARC is a quiz and if we can solve this problem we understand and utilize several concepts such like 'object', 'count', 'color', 'move', 'row', 'column' and etc.
            I want to evaluate whether you understand DSL before solving the ARC problem. 
            I will provide the input, dsl_functions_list, and the dsl_list that should be applied to the input.
            Apply the DSLs in the dsl_list sequentially to the input to create the final output grid. 
            Utilizing the dsl_functions_list will help you understand which DSLs you need to use.
            
            =========
            {dsl_list}
            =========
            The arguments for the DSL are mainly 'state' and 'object'. However, some require 'color', 'row', 'column', etc.
            The 'state' is the current state of the grid, which means the entire grid.
            The 'object' is the list of coordinates of the object; there may be multiple objects in the grid, but no DSL requires multiple objects.
            The 'color' is the color of the pixel in the grid, which is a number between 0 and 9.
            The 'row' and 'column' are the coordinate numbers of a pixel in the grid. Additionally, 'row' and 'column' start from 0.
            =========
            
            input: {input_grid}
            
            objects: {initial_object}
            
            dsl_list: {dsl_full}
            
            Generate the grid step by step by applying the DSLs in the 'dsl_list' to the input grid.
            '''

            format_message = '''
            Apply the dsl_list to the given input grid in order to create the final output grid. Leave a log as follows each time you apply a DSL from the dsl_list:
            {
                'step': 'Step number'
                'dsl': 'DSL used from the dsl_list'
                'grid': 'Grid after applying the DSL'
                'objects': 'Objects in the grid after applying the DSL'
            }
            
            if final output grid is created, please submit the final output grid.
            {
                'step': 'Step number'
                'dsl': 'DSL used from the dsl_list to make the final output grid'
                'grid': 'Final output grid'
                'objects': 'Objects in the final output grid'
            }
            
            For example,
            The applied DSL is pixel_color([(2, 1)], 4). And step is first time. 
            And the grid is below.
            [[0, 0, 0], [1, 1, 0], [0, 3, 3]]
            
            And objects is below
            {'object1': [[1, 0], [1, 1]], 'object2': [[2, 1], [2, 2]]}
            
            then you should submit the log as below.
            {
                'step': 2,
                'dsl': 'pixel_color([(5, 4)], 4)',
                'grid': [[0, 0, 0], [1, 1, 0], [0, 4, 0]],
                'objects': {'object1': [[1, 0], [1, 1]], 'object2': [[2, 1], [2, 2]]},
            }
            
            You should follow the above format(json). Remember, format is important.
            And you don't stop until you get the final output grid. If you can't get the final output grid, you should keep trying.
            It is mean that the reason of 'finish_reason' is not 'stop'.
            
            
            You must not use "Same as the previous grid or objects" even if the previous grid or objects are the same. 
            You must include that information exactly as it is in the corresponding value for the key in the JSON.
            
            I repeat, make sure to complete the entire process without stopping midway! Also, you must generate a log in JSON format! Keep this in mind!
            
            And generate step by step. If you can't generate the final output grid, you should keep trying.
            '''

            def preprocessing_dsl(dsl):
                dsl_name = dsl.split('(')[0]
                dsl_args = dsl[len(dsl_name):].replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                return dsl_name + '(' + dsl_args + ')'


            if given_dsl_txt != 'no':
                with open(dsl_file, 'r', encoding='utf-8') as f:
                    dsl_list_prompt = f.read()
            else:
                dsl_list_prompt = ''

            for problem_num in tqdm(problem_list):
                try:
                    print(f'Problem number: {problem_num}')
                    examples, quiz, temp_object, temp_state, _ = task.get_input(problem_num)
                    full_dsl_str = df_full_dsl[df_full_dsl['problem'] == problem_num]['excluding_complete_full_dsl'].values[0] if excluding_complete_step else df_full_dsl[df_full_dsl['problem'] == problem_num]['full_dsl'].values[0]
                    problem_id = df_full_dsl[df_full_dsl['problem'] == problem_num]['problem_id'].values[0]
                    problem_id = problem_id.split('.')[0]
                    total_result_file_path = f'{save_dir}/[total_result]checking_test-{prompt_testing_mode}_dsl-{given_dsl_txt}_{problem_num}_{problem_id}.pkl'
                    label_output = ast.literal_eval(df_full_dsl[df_full_dsl['problem'] == problem_num]['output'].values[0])
                    correct = None

                    # Transform the full_dsl string to replace square brackets with parentheses
                    split_dsl = ast.literal_eval(full_dsl_str)
                    preprocessed_dsl = [preprocessing_dsl(dsl) for dsl in split_dsl]

                    step_count = int(df_full_dsl[df_full_dsl['problem'] == problem_num]['excluding_complete_step'].values[0]) if excluding_complete_step else int(df_full_dsl[df_full_dsl['problem'] == problem_num]['step'].values[0])
                    if len(split_dsl) != step_count:
                        with open('result/[dsl_full_not_same_error]checking_test-{prompt_testing_mode}_dsl-{given_dsl_txt}.txt', 'a') as f:
                            f.write(f'{problem_num}: not same number of dsl and step\n')


                    query_prompt = fixed_prompt.format(input_grid=temp_state, initial_object=temp_object, dsl_list=dsl_list_prompt, dsl_full=full_dsl_str)

                    gpt_output, finish_reason, res_choices, input_prompt, success_flag, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list = cot_chatgpt(query_prompt, step=len(split_dsl), assistant_prompt=format_message, model=openai.deployment_name, temperature=0.7, max_tokens=4096, n=1, stop=None, excluding_complete_step=excluding_complete_step)
                    str_gpt_output = " ".join(gpt_output)

                    if finish_reason != 'stop':
                        finish_reason_error_count += 1

                        finish_reason_time = time.time()
                        finish_reason_local_time = time.localtime(finish_reason_time)
                        format_finish_reason_local_time = time.strftime('%Y-%m-%d %H:%M:%S', finish_reason_local_time)

                        finish_reason_error_log_data = {
                            "problem": [problem_num],
                            "problem_id": [problem_id],
                            "finish_reason": [finish_reason],
                            "total_cost": [np.cumsum(num_tokens_input_list) * input_price + np.cumsum(num_tokens_output_list) * output_price],
                            "time": [format_finish_reason_local_time],
                        }

                        df_log = pd.DataFrame(finish_reason_error_log_data)

                        if not os.path.isfile(finish_reason_error_csv_file_path):
                            df_log.to_csv(finish_reason_error_csv_file_path, index=False)
                        else:
                            df_log.to_csv(finish_reason_error_csv_file_path, mode='a', header=False, index=False)

                    # TODO 밑에 정확도 측정하는 if else문 추가하기. 이를 위해서 아마 파싱을 잘 해야할 것 같음.
                    pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)
                    matches = pattern.findall(str_gpt_output)

                    parsed_logs = []
                    json_error_flag = False
                    for match in matches:
                        if 'step' not in match:
                            continue
                        try:
                            if 'grid' not in match:
                                raise json.JSONDecodeError('grid key not in match', match, 0)
                            if success_flag == False:
                                raise json.JSONDecodeError('Fail generate full step.', match, 0)

                            try:
                                parsed_log = json.loads(match)
                            except json.JSONDecodeError as e:
                                try:
                                    parsed_log = json.loads(match.replace("'", '"'))
                                except json.JSONDecodeError as e:
                                    try:
                                        parsed_log = json.loads(match.replace('"', "'"))
                                    except json.JSONDecodeError as e:
                                        try:
                                            parsed_dict = ast.literal_eval(match)
                                            parsed_log = json.dumps(parsed_dict)
                                        except Exception as e:
                                            continue

                            parsed_logs.append(parsed_log)

                        except json.JSONDecodeError as e:
                            print(f"JSONDecodeError: {e}")

                            json_error_time = time.time()
                            json_error_local_time = time.localtime(json_error_time)
                            format_json_error_local_time = time.strftime('%Y-%m-%d %H:%M:%S', json_error_local_time)

                            json_error_log_data = {
                                "problem": [problem_num],
                                "problem_id": [problem_id],
                                "error": [e],
                                "error_traceback": [traceback.format_exc()],
                                "total_cost": [np.cumsum(num_tokens_input_list) * input_price + np.cumsum(num_tokens_output_list) * output_price],
                                "time": [format_json_error_local_time],
                            }
                            json_error_flag = True

                            df_json = pd.DataFrame(json_error_log_data)

                            if not os.path.isfile(json_error_csv_file_path):
                                df_json.to_csv(json_error_csv_file_path, index=False)
                            else:
                                df_json.to_csv(json_error_csv_file_path, mode='a', header=False, index=False)

                    if json_error_flag:
                        json_error_flag = False
                        json_error_count += 1
                    else:
                        if np.array_equal(parsed_logs[-1]['grid'], label_output):
                            count += 1
                            correct = True
                        else:
                            correct = False

                    result_time = time.time()
                    result_local_time = time.localtime(result_time)
                    format_result_local_time = time.strftime('%Y-%m-%d %H:%M:%S', result_local_time)

                    total_result_log_data = {
                        "problem": [problem_num],
                        "problem_id": [problem_id],
                        "input_grid": [temp_state],
                        "objects": [temp_object],
                        "prompt": [input_prompt],
                        "str_gpt_output": [str_gpt_output],
                        "gpt_output": [gpt_output],
                        "final_grid": [parsed_logs[-1]['grid']],
                        "label_grid": [label_output],
                        "correct": [correct],
                        "json": [parsed_logs],
                        "num_input_tokens": [num_tokens_input_list],
                        "num_output_tokens": [num_tokens_output_list],
                        "num_total_tokens": [num_tokens_total_list],
                        "cumulative_tokens": [np.cumsum(num_tokens_total_list)],
                        "total_cost": [num_tokens_input_list[-1] * input_price + num_tokens_output_list[-1] * output_price],
                        "time": [format_result_local_time],
                    }

                    with gzip.open(total_result_file_path, 'wb') as f:
                        pickle.dump(total_result_log_data, f)

                    result_log_data = {
                        "problem": [problem_num],
                        "problem_id": [problem_id],
                        "input_grid": [temp_state],
                        "final_grid": [parsed_logs[-1]['grid']],
                        "label_grid": [label_output],
                        "correct": [correct],
                        "total_cost": [num_tokens_input_list[-1] * input_price + num_tokens_output_list[-1] * output_price],
                        "time": [format_result_local_time],
                    }

                    df_result = pd.DataFrame(result_log_data)

                    if not os.path.isfile(result_csv_file_path):
                        df_result.to_csv(result_csv_file_path, index=False)
                    else:
                        df_result.to_csv(result_csv_file_path, mode='a', header=False, index=False)

                    exit()
                except Exception as e:
                    print(f"Error: {problem_num}")
                    print(e)

                    except_time = time.time()
                    except_local_time = time.localtime(except_time)
                    format_except_local_time = time.strftime('%Y-%m-%d %H:%M:%S', except_local_time)

                    except_error_log_data = {
                        "problem": [problem_num],
                        "problem_id": [problem_id],
                        "error": [str(e)],
                        "error_traceback": [traceback.format_exc()],
                        "time": [format_except_local_time],
                    }

                    df_except_error = pd.DataFrame(except_error_log_data)

                    if not os.path.isfile(except_error_csv_file_path):
                        df_except_error.to_csv(except_error_csv_file_path, index=False)
                    else:
                        df_except_error.to_csv(except_error_csv_file_path, mode='a', header=False, index=False)

            print(f'Number of correct outputs: {count}/{len(problem_list)}')
            print(f'Number of JSON errors: {json_error_count}')
            print(f'Number of finish reason errors: {finish_reason_error_count}')
