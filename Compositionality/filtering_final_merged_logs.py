import pandas as pd
import numpy as np
import ast
import random

random.seed(777)
np.random.seed(777)

MODE = 'C'

# Load the completeness_problem.csv
completeness_df = pd.read_csv('result/completeness_problem.csv')

# Load the final_merged_logs.xlsx
final_merged_logs_df = pd.read_excel('result/final_merged_logs.xlsx')
checker_Df = pd.read_csv('result/checker_log.csv')

# Filter rows from final_merged_logs_df based on problem column in completeness_df
filtered_final_merged_logs = final_merged_logs_df[final_merged_logs_df['problem'].isin(completeness_df['problem'])]

# Define the columns for the final dataframe
columns = ['user_id', 'problem', 'problem_id', 'dsl', 'full_dsl', 'step', 'correct', 'output', 'excluding_complete_step', 'excluding_complete_full_dsl']

# Initialize lists to store the rows for the final dataframe and excluded rows
final_data = []

# Priority order
priority_target = ['C', 'E', 'G', 'F']
if MODE == 'optimal':
    priority_order = priority_target
else:
    priority_order = [priority_target.pop(priority_target.index(MODE))]
    priority_order += random.sample(priority_target, k=len(priority_target))

# Loop through the filtered dataframe
for problem_id, group in filtered_final_merged_logs.groupby('problem'):
    temp_data = []
    for _, row in group.iterrows():
        for user_id in priority_order:
            correct_col = f'correct_{user_id}' if user_id else 'correct'
            dsl_col = f'dsl_{user_id}' if user_id else 'dsl'

            if user_id == 'C':
                full_dsl_col = 'full_dsl'
            elif user_id in ['B', 'D', 'A']:
                full_dsl_col = None
            else:
                full_dsl_col = f'full_dsl_{user_id}'

            # Check if output column exists based on user_id
            output_col = f'output_{user_id}' if user_id else 'output'

            if correct_col in row and row[correct_col]:
                if dsl_col in row and (full_dsl_col in row or full_dsl_col is None):
                    dsl_list = ast.literal_eval(row[dsl_col]) if pd.notna(row[dsl_col]) else []
                    temp_data.append({
                        'user_id': user_id,
                        'problem': row['problem'],
                        'problem_id': row['problem_id'],
                        'correct': row[correct_col],
                        'dsl': row[dsl_col],
                        'full_dsl': row[full_dsl_col] if full_dsl_col else None,
                        'step': len(dsl_list),
                        'output': row[output_col] if output_col in row else None,
                        'excluding_complete_step': len(dsl_list)-1 if 'complete' in dsl_list else len(dsl_list),
                        'excluding_complete_full_dsl': str(ast.literal_eval(row[full_dsl_col])[:-1])if 'complete' in dsl_list else row[full_dsl_col],
                    })
            if row['problem'] in [86, 141]:
                if dsl_col in row and (full_dsl_col in row or full_dsl_col is None):
                    dsl_list = ast.literal_eval(row[dsl_col]) if pd.notna(row[dsl_col]) else []
                    temp_data.append({
                        'user_id': user_id,
                        'problem': row['problem'],
                        'problem_id': row['problem_id'],
                        'correct': row[correct_col],
                        'dsl': row[dsl_col],
                        'full_dsl': row[full_dsl_col] if full_dsl_col else None,
                        'step': len(dsl_list),
                        'output': row[output_col] if output_col in row else None,
                        'excluding_complete_step': len(dsl_list)-1 if 'complete' in dsl_list else len(dsl_list),
                        'excluding_complete_full_dsl': str(ast.literal_eval(row[full_dsl_col])[:-1])if 'complete' in dsl_list else row[full_dsl_col],
                    })

    if temp_data:
        # Sort by DSL length
        temp_data.sort(key=lambda x: x['step'])

        for data in temp_data:
            if data['user_id'] not in ['B', 'D', 'A']:
                final_data.append(data)
                break
        else:
            # If all shortest are excluded, choose based on priority order
            temp_data.sort(
                key=lambda x: priority_order.index(x['user_id']) if x['user_id'] in priority_order else float('inf'))
            final_data.append(temp_data[0])

# Identify the excluded problems
selected_problems = set(row['problem'] for row in final_data)
excluded_problems = set(filtered_final_merged_logs['problem']) - selected_problems

# Process the excluded rows to set the required fields
excluded_processed_data = []
for problem in excluded_problems:
    excluded_rows = filtered_final_merged_logs[filtered_final_merged_logs['problem'] == problem]
    for _, row in excluded_rows.iterrows():
        excluded_processed_data.append({
            'user_id': np.nan,
            'problem': row['problem'],
            'problem_id': row['problem_id'],
            'correct': False,
            'dsl': np.nan,
            'full_dsl': np.nan,
            'step': np.nan,
            'output': np.nan,
        })

# Combine the final dataframe and the processed excluded dataframe
final_combined_df = pd.DataFrame(final_data + excluded_processed_data, columns=columns)

# Save the final combined dataframe to a CSV file
final_save_path = f'result/filtered_final_merged_logs_{MODE}.csv'
final_combined_df.to_csv(final_save_path, index=False)

# TODO user에 따른 csv파일 저장하도록 만들기

# Save the excluded dataframe to a separate CSV file for reference
excluded_save_path = f'result/excluded_final_merged_logs_{MODE}.csv'
excluded_df = pd.DataFrame(excluded_processed_data, columns=columns)
excluded_df.to_csv(excluded_save_path, index=False)

with open(f'result/filtered_final_merged_logs_priority_order_{MODE}.txt', 'w') as f:
    f.write(str(priority_order))

# Print the final dataframe to check the result
print(final_combined_df)

# Print the excluded dataframe to check the excluded rows
print(excluded_df)
