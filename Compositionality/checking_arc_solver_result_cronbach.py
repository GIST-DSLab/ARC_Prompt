import ast
import os.path
import pingouin as pg

import numpy as np
import pandas as pd
import json
import gzip
import pickle

# Set the mode, method, start, and end values
MODE = 'main'
METHOD = 'CoT'
START = 1
END = 10

total_result_dict = {
        True: {
            False: {
            },
            'MC-LARC': {
            },
        },
        False: {
            False: {
            },
            'MC-LARC': {
            },
        },
    }

# Check the arc_solver_result and calculate the Cronbach's alpha
def main(include_test_output, additional_info, method, mode, start, end):
    for i in range(start, end+1):
        df_filtered_problem = pd.read_csv('result/filtered_final_merged_logs.csv')
        df_add_info = pd.read_csv('data/add_info/add_info_tasks.csv')

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
        total_num = len(target_problem_index_list)
        correct_count = 0
        incorrect_count = 0
        not_exist_count = 0
        error_count = 0
        correct_id_list = []
        correct_index_list = []
        error_flags = ['invalid_object_usage_error', 'non_existent_dsl_error', 'dsl_internal_logic_error',
                       'invalid_dsl_usage_error', 'invalid_pixel_usage_error', 'non_existent_color_error', 'parse_error',
                       'exception_error']
        checking_flag = dict()
        if i == start:
            for problem_id in target_problem_id_list:
                total_result_dict[include_test_output][additional_info][problem_id.split('.')[0]] = []

        for problem_id in total_result_dict[include_test_output][additional_info].keys():
            checking_flag[problem_id.split('.')[0]] = 0

        error_flag_counts = {flag: 0 for flag in error_flags}


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

            check_id = df_filtered_problem[df_filtered_problem['problem'] == problem_index]['problem_id'].values[0].split('.')[0]
            check_problem_index = df_filtered_problem[df_filtered_problem['problem_id'] == problem_id+'.json']['problem'].values[0]

            if check_problem_index != (int(problem_index[0]) if type(problem_index) == list else int(problem_index)) or check_id != (problem_id[0] if type(problem_index) == list else problem_id):
                print(f'problem_index: {int(problem_index[0]) if type(problem_index) == list else int(problem_index)}, problem_id: {problem_id[0] if type(problem_index) == list else problem_id} is not matched, target_file is {target_task_file_name}')
                print(f'check_problem_index: {check_problem_index}, check_id: {check_id}')
                print('\n\n')
                error_count += 1
                continue

            with open(target_arc_task_file_name, 'r') as f:
                target_arc_task = json.load(f)

            with gzip.open(target_total_result_file_name, 'rb') as f:
                total_result = pickle.load(f)

            if method == 'CoT':
                if not np.array_equal(target_arc_task["test"][0]["input"], target_task['input_grid'][0]):
                    print(f'ARC Input grid is not matched , problem_index: {problem_index}, problem_id: {problem_id}, target_file is {target_task_file_name}')
                    error_count += 1
                    continue

            if target_task['correct'][0] if type(target_task['correct']) == list else target_task['correct']:
                total_result_dict[include_test_output][additional_info][problem_id].append(1)
                if checking_flag[problem_id] != 0:
                    print(1)
                checking_flag[problem_id] = 1
            else:
                total_result_dict[include_test_output][additional_info][problem_id].append(0)
                if checking_flag[problem_id] != 0:
                    print(1)
                checking_flag[problem_id] = 1

        if os.path.exists(f'{save_dir}/except_error_logs.csv'):
            for row in df_except_info.iterrows():
                total_result_dict[include_test_output][additional_info][row[1]['problem_id']].append(0)
                if checking_flag[row[1]['problem_id']] != 0:
                    print(1)
                checking_flag[row[1]['problem_id']] = 1

    df_total_result = pd.DataFrame(total_result_dict[include_test_output][additional_info]).T
    df_cronbach_alpha = pg.cronbach_alpha(data=df_total_result)

    with open(f'result/{method}/cronbach_alpha_{mode}_test-output-{include_test_output}_additional-info-{additional_info}.txt', 'a') as f:
        f.write(str(df_cronbach_alpha))

    print(f'\n===============include_test_output {include_test_output}, additional_info {additional_info}  ================')
    print(df_cronbach_alpha)

    return

if __name__ == '__main__':
    results = []
    mode = MODE
    method = METHOD
    start = START
    end = END

    for include_test_output in [False, True]:
        for additional_info in [False, "MC-LARC"]:
            main(include_test_output, additional_info, method, mode, start, end)

