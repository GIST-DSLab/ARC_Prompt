import argparse
from model.methods.bfs import decomposing_arc, reasoning_arc
from model.tasks.arc import ARCTask
import json
import os
from glob import glob
from tqdm import tqdm
import pandas as pd
import re
import openai

# Set variable realted the azure openai.  
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 

decomposing_args = argparse.Namespace(backend=openai.deployment_name, temperature=0, task='arc', naive_run=False, prompt_sample='standard', method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=3, n_evaluate_sample=3, n_select_sample=1)
reasoning_args = argparse.Namespace(backend=openai.deployment_name, temperature=0, task='arc', naive_run=False, prompt_sample='standard', method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=3, n_evaluate_sample=3, n_select_sample=1)

task = ARCTask()
target_task_ids = list(set(['3ed85e70', '0f63c0b9', '17cae0c1', '47996f11', '4acc7107', '0692e18c', '477d2879', '1c0d0a4b', '292dd178', '1990f7a8', '22a4bbc2', '4364c1c4', '2f0c5170', '17b80ad2', '03560426', '0c786b71', '3391f8c0', '42a15761', '0bb8deee', '1e97544e', '1c02dbbe', '4b6b68e5', '2a5f8217', '3194b014', '1acc24af', '0c9aba6e', '0e671a1a', '37d3e8b2', '0becf7df', '0607ce86', '3a301edc', '2546ccf6', '009d5c81', '31adaf00', '281123b4', '3d31c5b3', '423a55dc', '1d0a4b61', '1a2e2828', '319f2597', '3979b1a8', '12422b43', '140c817e', '0a2355a6', '19bb5feb', '332efdb3', '27a77e38', '2c0b0aff', '00dbd492', '2c737e39', '2072aba6', '48f8583b', '27f8ce4f', '14754a24', '32e9702f', '195ba7dc', '137f0df0', '184a9768', '29700607', '1c56ad9f', '15663ba9', '4c177718', '136b0064', '0a1d4ef5', '1d398264', '09c534e7', '2685904e', '48131b3c', '31d5ba1a', '2697da3f', '103eff5b', '12997ef3', '1e81d6f9', '25094a63', '08573cc6', '20981f0e', '4852f2fa', '2b01abd0', '2072aba6', '1a6449f1', '34b99a2b', '0b17323b', '15696249', '414297c0', '2753e76c', '12eac192', '0934a4d8', '310f3251', '358ba94e', '21f83797', '4aab4007', '351d6448', '45bbe264', '456873bc', '15113be4', '3490cc26', '3b4c2228', '00576224', '42918530', '45737921', '20818e16']))
except_task_ids = []

# Repeat the experiments five times
for index_number in range(0,5):
    tot_folder = f'result/[ToT]result_{index_number}'
    save_dir = f'result/[ToT]result_{index_number}/{index_number}'

    if not os.path.exists(tot_folder):
            os.mkdir(tot_folder)

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    for target_task_id in tqdm(target_task_ids):
        # Select the target_task information in total evaluation dataset files.
        for i in range(len(task.data_list)):
                if target_task_id in task.data_list[i]:
                    idx = i
                    break
        
        target_decomposing_file_name = f'{save_dir}/decomposing_{target_task_id}.json'
        target_reasoning_file_name = f'{save_dir}/reasoning_{target_task_id}.json'

         # Check this file exists to skip decomposing process.
        if not os.path.exists(target_decomposing_file_name):
            task_id = task.data_list[idx].split('\\')[-1].split('.')[0]
            # Decompose the task with tree of thoughts prompt method.
            decomposing_ys, decomposing_infos = decomposing_arc(decomposing_args, task, idx, to_print=False)

            with open(target_decomposing_file_name, 'w') as f:
                json.dump(decomposing_infos, f, indent=4)
        else:
            with open(target_decomposing_file_name, 'r') as f:
                decomposing_ys = json.load(f)['steps'][0]['select_new_ys']

        # Check this file exists to skip reasoning process.
        if not os.path.exists(target_reasoning_file_name):
            task_id = task.data_list[idx].split('\\')[-1].split('.')[0]

            # Reason the task with tree of thoughts prompt method.
            reasoning_ys, reasoning_infos = reasoning_arc(reasoning_args, task, idx, decomposing_ys, to_print=False)

            # Check the error case.
            if reasoning_ys == -1:
                except_task_ids.append(task_id)
                print(f"reasoning_ys is -1: {task_id}")
                continue

            with open(target_reasoning_file_name, 'w') as f:
                json.dump(reasoning_infos, f, indent=4)
        else:
            continue

    with open(f'{save_dir}/except_task_ids.txt', 'w') as f:
        json.dump(except_task_ids, f)
