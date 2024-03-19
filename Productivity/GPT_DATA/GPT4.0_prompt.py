#Note: The openai-python library support for Azure OpenAI is in preview.
import openai
import json

openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_base = "" 
openai.api_key = "" 

if openai.api_key == "":
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

if openai.api_base == "":
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 

# 채팅 메시지 설정
instructions = [{"role": "system", "content": "You are an ARC(Abstraction and Reasoning Corpus) solver."}]

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

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None

def generate_text(prompt):
    try:
        response = openai.ChatCompletion.create(
            engine = "Aug-GPT4",
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

json_file_path = "C:/Users/metaverse/Desktop/Research1007/GPT_DATA/Prompt.json"
data = read_json_file(json_file_path)

total_tasks = len(data['task'])  # 전체 작업 수

for i in range(total_tasks):
    arc_data = {
        "train": [],
        "test": []
    }

    for j in range(len(data['prompt'][i])):
        aug_data = {
            "input": [],
            "output": [],
            "test_input": [],
            "test_output": [],
        }
        prompt = data['prompt'][i][j]
        text = extract_2d_arrays(generate_text(prompt))
        aug_data['input'].append(data['input'][i][j])
        aug_data['output'].append(data['output'][i][j])
        for k in range(len(text)):
            aug_data['input'].append(text[k])
            aug_data['output'].append(extract_2d_arrays(prompt)[-1])

        for k in range(len(aug_data['input'])):
            train_data = {
                "input": aug_data['input'][k],
                "output": aug_data['output'][k]
            }
            arc_data['train'].append(train_data)

    for j in range(len(data['test_input'][i])):
        aug_data = {
            "input": [],
            "output": [],
            "test_input": [],
            "test_output": [],
        }
        aug_data['test_input'].append(data['test_input'][i][j])
        aug_data['test_output'].append(data['test_output'][i][j])
        for k in range(len(aug_data['test_input'])):
            test_data = {
                "input": aug_data['test_input'][k],
                "output": aug_data['test_output'][k]
            }
            arc_data['test'].append(test_data)

    output_file_path = f"C:/Users/metaverse/Desktop/Research1007/Augmented_Data/{data['task'][i]}_{i}_Aug.json"
    with open(output_file_path, "w") as json_file:
        json.dump(arc_data, json_file)

    print(f"Progress: {100 * (i + 1) / total_tasks:.2f}%")