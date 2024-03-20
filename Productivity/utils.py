import os
import json
import openai
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import base64
from io import BytesIO

openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 

augmented_path = "./data/augmented"
prompt_path = "./data/prompt/Prompt.json"
result_path = './result/'

def read_data_from_json(file_path, task=None):
    try:
        with open(file_path, 'r') as json_file:
            if task is None:
                data = json.load(json_file)
            else:
                data = json.load(json_file)[task]
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None

# 이거 안쓰이고 있음 - 세진
def remove_input_by_order(data, order):
    del data['train'][order]
    return data


# 이거 안쓰이고 있음 - 세진
def collect_data(dataset):
    inputs = [example['input'] for example in dataset]
    outputs = [example['output'] for example in dataset]
    return inputs, outputs

    
def combine_data_from_directory(directory_path):
    combined_data = {
        "input": [],
        "output": [],
        "task": [],
        "prompt": [],
        "result": [],
        "test_input": [],
        "test_output": []
    }

    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".json"):
                json_file_path = os.path.join(root, filename)
                data = collect_data(read_data_from_json(json_file_path, "train"))
                test_data = collect_data(read_data_from_json(json_file_path, "test"))
                if data is not None:
                    combined_data["input"].append(data[0])
                    combined_data["output"].append(data[1])
                    combined_data["task"].append(os.path.basename(root))
                    combined_data["result"].append(data[0])
                    combined_data["test_input"].append(test_data[0])
                    combined_data["test_output"].append(test_data[1])

    return combined_data


# 이거 안쓰이고 있음 - 세진
def remove_except(input_str, exception_chars='0123456789[], '):
    inside_brackets = False
    result = []
    for char in input_str:
        if char == '[':
            inside_brackets = True
        elif char == ']':
            inside_brackets = False
        if inside_brackets or char in exception_chars:
            result.append(char)
    return ''.join(result)


def extract_2d_arrays(input_str):
    cleaned_str = remove_except(input_str)

    extracted_arrays = []
    bracket_count = 0
    start_index = None
    end_index = None

    for i, char in enumerate(cleaned_str):
        if char == '[':
            bracket_count += 1
            if bracket_count == 1:
                start_index = i
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_index = i
                potential_array = cleaned_str[start_index:end_index+1]
                try:
                    current_array = eval(potential_array)
                    if isinstance(current_array, list) and all(isinstance(sublist, list) for sublist in current_array):
                        extracted_arrays.append(current_array)
                except:
                    pass

    return extracted_arrays


def generate_text(prompt):
    # 채팅 메시지 설정
    instructions = [{"role": "system", "content": "You are an ARC(Abstraction and Reasoning Corpus) solver."}]

    try:
        response = openai.ChatCompletion.create(
            engine = openai.deployment_name,
            messages = instructions + [{"role": "user", "content": prompt}],
            temperature = 1.0,
            max_tokens = 4096,
            top_p = 0.95,
            frequency_penalty = 0,
            presence_penalty = 0,
            stop = None
        )
        return response.choices[0].message['content'].strip() if response.choices else "No response."
    
    except openai.error.InvalidRequestError as e:
        # 콘텐츠 관리 정책에 걸려서 응답이 없는 경우 처리
        print(f"Error generating text: {e}")
        return "No response due to content management policy."
    
# 이거 안쓰이고 있음 - 세진
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