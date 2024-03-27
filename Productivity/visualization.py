import os
import json
from utils import write_file, plot_2d_grid, augmented_path, result_path
import warnings
warnings.filterwarnings('ignore')

# Set the variables.
target_files = os.listdir(augmented_path)
kinds_of_problem = set()
prev_name = ''
html = ''
augmented_count = 0
total_count = 0

# Make the visualization html files for each kinds of conceptARC categories.
for i, target_file in enumerate(target_files):
    kind_of_problem = target_file.split('_')[0]

    if i != 0:
        if kind_of_problem not in kinds_of_problem:
            write_file(html, prev_name, dir_path=result_path)
            print(f'{prev_name}: {augmented_count}')
            total_count += augmented_count
            augmented_count = 0
            kinds_of_problem.update([kind_of_problem])
            html = ''
            prev_name = kind_of_problem
    else:
        kinds_of_problem.update([kind_of_problem])
        prev_name = kind_of_problem
        count = 0 

    with open(f"{augmented_path}/{target_file}", 'r') as f:
        data = json.load(f)

    train_data = data['train']
    target_file_name = target_file.split('.json')[0]
    temp_html, temp_count = plot_2d_grid(train_data, target_file_name)
    html += temp_html
    augmented_count += temp_count

print(f'{prev_name}: {augmented_count}')
total_count += augmented_count
write_file(html, prev_name, dir_path=result_path)
print(f'total count: {total_count}')
