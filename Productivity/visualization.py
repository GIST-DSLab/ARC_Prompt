import os
from tqdm import tqdm
import json
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import base64
from io import BytesIO

def string_to_array(grid):
    try:
        if isinstance(grid[0][0], int): return grid
    except:
        print(1)

    grid_array = []
    if type(grid) == float:
        target_grid = '[]'
    else:
        target_grid = grid.replace(']', '').split(', [')

    for index in range(len(target_grid)):
        grid_array.append(np.fromstring(target_grid[index].strip('['), sep=',', dtype=np.int64))

    try:
        output_grid_array = np.array(grid_array)
        flag = True
    except:
        output_grid_array = [-1]
        flag = False
    return output_grid_array, flag

def plot_2d_grid(task_id, answer, mode):
    for count, index in enumerate(task_id.keys()):
        if task_id[index] == '2.08E+20':
            task_id[index] == '20818e16'
            using_task_id = '20818e16'
        else:
            using_task_id = task_id[index] if len(task_id[index]) == 8 else ('').join(['0' for _ in range(8-len(task_id[index]))])+str(task_id[index])

        try:
            with open(f'data/evaluation/{using_task_id}.json', 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(e)
            print(f"using_task_id: {using_task_id}")
            print(f'task id: {task_id[index]}')
            continue
        cvals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        colors = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00", "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25"]
        norm = plt.Normalize(min(cvals), max(cvals))
        tuples = list(zip(map(norm, cvals), colors))
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

        fig, axs = plt.subplots(len(data['test']), 3, figsize=(5, len(data['test']) * 3 * 0.7))
        axs = axs.reshape(-1, 3)

        for i, example in enumerate(data['test']):
            axs[i, 0].set_title(f'Test Input {i + 1}')
            rows, cols = np.array(example['input']).shape
            axs[i, 0].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
            axs[i, 0].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
            axs[i, 0].tick_params(which='minor', size=0)
            axs[i, 0].grid(True, which='minor', color='#555555', linewidth=0.5)
            axs[i, 0].set_xticks([])
            axs[i, 0].set_yticks([])
            axs[i, 0].imshow(np.array(example['input']), cmap=cmap, vmin=0, vmax=9)

            axs[i, 1].set_title(f'Test Output {i + 1}')
            rows, cols = np.array(example['output']).shape
            axs[i, 1].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
            axs[i, 1].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
            axs[i, 1].tick_params(which='minor', size=0)
            axs[i, 1].grid(True, which='minor', color='#555555', linewidth=0.5)
            axs[i, 1].set_xticks([])
            axs[i, 1].set_yticks([])
            axs[i, 1].imshow(np.array(example['output']), cmap=cmap, vmin=0, vmax=9)
            break

        axs[i, 2].set_title(f'GPT Output {i + 1}')
        if type(answer['refine_prediction'][index]) == float: 
            answer['refine_prediction'][index] = '[]'
        
        target_array, flag = string_to_array(answer['refine_prediction'][index].replace('], \n ', '], '))
        if flag:
            rows, cols = np.array(target_array).shape
            axs[i, 2].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
            axs[i, 2].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
            axs[i, 2].tick_params(which='minor', size=0)
            axs[i, 2].grid(True, which='minor', color='#555555', linewidth=0.5)
            axs[i, 2].set_xticks([])
            axs[i, 2].set_yticks([])
            axs[i, 2].imshow(target_array, cmap=cmap, vmin=0, vmax=9)

        plt.tight_layout()

        tmpfile = BytesIO()
        plt.savefig(tmpfile, bbox_inches='tight', format='png', dpi=300)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        if count == 0:
            html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
        else:
            html += '<img src=\'data:image/png;base64,{}\'>'.format(encoded)

        fig, axs = plt.subplots(len(data['train']), 2, figsize=(5, len(data['train']) * 3 * 0.7))
        axs = axs.reshape(-1, 2) 
        for i, example in enumerate(data['train']):
            axs[i, 0].set_title(f'Training Input {i + 1}')
            rows, cols = np.array(example['input']).shape
            axs[i, 0].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
            axs[i, 0].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
            axs[i, 0].tick_params(which='minor', size=0)
            axs[i, 0].grid(True, which='minor', color='#555555', linewidth=0.5)
            axs[i, 0].set_xticks([])
            axs[i, 0].set_yticks([])
            axs[i, 0].imshow(np.array(example['input']), cmap=cmap, vmin=0, vmax=9)

            axs[i, 1].set_title(f'Training Output {i + 1}')
            rows, cols = np.array(example['output']).shape
            axs[i, 1].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
            axs[i, 1].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
            axs[i, 1].tick_params(which='minor', size=0)
            axs[i, 1].grid(True, which='minor', color='#555555', linewidth=0.5)
            axs[i, 1].set_xticks([])
            axs[i, 1].set_yticks([])
            axs[i, 1].imshow(np.array(example['output']), cmap=cmap, vmin=0, vmax=9)

        plt.tight_layout()

        tmpfile = BytesIO()
        plt.savefig(tmpfile, bbox_inches='tight', format='png', dpi=300)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        html += '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
        html += f'''<p> ====================== task id: {using_task_id} ======================</p>\n'''

    return html


def write_file(plot_html, prev_name="obj", save_dir='result'):
    ''' Writes the output to a html file for easy reference next time '''

    html_content = f'''
            <html>
            <body>
            {plot_html}'''
    html_content += '''
            </body>
            </html>
            '''

    save_name = f"{save_dir}/{prev_name}.html

    with open(save_name, 'w') as file:
        file.write(html_content)

target_dir = 'HF_Augmented_Data/'
target_files = os.listdir(target_dir)
kinds_of_problem = set()
prev_name = ''
html = ''
augmented_count = 0
total_count = 0
for i, target_file in enumerate(target_files):
    kind_of_problem = target_file.split('_')[0]
    if i != 0:
        if kind_of_problem not in kinds_of_problem:
            write_file(html, prev_name, save_dir=target_dir)
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

    with open(target_dir + target_file, 'r') as f:
        data = json.load(f)
    train_data = data['train']
    target_file_name = target_file.split('.json')[0]
    temp_html, temp_count = plot_2d_grid(train_data, target_file_name)
    html += temp_html
    augmented_count += temp_count

print(f'{prev_name}: {augmented_count}')
total_count += augmented_count
write_file(html, prev_name)
print(f'total count: {total_count}')