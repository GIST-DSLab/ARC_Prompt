import os
import json
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import base64
from io import BytesIO
from utils import augmented_path, result_path
import warnings
warnings.filterwarnings('ignore')


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


def plot_2d_grid(dataset_dict, file_name):
    count = 0
    html = f'''<h2> ========================= file name: {file_name} =========================</h2>\n'''
    for i in range(len(dataset_dict)):
        input_ = dataset_dict[i]['input']
        output_ = dataset_dict[i]['output']
        cvals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        colors = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00", "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25",
                  "#000000"]
        norm = plt.Normalize(min(cvals), max(cvals))
        tuples = list(zip(map(norm, cvals), colors))
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

        # fig, axs = plt.subplots(len(data['test']), 3, figsize=(5, len(data['test']) * 3 * 0.7))
        fig, axs = plt.subplots(1, 2, figsize=(5, 1 * 3 * 0.7))
        axs = axs.reshape(-1, 2)  # Reshape axs to have 2 dimensions

        # show grid

        axs[0, 0].set_title(f'Input {i + 1}')
        # display gridlines
        rows, cols = np.array(input_).shape
        axs[0, 0].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
        axs[0, 0].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
        axs[0, 0].grid(True, which='minor', color='#555555', linewidth=0.5)
        axs[0, 0].set_xticks([]);
        axs[0, 0].set_yticks([])
        axs[0, 0].imshow(np.array(input_), cmap=cmap, vmin=0, vmax=9)

        axs[0, 1].set_title(f'Output {i + 1}')
        # display gridlines
        rows, cols = np.array(output_).shape
        axs[0, 1].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
        axs[0, 1].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
        axs[0, 1].grid(True, which='minor', color='#555555', linewidth=0.5)
        axs[0, 1].set_xticks([]);
        axs[0, 1].set_yticks([])
        axs[0, 1].imshow(np.array(output_), cmap=cmap, vmin=0, vmax=9)
        # plot gpt output if present

        plt.tight_layout()

        tmpfile = BytesIO()
        plt.savefig(tmpfile, format='png', dpi=300)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

        html += '<img src=\'data:image/png;base64,{}\'>'.format(encoded)

        # if mode == 'incorrect' and count == 20:
        #     break
        # plt.show()

        # returns back in html format
        count += 1
    
    return html, count


def write_file(plot_html, name, dir_path='result'):
    ''' Writes the output to a html file for easy reference next time '''
    # Create the HTML content
    html_content = f'''
            <html>
            <body>
            {plot_html}'''
    html_content += '''
            </body>
            </html>
            '''

    save_name = f"{dir_path}/{name}.html"
    # Overwrite if first run
    with open(save_name, 'w') as file:
        file.write(html_content)


target_files = os.listdir(augmented_path)
kinds_of_problem = set()
prev_name = ''
html = ''
augmented_count = 0
total_count = 0
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