import os
import openai
import jsonlines
import pandas as pd
from dotenv import load_dotenv
import time
from tqdm import tqdm
import re
openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 

cot_task_ids = ['3ed85e70', '0f63c0b9', '17cae0c1', '47996f11', '4acc7107', '0692e18c', '477d2879', '1c0d0a4b', '292dd178', '1990f7a8', '22a4bbc2', '4364c1c4', '2f0c5170', '17b80ad2', '03560426', '0c786b71', '3391f8c0', '42a15761', '0bb8deee', '1e97544e', '1c02dbbe', '4b6b68e5', '2a5f8217', '3194b014', '1acc24af', '0c9aba6e', '0e671a1a', '37d3e8b2', '0becf7df', '0607ce86', '3a301edc', '2546ccf6', '009d5c81', '31adaf00', '281123b4', '3d31c5b3', '423a55dc', '1d0a4b61', '1a2e2828', '319f2597', '3979b1a8', '12422b43', '140c817e', '0a2355a6', '19bb5feb', '332efdb3', '27a77e38', '2c0b0aff', '00dbd492', '2c737e39', '48f8583b', '27f8ce4f', '14754a24', '32e9702f', '195ba7dc', '137f0df0', '184a9768', '29700607', '1c56ad9f', '15663ba9', '4c177718', '136b0064', '0a1d4ef5', '1d398264', '09c534e7', '2685904e', '48131b3c', '31d5ba1a', '2697da3f', '103eff5b', '12997ef3', '1e81d6f9', '25094a63', '08573cc6', '20981f0e', '4852f2fa', '2b01abd0', '2072aba6', '1a6449f1', '34b99a2b', '0b17323b', '15696249', '414297c0', '2753e76c', '12eac192', '0934a4d8', '310f3251', '358ba94e', '21f83797', '4aab4007', '351d6448', '45bbe264', '456873bc', '15113be4', '3490cc26', '3b4c2228', '00576224', '42918530', '45737921', '20818e16']

data_path = f'./data/cot/'
for index_number in range(0,5):
    save_file_name = f"./result/[CoT]result_{index_number}/cot_predict{index_number}"

    load_dotenv()

    prompt_sentence = []
    label_sentence = []
    data = []
    count = 0
    error_log_list = []

    with jsonlines.open(f'{data_path}evaluation_dataset.jsonl') as read_file:
        for line in read_file.iter():
            data.append(line)
    task_ids = [x['task_id'] for x in data]
    prompt_sentence = [x['prompt'] for x in data]
    label_sentence = [x['completion'] for x in data]

    using_task_ids = []
    using_prompt_sentence = []
    using_label_sentence = []
    answer_list = []
    prediction_list = []
    except_count = 0
    using_count = 0
    all_tokens = 0
    error_list = []

    for task_id, prompt, label in tqdm(zip(task_ids, prompt_sentence, label_sentence)):
        if task_id not in cot_task_ids:
            continue
        
        label_len = len(label)
        max_tokens = label_len
        count += 1

        try:
            response = openai.ChatCompletion.create(
                engine = openai.deployment_name, 
                messages = [
                     {"role": "user", "content": prompt},
                ],
                temperature = 0,
                max_tokens = 4096, 
                frequency_penalty = 0.0,
                presence_penalty = 0.0,
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
            continue

        answer_list.append(response['choices'][0]['message']['content'])
        pattern = r"\[\[(((.|\n)*))\]\]"
        match = re.search(pattern, response['choices'][0]['message']['content'])
        if match:
            extracted_array = match.group()
        else:
            extracted_array = None

        prediction_list.append(extracted_array)
        using_prompt_sentence.append(prompt)
        using_label_sentence.append(label)
        using_count += 1
        using_task_ids.append(task_id)
        time.sleep(15)
        print(f'Progress: {using_count} / {len(cot_task_ids)}')
        if using_count == len(cot_task_ids):
            break

    df = pd.DataFrame({
        "task_id": using_task_ids,
        "prompt":using_prompt_sentence,
        "answer": answer_list,
        "prediction": prediction_list,
        "label": using_label_sentence,
    })
    df.to_csv(f'{save_file_name}.csv', index=None)

    a = pd.read_csv('prediction.csv')
    b = a['prediction']
    c = a['label']

    count = 0
    for pred, label in zip(b,c):
        if pred == label:
            count += 1

    print(f'accuracy: {count/len(b)}')
    print(f'except_count: {except_count}')
    print(f'cost: ${all_tokens/1000*0.12}')
    print(f'the number of usable data: {using_count}')

    with open(f'{save_file_name}_error_count_log.txt', 'w') as f:
        f.write(f'{error_list}')

    with open(f'{save_file_name}_error_log.txt', 'w') as f:
        f.write(f'{error_log_list}')
