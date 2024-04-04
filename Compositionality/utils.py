# We modify from tanchongmin's code and use it to visualize
import json
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import base64
from io import BytesIO

# Convert string value to list
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

# Create the grid wit matplotlib
def plot_2d_grid(task_id, answer, csv_map, data_path, mode):
    for count, index in enumerate(task_id.keys()):
        if task_id[index] == '2.08E+20':
            task_id[index] == '20818e16'
            using_task_id = '20818e16'
        else:
            using_task_id = task_id[index] if len(task_id[index]) == 8 else ('').join(['0' for _ in range(8-len(task_id[index]))])+str(task_id[index])

        try:
            with open(data_path, 'r') as f:
                target_index = int(csv_map[csv_map['aft_task_id'].astype(str) == using_task_id]['pre_task_id'].values)
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

        fig, axs = plt.subplots(len(data[target_index]['test']), 3, figsize=(5, len(data[target_index]['test']) * 3 * 0.7))
        axs = axs.reshape(-1, 3)

        for i, example in enumerate(data[target_index]['test']):
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
        if type(answer['prediction'][index]) == float: 
            answer['prediction'][index] = '[]'
        
        target_array, flag = string_to_array(answer['prediction'][index].replace('], \n ', '], '))
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

        fig, axs = plt.subplots(len(data[target_index]['train']), 2, figsize=(5, len(data[target_index]['train']) * 3 * 0.7))
        axs = axs.reshape(-1, 2) 
        for i, example in enumerate(data[target_index]['train']):
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

# Make the visualization html file
def write_file(plot_html, trial, total_count, correct, method_name="obj", save_dir='result', save_name="test", mode='correct'):
    ''' Writes the output to a html file for easy reference next time '''

    if mode == 'correct':
        html_content = f'''
        <html>
        <body>
        {plot_html}'''
        html_content += f'''<p> Total Problem Count: {total_count}</p>\n'''
        html_content += f'''<p> Correct Count: {correct}</p>\n'''
        html_content += f'''<p> Accuracy: {correct/total_count}</p>\n'''
        html_content += '''
        </body>
        </html>
        '''
    else:
        html_content = f'''
                <html>
                <body>
                {plot_html}'''
        html_content += '''
                </body>
                </html>
                '''

    save_name = f"{save_dir}/{save_name}_correct.html" if mode == 'correct' else f"{save_dir}/{save_name}_incorrect.html"

    with open(save_name, 'w') as file:
        file.write(html_content)
