#Note: The openai-python library support for Azure OpenAI is in preview.
import json
from utils import read_json_file, extract_2d_arrays, generate_text, augmented_path, prompt_path

data = read_json_file(prompt_path)
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

    augmented_data_path = f"{augmented_path}/{data['task'][i]}_{i}_Aug.json"
    with open(augmented_data_path, "w") as json_file:
        json.dump(arc_data, json_file)

    print(f"Progress: {100 * (i + 1) / total_tasks:.2f}%")