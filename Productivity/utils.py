import os
import json
import openai

openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 

augmented_path = "./data/augmented"
prompt_path = "./data/prompt/Prompt.json"

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