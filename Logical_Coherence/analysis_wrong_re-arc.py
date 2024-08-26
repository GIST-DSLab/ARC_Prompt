import pandas as pd
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

base_dir = 'result/[CoT-re-arc_correct]result_'
total_task_id = set()

re_arc_dir = 'data/re_arc/tasks'


def load_json_data(folder):
    json_files = [pos_json for pos_json in os.listdir(folder) if pos_json.endswith('.json')]
    data = {}
    for js in json_files:
        with open(os.path.join(folder, js)) as json_file:
            data[js] = json.load(json_file)
    return data


def array_to_string(grid):
    # if grid is already in string form, just return it
    if isinstance(grid[0][0], str): return grid

    mapping = {0: '.', 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i'}
    newgrid = [[mapping[grid[i][j]] for j in range(len(grid[0]))] for i in range(len(grid))]
    return newgrid


def string_to_array(grid):
    # if grid is already in integer form, just return it
    if isinstance(grid[0][0], int): return grid

    mapping = {0: '.', 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i'}
    revmap = {v: k for k, v in mapping.items()}
    newgrid = [[revmap[grid[i][j]] for j in range(len(grid[0]))] for i in range(len(grid))]
    return newgrid


def load_task_mapping(csv_file):
    df = pd.read_csv(csv_file)
    task_mapping = pd.Series(df.task_name.values, index=df.task_id).to_dict()
    return task_mapping


def plot_2d_grid(data, file_name, task_id, output_base_folder='evaluation_IO_each_without_label_3'):
    cvals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    colors = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00", "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF",
              "#870C25"]  # [Black, Blue, Red, Green, Yellow, Gray, Pink, Orange, Light blue, Brown]
    norm = plt.Normalize(min(cvals), max(cvals))
    tuples = list(zip(map(norm, cvals), colors))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

    output_folder = 'training_IO_each_without_label'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, example in enumerate(data):
        if i == 100:
            break
        fig, axs = plt.subplots(1, 2, figsize=(5, 3 * 0.7))

        # Input Image
        axs[0].set_title(f'Input {i + 1}')
        # display gridlines
        rows, cols = np.array(string_to_array(example['input'])).shape
        axs[0].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
        axs[0].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
        axs[0].tick_params(which='minor', size=0)
        axs[0].grid(True, which='minor', color='#555555', linewidth=1)
        axs[0].set_xticks([]);
        axs[0].set_yticks([])
        axs[0].imshow(np.array(string_to_array(example['input'])), cmap=cmap, vmin=0, vmax=9)

        # Output image
        axs[1].set_title(f'Output {i + 1}')
        # display gridlines
        rows, cols = np.array(string_to_array(example['output'])).shape
        axs[1].set_xticks(np.arange(cols + 1) - 0.5, minor=True)
        axs[1].set_yticks(np.arange(rows + 1) - 0.5, minor=True)
        axs[1].tick_params(which='minor', size=0)
        axs[1].grid(True, which='minor', color='#555555', linewidth=1)
        axs[1].set_xticks([]);
        axs[1].set_yticks([])
        axs[1].imshow(np.array(string_to_array(example['output'])), cmap=cmap, vmin=0, vmax=9)

        # Find the corresponding task_id for the task_name
        # task_id = task_mapping.get(file_name, file_name)
        output_folder = os.path.join(output_base_folder, str(task_id))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        case_file_name = f"{file_name}_case{i + 1}.png"
        output_file_path = os.path.join(output_folder, case_file_name)

        plt.tight_layout()
        plt.savefig(output_file_path, format='png', dpi=300)
        plt.close()


for i in range(5):
    cot_file_name = f'[iter_{i}]accuracy_each_task'
    cot_dir_path = base_dir + f'{i}/'

    cot_result = pd.read_csv(cot_dir_path + cot_file_name+'.csv', converters={"code": lambda x: str(x)})

    all_wrong_task_id = cot_result[cot_result['correct_flag'] == 0]['task_id'].tolist()

    total_task_id.update(all_wrong_task_id)


save = 'result/all_wrong_re_arc/'

if not os.path.exists(save):
    os.makedirs(save)

for file_name in total_task_id:
    with open(f'{re_arc_dir}/{file_name}.json', 'r') as f:
        target_data = json.load(f)
    target_task_id = file_name.split('.')[0]
    task_id = target_task_id
    file_name_str = file_name.split('.')[0]
    plot_2d_grid(target_data, file_name_str, target_task_id, output_base_folder=save)


