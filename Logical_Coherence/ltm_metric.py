import pandas as pd
import json
import os
from glob import glob
import re

# target_task_ids used in the experiment. It is a subset of the ids in the original dataset.
target_task_ids = list(set(['3ed85e70', '0f63c0b9', '17cae0c1', '47996f11', '4acc7107', '0692e18c', '477d2879', '1c0d0a4b', '292dd178', '1990f7a8', '22a4bbc2', '4364c1c4', '2f0c5170', '17b80ad2', '03560426', '0c786b71', '3391f8c0', '42a15761', '0bb8deee', '1e97544e', '1c02dbbe', '4b6b68e5', '2a5f8217', '3194b014', '1acc24af', '0c9aba6e', '0e671a1a', '37d3e8b2', '0becf7df', '0607ce86', '3a301edc', '2546ccf6', '009d5c81', '31adaf00', '281123b4', '3d31c5b3', '423a55dc', '1d0a4b61', '1a2e2828', '319f2597', '3979b1a8', '12422b43', '140c817e', '0a2355a6', '19bb5feb', '332efdb3', '27a77e38', '2c0b0aff', '00dbd492', '2c737e39', '2072aba6', '48f8583b', '27f8ce4f', '14754a24', '32e9702f', '195ba7dc', '137f0df0', '184a9768', '29700607', '1c56ad9f', '15663ba9', '4c177718', '136b0064', '0a1d4ef5', '1d398264', '09c534e7', '2685904e', '48131b3c', '31d5ba1a', '2697da3f', '103eff5b', '12997ef3', '1e81d6f9', '25094a63', '08573cc6', '20981f0e', '4852f2fa', '2b01abd0', '2072aba6', '1a6449f1', '34b99a2b', '0b17323b', '15696249', '414297c0', '2753e76c', '12eac192', '0934a4d8', '310f3251', '358ba94e', '21f83797', '4aab4007', '351d6448', '45bbe264', '456873bc', '15113be4', '3490cc26', '3b4c2228', '00576224', '42918530', '45737921', '20818e16']))
pattern = r"\[\[(((.|\n)*))\]\]"

# Calculate accuracy about five results
for index_number in range(0, 5):
    task_id_list = []
    task_list = []
    prompt_list = []
    prediction_list = []
    answer_list = []
    label_list = []
    save_path = f'result/[L2M]result_{index_number}'
    pd_file_name = f'L2M_result{index_number}.csv'
    for target_task_id in target_task_ids:
        cot_file =  f'{save_path}/{target_task_id}.json'

        if target_task_id == '3ed85e70':
            continue

        if not os.path.exists(cot_file):
            print(f'{cot_file} is not exist')
            continue

        with open(cot_file, 'r') as f:
            cot_infos = json.load(f)
        
        task_id = cot_infos['task_id']
        prompt = cot_infos['prompt']
        answer = cot_infos['answer']
        # postprocessing for prediction
        prediction = str(cot_infos['prediction']).replace('\n', '')
        label = cot_infos['label']

        task_id_list.append(task_id)
        prompt_list.append(prompt)
        prediction_list.append(prediction)
        answer_list.append(answer)
        label_list.append(label)


    df = pd.DataFrame({
    "task_id":task_id_list,
    "prompt": prompt_list,
    "answer": answer_list,
    "prediction": prediction_list,
    "label": label_list,
    "refine_prediction": prediction_list
    },
    dtype=object)

    # if index_number == 1:
    # df.to_csv(f'{save_path}/{pd_file_name}', index=None)

    def refine_prediction(prediction):
        if prediction:
            return str(prediction).replace('  ', ' ')
        else:
            return prediction

    df = pd.read_csv(f'{save_path}/{pd_file_name}', converters={"code": lambda x: str(x)})
    # postprocessing for refine_prediction
    df['refine_prediction']= df['refine_prediction'].apply(refine_prediction)
    df['correct_flag'] = df['refine_prediction'] == df['label']
    df.to_csv(f'{save_path}/{pd_file_name}', index=None)
