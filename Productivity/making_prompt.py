import os
import json

def collect_data(dataset):
    inputs = [example['input'] for example in dataset]
    outputs = [example['output'] for example in dataset]
    return inputs, outputs

def read_data_from_json(json_file_path, task):
    try:
        # JSON 파일을 열고 읽기 모드로 엽니다.
        with open(json_file_path, "r") as json_file:
            # JSON 데이터를 읽습니다.
            data = json.load(json_file)

            train_data = data[task]

            return train_data
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return None
    except KeyError:
        print(f"Key 'train' not found in the JSON data.")
        return None
    
def combine_data_from_directory(directory_path,):
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

top_folder_path = "./HF_Augmented_Data"

combined_data = combine_data_from_directory(top_folder_path)

prompt_data = []

for i in range(len(combined_data["input"])):
    cor_prompt = []
    for j in range(len(combined_data['input'][i])):
        prompt = 'Try solving the ARC problem and do not say sensitive word. : generate the output accordingly. I will give you Hint, '
        if combined_data['task'][i] == 'AboveBelow':
          prompt += "Focus on the horizontal criteria, you may have to modify some regein by that line. such as removing, moving, filling region by color. element. See the provided example to how to modify"
        elif combined_data['task'][i] == 'Center':
          prompt += "Fix the array issue by addressing the center, potentially moving or removing the central element. See the provided example for clarity."
        elif combined_data['task'][i] == 'CleanUp':
          prompt += "Distort the shapes in areas where they are polygonal or completely filled, adding noise or disturbances to disrupt the complete shapes."
        elif combined_data['task'][i] == 'CompleteShape':
          prompt += "Distort the perfectly shaped objects identified in the input image. Introduce noise to these identified objects to easily generate diverse outputs."
        elif combined_data['task'][i] == 'Copy':
          prompt += "Delete one identical object from the output. Refer to the example to identify which one to remove. Consider deleting the object located in a position-indicating space."
        elif combined_data['task'][i] == 'Count':
          prompt += "Create an input image based on the provided count-related problem. Focus on details like object or color count, as shown in the example."     
        elif combined_data['task'][i] == 'ExtendToBoundary':
          prompt += "In the input image, find lines connected to boundaries with different colors. Transform these lines into a different shape. The example illustrates how to make this transformation."
        elif combined_data['task'][i] == 'ExtractObjects':
          prompt += "Generate an output image with objects from the given input. Refer to examples for guidance. Hint: Extract objects when inferring input from output."
        elif combined_data['task'][i] == 'FilledNotFilled':
          prompt += "When inferring the input from the output, focus on situations where the inner part of an object contains empty space or another object. Examples provide guidance for creating the output image."
        elif combined_data['task'][i] == 'HorizontalVertical':
          prompt += "Focus on horizontal and vertical relations, representing them with colors or preserving one direction while eliminating the other. Examples illustrate the approach."
        elif combined_data['task'][i] == 'InsideOutside':
          prompt += "Address the inside-outside relationship, either by selecting items inside or outside in the input or determining quantities. Use the boundary as a reference. Examples offer guidance."
        elif combined_data['task'][i] == 'MoveToBoundary':
          prompt += "Objects in the input may be shifted to one side, and in the output, they are displaced either horizontally or vertically. Infer the direction from examples and choose the displacement freely."
        elif combined_data['task'][i] == 'Order':
          prompt += "This is about randomly rearranging initially ordered objects while representing their original positions through a specific rule. Examine the examples to understand how to achieve this."
        elif combined_data['task'][i] == 'SameDifferent':
          prompt += "You'll notice that only specific-shaped objects are extracted in the input image. Create additional objects in the zero-represented space. Examples provide guidance on how to proceed."
        elif combined_data['task'][i] == 'TopBottom2D':
          prompt += "Objects are in a 2D space. Check changes in the top and bottom. The input may have shifted or require removing top/bottom indicators. Look at examples for specifics."
        elif combined_data['task'][i] == 'TopBottom3D':
          prompt += "Objects are in 3D space. Consider front-back relationships; bring objects forward or move them backward in the input. Look at examples for specific methods."
        temp = -1
        prompt += f"Here are some examples to help you."
        for k in range(len(combined_data['input'][i])):
            if j == k:
                temp = k
            if j != k:
                prompt += f"Input: {combined_data['output'][i][k]}, output: {combined_data['input'][i][k]}"
        prompt += f" Input: {combined_data['output'][i][temp]}, Provide two output arrays that are not identical to the input array or a direct copy of the example output. Ensure that each element in the arrays is an integer between 0 and 9. Would you give me 3 output array? No need to explain how you solved."
        cor_prompt.append(prompt)
    prompt_data.append(cor_prompt)

combined_data['prompt'] = prompt_data
print(len(prompt_data))
print(len(combined_data['input']))
print(len(combined_data['output']))
print(len(combined_data['test_input']))
print(len(combined_data['test_input']))


output_directory = "./GPT_Data/Prompt.json"

with open(output_directory, "w") as json_file:
    json.dump(combined_data, json_file)