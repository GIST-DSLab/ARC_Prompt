import ast
import os.path

import numpy as np
import pandas as pd
import json
import gzip
import pickle
import matplotlib.pyplot as plt

# Set the mode, method, start, and end values
MODE = 'main'
METHOD = 'CoT'
START = 1
END = 10

# Check the arc_solver_result for each experiment to calcuate the accuracy
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

        if method == 'CoT':
            if not np.array_equal(target_arc_task["test"][0]["input"], target_task['input_grid'][0]):
                print(f'ARC Input grid is not matched , problem_index: {problem_index}, problem_id: {problem_id}, target_file is {target_task_file_name}')
                error_count += 1
                continue

        if target_task['correct'][0] if type(target_task['correct']) == list else target_task['correct']:
            correct_count += 1
            correct_id_list.append(problem_id)
            correct_index_list.append(problem_index)
        else:
            incorrect_count += 1

    for flag in error_flags:
        error_flag_counts[flag] = df_except_info[flag].sum() if exist_except_info else 0

    print(f'Total number of tasks: {total_num}')
    print(f'Correct count: {correct_count}')
    print(f'Error count: {error_count}')
    print(f'Not exist count: {not_exist_count}')

    correct_rate = correct_count / total_num
    print(f'Correct rate: {correct_rate:.2f}')
    print(f'Correct id list: {correct_id_list}')
    print(f'Correct index list: {correct_index_list}')

    return correct_rate, correct_id_list, correct_index_list, correct_count, incorrect_count, error_flag_counts

if __name__ == '__main__':
    results = []
    total_results = []
    FF_results = []
    FT_results = []
    TF_results = []
    TT_results = []
    mode = MODE
    method = METHOD
    start = START
    end = END

    cumulative_data_avg = {
        'Correct': [],
        'Incorrect': [],
        'Configuration': [],
    }

    cumulative_data_over_runs = {
        True: {
            False: {
                'Correct': [],
                'Incorrect': [],
                'Configuration': [],
            },
            'MC-LARC': {
                'Correct': [],
                'Incorrect': [],
                'Configuration': [],
            },
        },
        False: {
            False: {
                'Correct': [],
                'Incorrect': [],
                'Configuration': [],
            },
            'MC-LARC': {
                'Correct': [],
                'Incorrect': [],
                'Configuration': [],
            },
        },
    }

    for flag in ['invalid_object_usage_error', 'non_existent_dsl_error', 'dsl_internal_logic_error',
                 'invalid_dsl_usage_error', 'invalid_pixel_usage_error', 'non_existent_color_error', 'parse_error',
                 'exception_error']:
        for include_test_output in [False, True]:
            for additional_info in [False, "MC-LARC"]:
                cumulative_data_over_runs[include_test_output][additional_info][flag] = []
        cumulative_data_avg[flag] = []

    for i in range(start, end+1):
        cumulative_data = {
            'Correct': [],
            'Incorrect': [],
            'Configuration': [],
        }

        for flag in ['invalid_object_usage_error', 'non_existent_dsl_error', 'dsl_internal_logic_error',
                     'invalid_dsl_usage_error', 'invalid_pixel_usage_error', 'non_existent_color_error', 'parse_error',
                     'exception_error']:
            cumulative_data[flag] = []

        configurations = []

        for include_test_output in [False, True]:
            for additional_info in [False, "MC-LARC"]:
                total_correct = 0
                total_incorrect = 0
                total_error_flags = {flag: 0 for flag in ['invalid_object_usage_error', 'non_existent_dsl_error',
                                                          'dsl_internal_logic_error', 'invalid_dsl_usage_error',
                                                          'invalid_pixel_usage_error', 'non_existent_color_error',
                                                          'parse_error', 'exception_error']}

                name = f'test-output-{include_test_output}_additional-info-{additional_info}'
                correct_rate, correct_id_list, correct_index_list, correct_count, incorrect_count, error_flag_counts = main(i, include_test_output, additional_info, method, mode)
                total_correct += correct_count
                total_incorrect += incorrect_count
                for flag in total_error_flags:
                    total_error_flags[flag] += error_flag_counts[flag]

                results.append([i, name, correct_count, incorrect_count, error_flag_counts])

                cumulative_data['Correct'].append(total_correct)
                cumulative_data['Incorrect'].append(total_incorrect)
                cumulative_data['Configuration'].append(name)
                configurations.append(name)
                for flag in total_error_flags:
                    cumulative_data[flag].append(total_error_flags[flag])

                if i == START:
                    cumulative_data_over_runs[include_test_output][additional_info]['Correct'].append(total_correct)
                    cumulative_data_over_runs[include_test_output][additional_info]['Incorrect'].append(total_incorrect)
                    cumulative_data_over_runs[include_test_output][additional_info]['Configuration'].append(name)
                    for flag in total_error_flags:
                        cumulative_data_over_runs[include_test_output][additional_info][flag].append(total_error_flags[flag])
                else:
                    cumulative_data_over_runs[include_test_output][additional_info]['Correct'][-1] += total_correct
                    cumulative_data_over_runs[include_test_output][additional_info]['Incorrect'][-1] += total_incorrect
                    for flag in total_error_flags:
                        cumulative_data_over_runs[include_test_output][additional_info][flag][-1] += total_error_flags[flag]

        # Plotting the cumulative graph
        df_cumulative = pd.DataFrame(cumulative_data)

        ax = df_cumulative.plot(kind='bar', stacked=True, figsize=(10, 6))

        plt.title(f'Cumulative Correct, Incorrect, and Error Counts - Experiment {i}, {name}')
        plt.xlabel('Name of Configuration')
        plt.ylabel('Counts')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.grid(False)
        plt.tight_layout()

        ax.set_xticklabels(configurations, rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(f'result/{method}/[{mode}_{start}-{end}]cumulative_graph_exp_{i}_{name}.png')

        results.append([i, name, correct_rate, correct_id_list, correct_index_list, correct_count, incorrect_count,total_error_flags])

    # Plotting the average cumulative graph
    for include_test_output in [False, True]:
        for additional_info in [False, "MC-LARC"]:
            name = cumulative_data_over_runs[include_test_output][additional_info]['Configuration']
            for key in cumulative_data_over_runs[include_test_output][additional_info].keys():
                if key != 'Configuration':
                    cumulative_data_avg[key] += ([x / (END - START + 1) for x in cumulative_data_over_runs[include_test_output][additional_info][key]])
                else:
                    cumulative_data_avg[key] += (cumulative_data_over_runs[include_test_output][additional_info][key])

    # checking
    for i in range(len(cumulative_data_avg['Configuration'])):
        if 158 != round(sum([cumulative_data_avg[k][i] for k in cumulative_data_avg if k != 'Configuration']),1):
            print(f'Error: {include_test_output}, {additional_info}')
            print(f'Have problem.')
            print(round(sum([cumulative_data_over_runs[include_test_output][additional_info][k][0] for k in cumulative_data_over_runs[include_test_output][additional_info] if k != 'Configuration']),1))

    df_cumulative_avg = pd.DataFrame(cumulative_data_avg)
    df_cumulative_avg.to_csv(f'result/{method}/[{mode}_{start}-{end}]cumulative_avg.csv')

    ax = df_cumulative_avg.plot(kind='bar', stacked=True, figsize=(10, 6))

    plt.ylabel('Average Counts')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(False)
    plt.tight_layout()

    ax.set_xticklabels(cumulative_data_avg['Configuration'], rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig(f'result/{METHOD}/[{MODE}_{START}-{END}]cumulative_graph_avg.png')
    # plt.show()

    df = pd.DataFrame(results, columns=['Experiment', 'Configuration', 'Correct Rate', 'Correct Problem ID', 'Correct Problem Index', 'Correct Count', 'Incorrect Count', 'Error Flags'])

    # Extracting Correct Rate and Correct Problem ID/Index from the results
    df['Correct Rate'] = df.apply(lambda row: row['Correct Count'] / (row['Correct Count'] + row['Incorrect Count']),axis=1)

    df_correct_problem_id = df[['Experiment', 'Configuration', 'Correct Problem ID']].explode('Correct Problem ID')
    df_correct_problem_index = df[['Experiment', 'Configuration', 'Correct Problem Index']].explode('Correct Problem Index')

    # Pivot the dataframe to get the desired format
    df_pivot = df.pivot_table(index='Experiment', columns='Configuration', values='Correct Rate')
    df_pivot = df_pivot.rename(columns={'test-output-True_additional-info-MC-LARC': 'accuracy'})

    df_correct_problem_index.to_csv(f'result/{method}/[{mode}_{start}-{end}]correct_index.csv')
    df_correct_problem_id.to_csv(f'result/{method}/[{mode}_{start}-{end}]correct_id.csv')
    df_pivot.to_csv(f'result/{method}/[{mode}_{start}-{end}]accuracy_matrix.csv')

    print("=============================================")

    column_means = df_pivot.mean()
    df_pivot.loc['Mean'] = column_means

    n = end - start + 1 if (end - start + 1) else end - start if end - start > 0 else 1
    variances = column_means * (1 - column_means) / n
    std_errors = np.sqrt(variances)
    confidence_intervals = 1.96 * std_errors

    lower_bounds = column_means - confidence_intervals
    upper_bounds = column_means + confidence_intervals

    # Combine lower and upper bounds with the original DataFrame
    df_confidence = pd.DataFrame({
        'Lower Bound': lower_bounds,
        'Upper Bound': upper_bounds,
        'Variance': variances,
        'Standard Deviation': std_errors
    })
    # Save the result to a CSV file
    df_result_with_confidence = pd.concat([df_pivot, df_confidence.T])
    df_result_with_confidence.to_csv(f'result/{method}/[{mode}_{start}-{end}]Accuracy_matrix_with_confidence.csv')
