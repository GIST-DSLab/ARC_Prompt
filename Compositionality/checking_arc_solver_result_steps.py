import ast
import os.path

import numpy as np
import pandas as pd
import json
import gzip
import pickle

MODE = 'main'
METHOD = 'CoT'
START = 1
END = 10

def main(i, include_test_output, additional_info, method, mode):
    df_filtered_problem = pd.read_csv('result/filtered_final_merged_logs.csv')

    save_dir = f'result/{method}/exp-{i}/[{mode}]test-output-{include_test_output}_additional-info-{additional_info}'
    arc_dir = f'data/arc_dataset/'

    if os.path.exists(f'{save_dir}/except_error_logs.csv'):
        df_except_info = pd.read_csv(f'{save_dir}/except_error_logs.csv')
        exist_except_info = True
    else:
        exist_except_info = False

    PROMPT_TESTING_MODE = True if mode == 'sub' else False

    if not os.path.exists(save_dir):
        pass

    print("=============================================")
    print(f'exp-{i}')
    print(f'include_test_output: {include_test_output}, additional_info: {additional_info}')
    target_problem_index_list = [1, 4, 6, 10, 20, 62, 95, 100, 103, 250] if PROMPT_TESTING_MODE else df_filtered_problem['problem'].unique()
    target_problem_id_list = df_filtered_problem[df_filtered_problem['problem'].isin(target_problem_index_list)]['problem_id'].unique()
    not_exist_count = 0
    error_count = 0

    step_count = {x: 0 for x in range(11)}

    for problem_index, problem_id in zip(target_problem_index_list, target_problem_id_list):
        problem_id = problem_id.split('.')[0]
        target_task_file_name = f'{save_dir}/{problem_id}.json'
        target_total_result_file_name = f'{save_dir}/[total_result]{problem_index}_{problem_id}.pkl'
        target_arc_task_file_name = f'{arc_dir}/{problem_id}.json'

        if not os.path.exists(target_task_file_name):
            not_exist_count += 1
            continue

        with open(target_task_file_name, 'r') as f:
            target_task = json.load(f)

        # id와 problem_index가 일치하는지 체크
        check_id = df_filtered_problem[df_filtered_problem['problem'] == problem_index]['problem_id'].values[0].split('.')[0]
        check_problem_index = df_filtered_problem[df_filtered_problem['problem_id'] == problem_id+'.json']['problem'].values[0]

        if check_problem_index != (int(problem_index[0]) if type(problem_index) == list else int(problem_index)) or check_id != (problem_id[0] if type(problem_index) == list else problem_id):
            print(f'problem_index: {int(problem_index[0]) if type(problem_index) == list else int(problem_index)}, problem_id: {problem_id[0] if type(problem_index) == list else problem_id} is not matched, target_file is {target_task_file_name}')
            print(f'check_problem_index: {check_problem_index}, check_id: {check_id}')
            print('\n\n')
            error_count += 1
            continue
        # id와 input grid가 일치하는지 체크
        with open(target_arc_task_file_name, 'r') as f:
            target_arc_task = json.load(f)

        with gzip.open(target_total_result_file_name, 'rb') as f:
            total_result = pickle.load(f)

        step_count[len(target_task['total_dsl'][0])] += 1

    if exist_except_info:
        step_count[0] += len(df_except_info)

    return step_count

if __name__ == '__main__':
    total_results = {x: 0 for x in range(11)}
    FF_results = {x: 0 for x in range(11)}
    FT_results = {x: 0 for x in range(11)}
    TF_results = {x: 0 for x in range(11)}
    TT_results = {x: 0 for x in range(11)}
    mode = MODE
    method = METHOD
    start = START
    end = END

    for i in range(start, end+1):
        for include_test_output in [False, True]:
            for additional_info in [False, "MC-LARC"]:
                total_correct = 0
                total_incorrect = 0

                name = f'test-output-{include_test_output}_additional-info-{additional_info}'
                step_count = main(i, include_test_output, additional_info, method, mode)

                if include_test_output and additional_info:
                    for key in step_count.keys():
                        TT_results[key] += step_count[key]
                elif include_test_output and not additional_info:
                    for key in step_count.keys():
                        TF_results[key] += step_count[key]
                elif not include_test_output and additional_info:
                    for key in step_count.keys():
                        FT_results[key] += step_count[key]
                elif not include_test_output and not additional_info:
                    for key in step_count.keys():
                        FF_results[key] += step_count[key]

                for key in step_count.keys():
                    total_results[key] += step_count[key]

    TT_results = {k: v/10 for k, v in TT_results.items()}
    TF_results = {k: v/10 for k, v in TF_results.items()}
    FT_results = {k: v/10 for k, v in FT_results.items()}
    FF_results = {k: v/10 for k, v in FF_results.items()}
    total_results = {k: v/40 for k, v in total_results.items()}


    df_TT_result = pd.DataFrame(list(TT_results.items()), columns=['step', 'avg_counts'])
    df_TF_result = pd.DataFrame(list(TF_results.items()), columns=['step', 'avg_counts'])
    df_FT_result = pd.DataFrame(list(FT_results.items()), columns=['step', 'avg_counts'])
    df_FF_result = pd.DataFrame(list(FF_results.items()), columns=['step', 'avg_counts'])
    df_total_result = pd.DataFrame(list(total_results.items()), columns=['step', 'avg_counts'])

    df_TT_result.to_csv(f'result/{method}/[TT]step_counts.csv', index=False)
    df_TF_result.to_csv(f'result/{method}/[TF]step_counts.csv', index=False)
    df_FT_result.to_csv(f'result/{method}/[FT]step_counts.csv', index=False)
    df_FF_result.to_csv(f'result/{method}/[FF]step_counts.csv', index=False)
    df_total_result.to_csv(f'result/{method}/[total]step_counts.csv', index=False)



