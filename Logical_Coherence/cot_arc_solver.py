import os

import numpy as np
import openai
import jsonlines
import pandas as pd
from dotenv import load_dotenv
import time
from tqdm import tqdm
import re
import ast
import json
import backoff

# Set variable realted the azure openai.  
openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# This ids used in the experiment. It is a subset of the ids in the original dataset.
MODE = 're-arc_correct'

if MODE == 'eval':
    cot_task_ids = ['3ed85e70', '0f63c0b9', '17cae0c1', '47996f11', '4acc7107', '0692e18c', '477d2879', '1c0d0a4b', '292dd178', '1990f7a8', '22a4bbc2', '4364c1c4', '2f0c5170', '17b80ad2', '03560426', '0c786b71', '3391f8c0', '42a15761', '0bb8deee', '1e97544e', '1c02dbbe', '4b6b68e5', '2a5f8217', '3194b014', '1acc24af', '0c9aba6e', '0e671a1a', '37d3e8b2', '0becf7df', '0607ce86', '3a301edc', '2546ccf6', '009d5c81', '31adaf00', '281123b4', '3d31c5b3', '423a55dc', '1d0a4b61', '1a2e2828', '319f2597', '3979b1a8', '12422b43', '140c817e', '0a2355a6', '19bb5feb', '332efdb3', '27a77e38', '2c0b0aff', '00dbd492', '2c737e39', '48f8583b', '27f8ce4f', '14754a24', '32e9702f', '195ba7dc', '137f0df0', '184a9768', '29700607', '1c56ad9f', '15663ba9', '4c177718', '136b0064', '0a1d4ef5', '1d398264', '09c534e7', '2685904e', '48131b3c', '31d5ba1a', '2697da3f', '103eff5b', '12997ef3', '1e81d6f9', '25094a63', '08573cc6', '20981f0e', '4852f2fa', '2b01abd0', '2072aba6', '1a6449f1', '34b99a2b', '0b17323b', '15696249', '414297c0', '2753e76c', '12eac192', '0934a4d8', '310f3251', '358ba94e', '21f83797', '4aab4007', '351d6448', '45bbe264', '456873bc', '15113be4', '3490cc26', '3b4c2228', '00576224', '42918530', '45737921', '20818e16']

data_path = f'./data/cot/'

assistant_format_prompt = '''
You must respond in the following JSON format when answering! Make sure to follow this!

{
    'grid': (Include the test output grid, which you have derived based on the given example pair and test input (quiz), in the form of a 2D array),
    'description': (Explain in a string why the test output grid is structured in that way, i.e., how you solved the problem),
}

You must strictly adhere to these guidelines to create the response in JSON format! I repeat, you must strictly follow these guidelines!

Make sure to generate the complete JSON format without stopping midway. You must generate the tokens all the way to the end! Make sure to finish the entire generation!
'''

@backoff.on_exception(backoff.expo, openai.error.OpenAIError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

for index_number in range(4,5):
    if MODE == 'eval':
        save_base_dir = f"./result/[CoT]result_{index_number}"
        data_file_name = f"{data_path}evaluation_dataset.jsonl"
    elif MODE == 'train':
        save_base_dir = f"./result/[CoT-train]result_{index_number}"
        data_file_name = f"{data_path}training_dataset.jsonl"
    elif MODE == 're-arc_correct':
        save_base_dir = f"./result/[CoT-re-arc_correct]result_{index_number}"
        data_file_name = f"{data_path}re-arc_correct_dataset.jsonl"
    elif MODE == 're-arc_incorrect':
        save_base_dir = f"./result/[CoT-re-arc_incorrect]result_{index_number}"
        data_file_name = f"{data_path}re-arc_incorrect_dataset.jsonl"
    else:
        raise ValueError("Invalid mode")

    if os.path.exists(f"{save_base_dir}") == False:
        os.makedirs(f"{save_base_dir}")

    save_file_name = f"{save_base_dir}/cot_predict{index_number}"
    load_dotenv()

    prompt_sentence = []
    label_sentence = []
    data = []
    count = 0
    error_log_list = []

    with jsonlines.open(f'{data_file_name}') as read_file:
        for line in read_file.iter():
            data.append(line)
    task_ids = [x['task_id'] for x in data]
    prompt_sentence = [x['prompt'] for x in data]
    label_sentence = [x['completion'] for x in data]

    try_count_list = []
    using_task_ids = []
    using_prompt_sentence = []
    using_label_sentence = []
    answer_list = []
    prediction_list = []
    description_list = []
    correct_list = []
    except_count = 0
    using_count = 0
    all_tokens = 0
    error_list = []
    retry_flag = False
    try_count = 0
    pre_task_id = None

    if os.path.exists(f'{save_file_name}.csv'):
        prev_df = pd.read_csv(f'{save_file_name}.csv', converters={"task_id": lambda x: str(x)})

        retry_flag = True


    for task_id, prompt, label in tqdm(zip(task_ids, prompt_sentence, label_sentence)):
        # if task_id not in cot_task_ids:
        #     continue
        if pre_task_id == None:
            pre_task_id = task_id
        elif pre_task_id != task_id:
            pre_task_id = task_id
            try_count = 0

        try_count += 1
        label_len = len(label)
        max_tokens = label_len
        error_flag = False

        if retry_flag:
            if len(prev_df[(prev_df['task_id']==task_id) & (prev_df['try'] == try_count)]) == 1:
                using_count += 1
                print(f'Progress: {using_count} / {len(task_ids)}')
                continue

        messages = [
                         {"role": "user", "content": prompt},
                         {"role": "assistant", "content": assistant_format_prompt}
        ]

        try:
            fail_count = 0
            # Call the OpenAI API
            while True:
                if fail_count >= 3:
                    break

                response = completions_with_backoff(
                    engine = openai.deployment_name,
                    messages = messages,
                    temperature = 0,
                    max_tokens = 4096,
                    frequency_penalty = 0.0,
                    presence_penalty = 0.0,
                )

                if response['choices'][0]['finish_reason'] == 'length':
                    messages[0]['content'] = prompt + "\n\nYOUR RESPONSE IS like this\n\n" + response['choices'][0]['message']['content'] + "\n\n!!!Continue generate the response to complete the grid and description in JSON format.!!!"
                else:
                    pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)
                    matches = pattern.findall(response['choices'][0]['message']['content'])
                    temp_parsed_log = None
                    temp_parsed_dict = None
                    for match in matches:
                        match = match.replace("grid:", "grid")
                        match = match.replace("description:", "description")
                        try:
                            temp_parsed_log = json.loads(match)
                        except json.JSONDecodeError as e:
                            try:
                                temp_parsed_log = json.loads(match.replace("'", '"'))
                            except json.JSONDecodeError as e:
                                try:
                                    temp_parsed_log = json.loads(match.replace('"', "'"))
                                except json.JSONDecodeError as e:
                                    try:
                                        temp_parsed_dict = ast.literal_eval(match)
                                        temp_parsed_log = json.dumps(temp_parsed_dict)
                                    except Exception as e:
                                        continue
                    if temp_parsed_log == None:
                        fail_count += 1
                        messages[0]['content'] = prompt + f"\n\nYOUR RESPONSE IS like this\n\n" + response['choices'][0]['message']['content'] + "\n\n!!!Continue generate the response to make the grid and description in JSON format.!!!"
                        print(f"===================== [Fail {fail_count}] =====================")
                        print(f"task id: {task_id}")
                        print(f"try: {try_count}")
                        print(f"response: {response['choices'][0]['message']['content']}")
                    else:
                        break
        except Exception as e:
            print(e)
            error_str = f"error message: {e}\n" + \
                        f"error: {count}\n" + \
                        f"task id: {task_id}\n" + \
                        f'prompt: {prompt}\n' + \
                        f'prompt len: {len(prompt)}\n'
            print(error_str)
            error_log_list.append(error_str)
            error_list.append(count)
            except_count += 1

            df_error = pd.DataFrame({
                "task_id": [task_id],
                "try": [try_count],
            })

            if os.path.exists(f'{save_file_name}_error_info.csv'):
                df_error.to_csv(f'{save_file_name}_error_info.csv', mode='a', header=False, index=None)
            else:
                df_error.to_csv(f'{save_file_name}_error_info.csv', index=None)
            continue
        
        # Extract the response from the API
        total_parsed_log = []
        parsed_log = None
        pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)
        matches = pattern.findall(response['choices'][0]['message']['content'])
        for match in matches:
            match = match.replace("grid:", "grid")
            match = match.replace("description:", "description")

            try:
                parsed_log = json.loads(match)
            except json.JSONDecodeError as e:
                try:
                    parsed_log = json.loads(match.replace("'", '"'))
                except json.JSONDecodeError as e:
                    try:
                        parsed_log = json.loads(match.replace('"', "'"))
                    except json.JSONDecodeError as e:
                        try:
                            parsed_dict = ast.literal_eval(match)
                            parsed_log = json.dumps(parsed_dict)
                        except Exception as e:
                            print(e)
                            print(f"error: {count}")
                            print(f"task id: {task_id}")
                            print(f'prompt: {prompt}')
                            print(f'prompt len: {len(prompt)}')
                            error_log_list.append(f"error: {count}")
                            error_list.append(count)
                            except_count += 1

                            df_error = pd.DataFrame({
                                "task_id": [task_id],
                                "try": [try_count],
                            })

                            error_flag = True

                            if os.path.exists(f'{save_file_name}_error_info.csv'):
                                df_error.to_csv(f'{save_file_name}_error_info.csv', mode='a', header=False, index=None)
                            else:
                                df_error.to_csv(f'{save_file_name}_error_info.csv', index=None)
                            continue

        using_count += 1
        print(f'Progress: {using_count} / {len(task_ids)}')

        if parsed_log == None:
            df_error = pd.DataFrame({
                "task_id": [task_id],
                "try": [try_count],
            })

            error_flag = True

            if os.path.exists(f'{save_file_name}_error_info.csv'):
                df_error.to_csv(f'{save_file_name}_error_info.csv', mode='a', header=False, index=None)
            else:
                df_error.to_csv(f'{save_file_name}_error_info.csv', index=None)

        if error_flag:
            continue

        count += 1
        answer = response['choices'][0]['message']['content']
        prediction = str(parsed_log['grid'])
        description = str(parsed_log['description'])
        using_prompt= prompt
        using_label = label
        using_task= str(task_id)

        if np.array_equal(parsed_log['grid'], ast.literal_eval(label)):
            print(f"Correct: {count}")
            correct = True
        else:
            correct = False

        # Save the results to a CSV file
        if MODE == 'eval' or MODE == 'train':
            df = pd.DataFrame({
                "task_id": [using_task],
                "prompt":[using_prompt],
                "answer": [answer],
                "description": [description],
                "prediction": [prediction],
                "label": [using_label],
                "correct_flag": [correct],
            })
        else:
            df = pd.DataFrame({
                "task_id": [using_task],
                "try": [try_count],
                "prompt": [using_prompt],
                "answer": [answer],
                "description": [description],
                "prediction": [prediction],
                "label": [using_label],
                "correct_flag": [correct],
            })

        if os.path.exists(f'{save_file_name}.csv'):
            df.to_csv(f'{save_file_name}.csv', mode='a', header=False, index=None)
        else:
            df.to_csv(f'{save_file_name}.csv', index=None)


    def refine_prediction(prediction):
        if prediction:
            return str(prediction).replace('  ', ' ')
        else:
            return prediction

    print(f'Check the number of tasks: {using_count}')
