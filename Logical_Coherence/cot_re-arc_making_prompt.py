import json
import os
import numpy as np
import random
import pandas as pd
from collections import OrderedDict

# Set the seed for augmentation
SEED = 777
INCORRECT_NUM = 20
MAX_AUG_NUM = 100

np.random.seed(SEED)
random.seed(SEED)

# Set the directory
re_arc_dir = 'data/re_arc/tasks'
save_dir = 'data/cot'
train_dir = './data/training/'
evaluation_dir = './data/evaluation/'
cot_result_dir = 'result/[CoT-train]result_'
train_data_dict = {}
evaluation_data_dict = {}

# Load the task ids
for target_file in os.listdir(train_dir):
    with open(train_dir + target_file, 'r') as f:
        train_data_dict[target_file.split('.')[0]] = json.load(f)

for target_file in os.listdir(evaluation_dir):
    with open(evaluation_dir + target_file, 'r') as f:
        evaluation_data_dict[target_file.split('.')[0]] = json.load(f)

start_prompt_sentence = """
Do you know ARC problem?

It is similary below.

=========
Example 1

If input grids are like that
[[0, 3, 0, 0, 0, 0], [0, 3, 0, 2, 0, 0], [0, 0, 0, 2, 0, 0], [0, 8, 0, 0, 2, 2], [0, 0, 0, 0, 2, 2], [6, 6, 6, 0, 0, 0]],
then this grids change to output grids below
[[0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 3, 2], [0, 0, 0, 0, 0, 2], [0, 0, 0, 8, 2, 2], [0, 0, 0, 0, 2, 2], [0, 0, 0, 6, 6, 6]].

=========

You can understand the pattern of this problem with input-output pair about example1.
In above case, you can inference like below.

In example 1 case, all obejct move right. So if given input is below,
[[0, 3, 0, 0, 0, 0], [0, 3, 0, 2, 0, 0], [0, 0, 0, 2, 0, 0], [0, 8, 0, 0, 2, 2], [0, 0, 0, 0, 2, 2], [6, 6, 6, 0, 0, 0]],
then you can move object to right side.
[[0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 3, 2], [0, 0, 0, 0, 0, 2], [0, 0, 0, 8, 2, 2], [0, 0, 0, 0, 2, 2], [0, 0, 0, 6, 6, 6]].

Like this concept, 'object', 'count', 'color', 'move', 'row', 'column' and etc, helps you to understand patterns of problem and solve it.

Below problem is other pattern to solve. So you can understand below pattern with several examples and apply quiz's input to get right output.

=========
"""

start_completion_sentence = "<quiz answer>"

# Variables to store the re-arc prompt and completion
correct_task_id_set = set()
incorrect_task_id_set = set()
target_incorrect_task_id_set = []

rearc_correct_prompt_sentence = []
rearc_correct_completion_sentence = []
rearc_correct_task_id = []

rearc_incorrect_prompt_sentence = []
rearc_incorrect_completion_sentence = []
rearc_incorrect_task_id = []

def make_train_prompt(task_id, is_correct_flag):
    if task_id in train_data_dict:
        data_dict = train_data_dict[task_id]
    else:
        data_dict = evaluation_data_dict[task_id]

    with open(f'{re_arc_dir}/{task_id}.json', 'r') as f:
        re_arc_data = json.load(f)

    for i in range(len(re_arc_data)):
        train_count = 0
        test_count = 0
        temp_train_input = []
        temp_train_output = []
        temp_rearc_input = []
        temp_rearc_output = []


        example_number = 1
        prompt_sentence = start_prompt_sentence
        completion_sentence = ""

        for train_index in range(len(data_dict['train'])):
            for keys in data_dict['train'][train_index].keys():
                if keys == 'input':
                    temp_train_input.append(data_dict['train'][train_index][keys])
                    prompt_sentence += f"Example {example_number}\n" \
                                       f"If input grids are like that\n" \
                                       f"{data_dict['train'][train_index][keys]},\n"
                else:
                    temp_train_output.append(data_dict['train'][train_index][keys])
                    prompt_sentence += f"then this grids change to output grids below\n" \
                                       f"{data_dict['train'][train_index][keys]}.\n\n"
                train_count += 1

            example_number += 1

        temp_rearc_input.append(re_arc_data[i]['input'])
        prompt_sentence += f"Quiz\n" \
                           f"If input grids are like that\n" \
                           f"{re_arc_data[i]['input']},\n" \
                           f"then output grids?\n\n" \
                           f"========="
        temp_rearc_output.append(re_arc_data[i]['output'])
        completion_sentence = f"{re_arc_data[i]['output']}"


        if is_correct_flag:
            rearc_correct_prompt_sentence.append(prompt_sentence)
            rearc_correct_completion_sentence.append(completion_sentence)
            rearc_correct_task_id.append(task_id)
        else:
            rearc_incorrect_prompt_sentence.append(prompt_sentence)
            rearc_incorrect_completion_sentence.append(completion_sentence)
            rearc_incorrect_task_id.append(task_id)

        if i+1 >= MAX_AUG_NUM:
            break

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for i in range(0, 4):
    cot_result_name = f'{cot_result_dir}{i}/cot_predict{i}.csv'
    cot_result = pd.read_csv(cot_result_name)
    cot_correct_task_id = cot_result[cot_result['correct_flag'] == True]['task_id'].tolist()
    cot_incorrect_task_id = cot_result[cot_result['correct_flag'] == False]['task_id'].tolist()

    correct_task_id_set.update(cot_correct_task_id)
    incorrect_task_id_set.update(cot_incorrect_task_id)

target_incorrect_task_id_set = random.sample(list(incorrect_task_id_set), INCORRECT_NUM)

for task_id in correct_task_id_set:
    make_train_prompt(task_id, True)

for task_id in target_incorrect_task_id_set:
    make_train_prompt(task_id, False)

for name in ['correct', 'incorrect']:
    with open(f"{save_dir}/re-arc_{name}_dataset.jsonl", "w") as f:
        if name == 'correct':
            task_id = rearc_correct_task_id
            prompt_sentence = rearc_correct_prompt_sentence
            completion_sentence = rearc_correct_completion_sentence
        else:
            task_id = rearc_incorrect_task_id
            prompt_sentence = rearc_incorrect_prompt_sentence
            completion_sentence = rearc_incorrect_completion_sentence

        for task_id, prompt, completion in zip(task_id, prompt_sentence, completion_sentence):
            data_jsonl = OrderedDict()
            data_jsonl['task_id'] = task_id
            data_jsonl['prompt'] = prompt
            data_jsonl['completion'] = completion
            f.write(json.dumps(data_jsonl, ensure_ascii=False)+'\n')






