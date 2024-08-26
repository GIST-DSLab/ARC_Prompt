import copy

from model.tasks.arc import ARCTask
import json
import os
import openai
import pandas as pd
import traceback
from tqdm import tqdm
import time
import ast
import numpy as np
import gzip
import pickle
from model.errors import save_exception_log, InvalidDSLUsageError, InvalidObjectUsageError, \
    InvalidPixelUsageError, NonExistentDSLError, NonExistentColorError, DSLInternalLogicError, \
    ParseError
from model.models import cot_chatgpt
from model.prompts.arc import cot_format_prompt, test_output_info, add_info

openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
MODE = 'main'
PROMPT_TESTING_MODE = False
START = 1
END = 10

def main(i, include_test_output, additional_info, mode):
    input_price = 0.005 / 1_000
    output_price = 0.015 / 1_000

    finish_reason_error_count = 0
    count = 0

    df_filtered_problem = pd.read_csv('result/filtered_final_merged_logs.csv')
    df_add_info = pd.read_csv('data/add_info/add_info_tasks.csv')

    if not os.path.exists(f'result/CoT/'):
        os.mkdir(f'result/CoT/')

    if not os.path.exists(f'result/CoT/exp-{i}'):
        os.mkdir(f'result/CoT/exp-{i}')

    task = ARCTask(dsl_file='new_dsl_full.txt')
    save_dir = f'result/CoT/exp-{i}/[{mode}]test-output-{include_test_output}_additional-info-{additional_info}'
    except_error_csv_file_path = f'{save_dir}/except_error_logs.csv'
    finish_reason_error_csv_file_path = f'{save_dir}/[finish_reason_error].csv'

    prompt_testing_problem_list = [1, 4, 6, 10, 20, 62, 95, 100, 103, 250]

    problem_index_list = df_filtered_problem[df_filtered_problem['problem'].isin(prompt_testing_problem_list)]['problem'].unique() if PROMPT_TESTING_MODE else df_filtered_problem['problem'].unique()
    problem_id_list = df_filtered_problem[df_filtered_problem['problem'].isin(problem_index_list)]['problem_id'].unique() if PROMPT_TESTING_MODE else df_filtered_problem['problem_id'].unique()

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # Solve ARC task with tot prompts and DSLs
    for problem_id, problem_index in zip(problem_id_list, problem_index_list):
        try:
            if PROMPT_TESTING_MODE:
                if problem_index not in prompt_testing_problem_list:
                    continue

            if os.path.exists(except_error_csv_file_path):
                df_except_error = pd.read_csv(except_error_csv_file_path)
                if problem_index in df_except_error['problem'].values:
                    continue

            problem_id = problem_id.split('.')[0]
            target_task_file_name = f'{save_dir}/{problem_id}.json'
            total_result_file_path = f'{save_dir}/[total_result]{problem_index}_{problem_id}.pkl'

            InvalidObjectUsageError_flag = False
            NonExistentDSLError_flag = False
            DSLInternalLogicError_flag = False
            InvalidDSLUsageError_flag = False
            InvalidPixcelUsageError_flag = False
            NonExistentColorError_flag = False
            ParseError_flag = False
            ExceptionError_flag = False

            total_dsl_list = []

            if not os.path.exists(total_result_file_path):
                # TODO-1: tot에서 sample prompt 내용 확인해서 재사용 가능한지 판단하기 => 사용 가능
                # TODO-2: tot에서 sample prompt 내용을 이용해서 prompt 생성하기

                # TODO-3: models에 있는 chatgpt 함수 사용해서 예외가 있는지 확인해보기, 만약 output token수가 부족하다고 생각되어지면 dsl_chatgpt에 mode를 추가해서 사용하기

                # TODO prompt 부분
                examples, quiz, object, state, label_grid = task.get_input(problem_index)
                init_state = copy.deepcopy(state)
                init_object = copy.deepcopy(object)

                if include_test_output:
                    test_output_info_prompt = test_output_info.format(test_output=label_grid)

                if additional_info:
                    target_column = None
                    if additional_info == 'MC-LARC':
                        target_column = 'description_output'
                    elif additional_info == 'LARC':
                        target_column = 'description_output'
                    elif additional_info == 'Fast-Flexible':
                        target_column = 'select_final_description'

                    add_info_prompt = add_info.format(add_info=df_add_info[df_add_info['problem'] == problem_index][target_column].values[0])


                prompt = task.cot_prompt_wrap(examples=examples, quiz=quiz, object=object, step=0, test_output_info=test_output_info_prompt if include_test_output else '', add_info=add_info_prompt if additional_info != False else '')


                # TODO openai api 호출하는 부분
                gpt_output, finish_reason, res_choices, input_prompt, success_flag, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, parsed_logs = cot_chatgpt(
                    prompt, step=task.steps, assistant_prompt=cot_format_prompt, model=openai.deployment_name,
                    temperature=0.7, max_tokens=4096, n=1, stop=None, use_env=True)

                str_gpt_output = " ".join(gpt_output)

                if finish_reason != 'stop':
                    finish_reason_error_count += 1

                    finish_reason_time = time.time()
                    finish_reason_local_time = time.localtime(finish_reason_time)
                    format_finish_reason_local_time = time.strftime('%Y-%m-%d %H:%M:%S', finish_reason_local_time)

                    finish_reason_error_log_data = {
                        "problem": [problem_index],
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

                # TODO 파싱해서 가져온 dsl을 환경에 적용하기
                for log in parsed_logs:
                    dsl = log['dsl']
                    total_dsl_list.append(dsl)
                    state, object = task.env.step(state, object, dsl)

                label_output = ast.literal_eval(df_filtered_problem[df_filtered_problem['problem'] == problem_index]['output'].values[0])
                # TODO 해당 task에 대한 정보 저장하기
                if np.array_equal(state, label_output):
                    count += 1
                    correct = True
                else:
                    correct = False

                result_time = time.time()
                result_local_time = time.localtime(result_time)
                format_result_local_time = time.strftime('%Y-%m-%d %H:%M:%S', result_local_time)

                total_result_log_data = {
                    "problem": [str(problem_index)],
                    "problem_id": [problem_id],
                    "input_grid": [init_state],
                    "objects": [init_object],
                    "prompt": [input_prompt],
                    "str_gpt_output": [str_gpt_output],
                    "gpt_output": [gpt_output],
                    "final_grid": [state],
                    "label_grid": [label_output],
                    "correct": [correct],
                    "total_dsl": [total_dsl_list],
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
                    "problem": [str(problem_index)],
                    "problem_id": [problem_id],
                    "input_grid": [init_state],
                    "final_grid": [state],
                    "label_grid": [label_output],
                    "total_dsl": [total_dsl_list],
                    "correct": [correct],
                    "total_step": [len(parsed_logs)],
                    "total_cost": [num_tokens_input_list[-1] * input_price + num_tokens_output_list[-1] * output_price],
                    "time": [format_result_local_time],
                }

                with open(target_task_file_name, 'w') as f:
                    json.dump(result_log_data, f, indent=4)

        # TODO 예외 처리 부분
        except InvalidObjectUsageError as e:
            InvalidObjectUsageError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except NonExistentDSLError as e:
            NonExistentDSLError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except DSLInternalLogicError as e:
            DSLInternalLogicError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except InvalidDSLUsageError as e:
            InvalidDSLUsageError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except InvalidPixelUsageError as e:
            InvalidPixcelUsageError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except NonExistentColorError as e:
            NonExistentColorError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except ParseError as e:
            ParseError_flag = True
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)
        except Exception as e:
            save_exception_log(e, problem_index, problem_id, except_error_csv_file_path, InvalidObjectUsageError_flag,
                               NonExistentDSLError_flag, DSLInternalLogicError_flag, InvalidDSLUsageError_flag,
                               InvalidPixcelUsageError_flag, NonExistentColorError_flag, ParseError_flag, ExceptionError_flag)

if __name__ == '__main__':
    mode = MODE
    start = START
    end = END
    for i in tqdm(range(start, end+1)):
        for include_test_output in [False, True]:
            for additional_info in [False, "MC-LARC"]:
                main(i, include_test_output, additional_info, mode)