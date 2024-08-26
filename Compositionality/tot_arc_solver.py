import argparse
from model.methods.bfs import arc_solve
from model.tasks.arc import ARCTask
import json
import os
import openai
import pandas as pd
import traceback
from tqdm import tqdm
import time
import numpy as np
import gzip
import pickle
from model.errors import save_exception_log, InvalidDSLUsageError, InvalidObjectUsageError, \
    InvalidPixelUsageError, NonExistentDSLError, NonExistentColorError, DSLInternalLogicError, \
    ParseError

# Set variable related with Azure OpenAI
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
MODE = 'main'
PROMPT_TESTING_MODE = True
START = 1
END = 1

def main(i, include_test_output, additional_info, mode):
    input_price = 0.005 / 1_000
    output_price = 0.015 / 1_000

    # include_test_output = False
    # planning_mode = False
    # additional_info = False

    args = argparse.Namespace(backend=openai.deployment_name, temperature=0.7, task='arc', naive_run=False, prompt_sample='standard', method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=3, n_evaluate_sample=1, n_select_sample=2)
    df_filtered_problem = pd.read_csv('result/filtered_final_merged_logs.csv')
    df_add_info = pd.read_csv('data/add_info/add_info_tasks.csv')

    task = ARCTask(dsl_file='new_dsl_full.txt')

    if not os.path.exists(f'result/ToT'):
        os.mkdir(f'result/ToT')

    if not os.path.exists(f'result/ToT/exp-{i}'):
        os.mkdir(f'result/ToT/exp-{i}')

    save_dir = f'result/ToT/exp-{i}/[{mode}]test-output-{include_test_output}_additional-info-{additional_info}'
    except_error_csv_file_path = f'{save_dir}/except_error_logs.csv'

    prompt_testing_problem_list = [1, 4, 6, 10, 20, 62, 95, 100, 103, 250] #df_add_info['problem'].unique()  # [1, 4, 6, 10, 20, 62, 95, 100, 103, 250]

    problem_index_list = df_filtered_problem[df_filtered_problem['problem'].isin(prompt_testing_problem_list)]['problem'].unique() if PROMPT_TESTING_MODE else df_filtered_problem['problem'].unique()
    problem_id_list = df_filtered_problem[df_filtered_problem['problem'].isin(problem_index_list)]['problem_id'].unique() if PROMPT_TESTING_MODE else df_filtered_problem['problem_id'].unique()


    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # Solve ARC task with tot prompts and DSLs
    for problem_id, problem_index in tqdm(zip(problem_id_list, problem_index_list)):
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
            print(f'******************* index: {problem_index} ******************')
            print(f'******************* id: {problem_id} ******************')

            InvalidObjectUsageError_flag = False
            NonExistentDSLError_flag = False
            DSLInternalLogicError_flag = False
            InvalidDSLUsageError_flag = False
            InvalidPixcelUsageError_flag = False
            NonExistentColorError_flag = False
            ParseError_flag = False
            ExceptionError_flag = False


            if not os.path.exists(target_task_file_name):
                ys, infos, total_result = arc_solve(args, task, problem_index, input_price, output_price, include_test_output, additional_info, df_add_info)

                infos['problem_id'] = problem_id
                infos['problem'] = str(problem_index)

                total_result['problem_id'] = problem_id
                total_result['problem'] = str(problem_index)

                result_time = time.time()
                result_local_time = time.localtime(result_time)
                format_result_local_time = time.strftime('%Y-%m-%d %H:%M:%S', result_local_time)

                infos['result_time'] = format_result_local_time
                total_result['result_time'] = format_result_local_time
                total_result['corrects'] = [total_result['selections'][-1]['complete_corrects'] + total_result['selections'][-1]['selected_corrects']]
                total_result['correct'] = True if np.sum(total_result['corrects']) > 0 else False
                sample_cost = np.sum([np.sum(result['step_cost']) for result in total_result['samples']])
                value_cost = np.sum([np.sum(result['step_cost']) for result in total_result['values']])
                total_result['total_cost'] = sample_cost + value_cost

                infos['total_cost'] = sample_cost + value_cost
                infos['correct'] = True if np.sum(total_result['corrects']) > 0 else False

                with gzip.open(f'{save_dir}/[total_result]{problem_index}_{problem_id}.pkl', 'wb') as f:
                    pickle.dump(total_result, f)

                # save result json file
                with open(target_task_file_name, 'w') as f:
                    json.dump(infos, f, indent=4)

            else:
                continue
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
                name = f'test-output-{include_test_output}_additional-info-{additional_info}'
                print('=============================================')
                print(f'exp-{i} {name}')
                main(i, include_test_output, additional_info, mode)