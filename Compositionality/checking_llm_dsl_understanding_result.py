import numpy as np
import pandas as pd
import ast
import pickle
import gzip

EXCLUDING_COMPLETE_STEP = True

# Checking LLM DSL understanding result.
for num_iter in range(1,3):
    iter_dir = f'result/llm_dsl_understanding/{num_iter}'
    for user_mode in ['optimal', 'C', 'E', 'G', 'F']:
        final_file_name = f'result/filtered_final_merged_logs_{user_mode}.csv'
        check_file_dir = f'{iter_dir}/{user_mode}'
        check_file_name = f'{check_file_dir}/[total-result]checking_test-False_dsl-full.csv'
        save_name = f'{iter_dir}/{user_mode}/[double_checking_result]checking_test-False_dsl-full.csv'

        df_full_dsl = pd.read_csv(final_file_name)
        df_llm_dsl_result = pd.read_csv(check_file_name)
        df_target = df_llm_dsl_result[df_llm_dsl_result['correct'].isna()]
        df_target_full_dsl = df_full_dsl[df_full_dsl['problem'].isin(df_target['problem'])]

        input_price = 0.005 / 1_000
        output_price = 0.015 / 1_000

        # Check the correctness of the result about nan correct value rows.
        for i, row in df_target_full_dsl.iterrows():
            with gzip.open(f'{check_file_dir}/[total_result]checking_test-False_dsl-full_{row["problem"]}_{row["problem_id"].split(".")[0]}.pkl', 'rb') as f:
                data = pickle.load(f)
            total_step = df_target_full_dsl[df_target_full_dsl['problem'] == row['problem']]['step'].values[0]

            if data['json'][0][-1]['step'] == total_step:
                if np.array_equal(data['json'][0][-1]['grid'], data['label_grid'][0]):
                    df_llm_dsl_result.loc[df_llm_dsl_result['problem'] == row['problem'], 'correct'] = True
                else:
                    df_llm_dsl_result.loc[df_llm_dsl_result['problem'] == row['problem'], 'correct'] = False

        # modify the total cost of the result because of considering total prompt message and outputs.
        for i, row in df_llm_dsl_result.iterrows():
            with gzip.open(f'{check_file_dir}/[total_result]checking_test-False_dsl-full_{row["problem"]}_{row["problem_id"].split(".")[0]}.pkl', 'rb') as f:
                data = pickle.load(f)
            num_input_tokens = np.sum(data['num_input_tokens'])
            num_output_tokens = np.sum(data['num_output_tokens'])

            input_cost = num_input_tokens * input_price
            output_cost = num_output_tokens * output_price

            df_llm_dsl_result.loc[df_llm_dsl_result['problem'] == row['problem'], 'total_cost'] = input_cost + output_cost

        correct_not_same_count = 0
        correct_not_same_file_list = []

        incorrect_not_same_count = 0
        incorrect_not_same_file_list = []

        for i, row in df_llm_dsl_result.iterrows():
            with gzip.open(f'{check_file_dir}/[total_result]checking_test-False_dsl-full_{row["problem"]}_{row["problem_id"].split(".")[0]}.pkl', 'rb') as f:
                data = pickle.load(f)

            prev_complete_index_list = []
            step = df_full_dsl[df_full_dsl['problem'] == row['problem']]['excluding_complete_step'].values[0] if EXCLUDING_COMPLETE_STEP else df_full_dsl[df_full_dsl['problem'] == row['problem']]['step'].values[0]
            df_llm_dsl_result.loc[df_llm_dsl_result['problem'] == row['problem'], 'step'] = step

            for j in prev_complete_index_list:
                if row['correct']:
                    if not np.array_equal(data['json'][0][j]['grid'], data['json'][0][j+1]['grid']):
                        correct_not_same_count += 1
                        break
                else:
                    if not np.array_equal(data['json'][0][j]['grid'], data['json'][0][j+1]['grid']):
                        incorrect_not_same_count += 1
                        break

        print(correct_not_same_count)
        print(('\n').join(correct_not_same_file_list))

        print(incorrect_not_same_count)
        print(('\n').join(incorrect_not_same_file_list))

        df_llm_dsl_result.to_csv(save_name, index=False)



