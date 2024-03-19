import os
import openai
import jsonlines
import json
import pandas as pd
from dotenv import load_dotenv
from collections import OrderedDict
import time
from tqdm import tqdm
import re
openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_base = "" 
openai.api_key = "" 

if openai.api_key == "":
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

if openai.api_base == "":
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 

fail_task_ids = ['47996f11']
cot_task_ids = ['3ed85e70', '0f63c0b9', '17cae0c1', '47996f11', '4acc7107', '0692e18c', '477d2879', '1c0d0a4b', '292dd178', '1990f7a8', '22a4bbc2', '4364c1c4', '2f0c5170', '17b80ad2', '03560426', '0c786b71', '3391f8c0', '42a15761', '0bb8deee', '1e97544e', '1c02dbbe', '4b6b68e5', '2a5f8217', '3194b014', '1acc24af', '0c9aba6e', '0e671a1a', '37d3e8b2', '0becf7df', '0607ce86', '3a301edc', '2546ccf6', '009d5c81', '31adaf00', '281123b4', '3d31c5b3', '423a55dc', '1d0a4b61', '1a2e2828', '319f2597', '3979b1a8', '12422b43', '140c817e', '0a2355a6', '19bb5feb', '332efdb3', '27a77e38', '2c0b0aff', '00dbd492', '2c737e39', '2072aba6', '48f8583b', '27f8ce4f', '14754a24', '32e9702f', '195ba7dc', '137f0df0', '184a9768', '29700607', '1c56ad9f', '15663ba9', '4c177718', '136b0064', '0a1d4ef5', '1d398264', '09c534e7', '2685904e', '48131b3c', '31d5ba1a', '2697da3f', '103eff5b', '12997ef3', '1e81d6f9', '25094a63', '08573cc6', '20981f0e', '4852f2fa', '2b01abd0', '2072aba6', '1a6449f1', '34b99a2b', '0b17323b', '15696249', '414297c0', '2753e76c', '12eac192', '0934a4d8', '310f3251', '358ba94e', '21f83797', '4aab4007', '351d6448', '45bbe264', '456873bc', '15113be4', '3490cc26', '3b4c2228', '00576224', '42918530', '45737921', '20818e16']
miss_task_ids = ['48f8583b', '42918530', '42a15761', '4c177718', '45737921', '576224', '4acc7107', '4852f2fa', '4aab4007', '477d2879', '4b6b68e5', '45bbe264', '3560426', '47996f11', '48131b3c', '456873bc', '4364c1c4']


file_name = 'data/l2m/Decompose_evaluation_dataset_CoT.jsonl'
L2M_file_name = 'L2M_evaluation_dataset_CoT.jsonl'

count = 0

for index_number in range(0,5):
    save_path = f'result/[L2M]result_{index_number}'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_file_name = f"Decompose_CoT_predict"
    error_log_path = f'{save_path}/{save_file_name}_error_count_log_{index_number}.txt'
    error_log_count_list = []

    load_dotenv()

    prompt_sentence = []
    label_sentence = []
    data = []
    count = 0
    error_log_list = []

    with jsonlines.open(file_name) as read_file:
        for line in read_file.iter():
            data.append(line)
    task_ids = [x['task_id'] for x in data]
    prompt_sentence = [x['subquestion_prompt'] for x in data]
    label_sentence = [x['completion'] for x in data]
    example_prompt = [x['solve_prompt'] for x in data]
    quiz_prompt = [x['quiz_prompt'] for x in data]

    using_task_ids = []
    using_prompt_sentence = []
    using_label_sentence = []
    using_example_prompt_sentence = []
    using_quiz_prompt_sentence = []
    answer_list = []
    prediction_list = []
    except_count = 0
    using_count = 0
    all_tokens = 0
    error_list = []
    total_count = 0

    for task_id, prompt, label, example, quiz in tqdm(zip(task_ids, prompt_sentence, label_sentence, example_prompt, quiz_prompt)):
        if task_id not in fail_task_ids:
            continue
        print(f'task_id: {task_id}')
        label_len = len(label)
        max_tokens = label_len
        count += 1
        total_count += 1
        prompt += quiz
        
        try:
            response = openai.ChatCompletion.create(
                engine="Write your deployed engine name here",
                messages=[
                     {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=2500,
                # max_tokens=4096, 
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
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
            time.sleep(15)
            continue

        answer_list.append(response['choices'][0]['message']['content'])
        pattern = r"Q[1-9].*"
        match = re.search(pattern, response['choices'][0]['message']['content'])
        p = re.compile(pattern)
        if match:
            extracted_array = match.group()
        else:
            extracted_array = None

        temp_list = []
        for i in range(len(p.findall(response['choices'][0]['message']['content']))):
            temp_str = p.findall(response['choices'][0]['message']['content'])[i].split('.')[0] + '.'
            temp_list.append(temp_str)

        prediction_list.append('\n\n'.join(temp_list))

        using_prompt_sentence.append(prompt)
        using_label_sentence.append(label)
        using_example_prompt_sentence.append(example)
        using_quiz_prompt_sentence.append(quiz)
        using_count += 1
        using_task_ids.append(task_id)
        time.sleep(15)
        print(f'진행정도: {total_count}')
        print(f'task_id: {task_id}')


    with open(f"{save_path}/{L2M_file_name}_{index_number}_3", "w") as f:
        for task_id, prompt, completion, example, quiz, prediction in zip(using_task_ids ,using_prompt_sentence, using_label_sentence, using_example_prompt_sentence, using_quiz_prompt_sentence, prediction_list):
            data_jsonl = OrderedDict()
            data_jsonl['task_id'] = task_id
            data_jsonl['prompt'] = prompt
            data_jsonl['completion'] = completion
            data_jsonl['subquestion'] = prediction
            data_jsonl['example_prompt'] = example
            data_jsonl['quiz_prompt'] = quiz
            f.write(json.dumps(data_jsonl, ensure_ascii=False)+'\n')

    print(f'except_count: {except_count}')
    print(f'사용할 수 있는 데이터 개수: {using_count}')

    with open(f'{save_path}/{save_file_name}_error_count_log_{index_number}_3.txt', 'w') as f:
        f.write(f'{error_list}')

    with open(f'{save_path}/{save_file_name}_error_log_{index_number}_3.txt', 'w') as f:
        f.write(f'{error_log_list}')



