import os
import json
from collections import OrderedDict
from tqdm import tqdm

train_path = './data/training/'
evaluation_path = './data/evaluation/'

data_train_dict = {}
data_evaluation_dict = {}

training_temp_train_input = []
training_temp_train_output = []
training_temp_test_input = []
training_temp_test_output = []

evaluation_temp_train_input = []
evaluation_temp_train_output = []
evaluation_temp_test_input = []
evaluation_temp_test_output = []

training_total_train_task_count = 0
training_total_test_task_count = 0
training_train_count = 0
training_test_count = 0
training_train_task_count = 0

evaluation_total_train_task_count = 0
evaluation_total_test_task_count = 0
evaluation_train_count = 0
evaluation_test_count = 0
evaluation_task_count = 0

training_prompt_sentence = []
training_completion_sentence = []
train_task_id = []

evaluation_subquestion_prompt_sentence = []
evaluation_completion_sentence = []
evaluation_task_id = []
evaluation_quiz_prompt_sentence = []
evaluation_solve_prompt_sentence = []

CoT_solve_prompt = """
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


CoT_subquestion_prompt1 = """
Do you know ARC problem?

Each example has same pattern and quiz also has  same pattern with examples.
So If you understand pattern of examples, you can solve quiz.

It will help you to analyze the pattern if you decompose the pattern into some steps.

I give an example that decomposes patterns into subquestions.

=========
# Example of how to decompose patterns into subquestions - start

Example 1
If input grids are like that
[[0, 0, 0, 0, 0, 0], [0, 0, 3, 0, 0, 0], [0, 3, 0, 3, 0, 0], [0, 0, 3, 0, 3, 0], [0, 0, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0]],
then this grids change to output grids below
[[0, 0, 0, 0, 0, 0], [0, 0, 3, 0, 0, 0], [0, 3, 4, 3, 0, 0], [0, 0, 3, 4, 3, 0], [0, 0, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0]].

Example 2
If input grids are like that
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 3, 0, 3, 0, 0, 0, 0, 0], [0, 0, 0, 3, 0, 3, 0, 0, 0, 0], [0, 0, 3, 0, 0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 0, 3, 0, 3, 0, 0], [0, 0, 0, 3, 0, 3, 3, 0, 0, 0], [0, 0, 3, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
then this grids change to output grids below
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 3, 0, 3, 0, 0, 0, 0, 0], [0, 0, 0, 3, 0, 3, 0, 0, 0, 0], [0, 0, 3, 0, 0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 0, 3, 4, 3, 0, 0], [0, 0, 0, 3, 0, 3, 3, 0, 0, 0], [0, 0, 3, 3, 3, 0, 0, 0, 0, 0], [0, 0, 0, 3, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]].

Example-Quiz
If input grids are like that
[[0, 0, 0, 0, 0, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 0, 0, 0, 0, 0], [0, 3, 3, 0, 3, 3, 0, 3, 0, 0], [3, 0, 0, 3, 0, 0, 3, 0, 3, 0], [0, 0, 0, 3, 0, 0, 3, 3, 0, 0], [0, 0, 0, 3, 0, 0, 3, 0, 0, 0], [0, 0, 0, 3, 0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 3, 3, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
then output grids?

To solve the quiz, I think we should do something like below

Q1: We need to identify the places surrounded by 3s in the input grid of example-quiz.
Q2: Fill in the 4 in the location we found through Q1.

Therefore we answer these questions aspect the quiz, then we solve the quiz.

If apply the quiz, then it like below
First, we need to identify the places surrounded by 3s in the input grid of example-quiz. [[0, 0, 0, 0, 0, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 0, 0, 0, 0, 0], [0, 3, 3, 0, 3, 3, 0, 3, 0, 0], [3, 0, 0, 3, 0, 0, 3, 0, 3, 0], [0, 0, 0, 3, 0, 0, 3, 3, 0, 0], [0, 0, 0, 3, 0, 0, 3, 0, 0, 0], [0, 0, 0, 3, 0, 0, 3, 0, 0, 0], [0, 0, 0, 0, 3, 3, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], then (3,4), (3,5), (3,7), (4,4), (4,5), (5,4), (5,5), (6,4), (6,5) are surrounded by 3s.

Second, we fill in the 4 in the location we found through Q1, then we get the below grids.

[[0, 0, 0, 0, 0, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 0, 0, 0, 0, 0], [0, 3, 3, 0, 3, 3, 0, 3, 0, 0], [3, 0, 0, 3, 4, 4, 3, 4, 3, 0], [0, 0, 0, 3, 4, 4, 3, 3, 0, 0], [0, 0, 0, 3, 4, 4, 3, 0, 0, 0], [0, 0, 0, 3, 4, 4, 3, 0, 0, 0], [0, 0, 0, 0, 3, 3, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]].

So, the output of the example-quiz is [[0, 0, 0, 0, 0, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 0, 0, 0, 0, 0], [0, 3, 3, 0, 3, 3, 0, 3, 0, 0], [3, 0, 0, 3, 4, 4, 3, 4, 3, 0], [0, 0, 0, 3, 4, 4, 3, 3, 0, 0], [0, 0, 0, 3, 4, 4, 3, 0, 0, 0], [0, 0, 0, 3, 4, 4, 3, 0, 0, 0], [0, 0, 0, 0, 3, 3, 0, 3, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]].

# Example of how to decompose patterns into subquestions - end
=========

Below is a real problem. You can decompose the problem into subquestions.
"""

CoT_subquestion_prompt2 = """
I want to you answer the format that is below
'''
Q1: ....
Q2: ....
....
QN: ....
'''
N is the index of last question.

(The answers to the last question should allow you to generate the output grid for the quiz, and you shouldn't solve the quiz yet in this process. You should only create the subquestions for solving the quiz. )
"""

for target_file in os.listdir(evaluation_path):
    with open(evaluation_path+target_file,'r') as f:
        data_evaluation_dict[target_file.split('.')[0]] = json.load(f)

for file_name, value in tqdm(data_evaluation_dict.items()):
    evaluation_task_count += 1
    example_number = 1
    subquestion_prompt_sentence = CoT_subquestion_prompt1
    solve_prompt_sentence = CoT_solve_prompt
    completion_sentence = ""

    for train_index in range(len(value['train'])):
        evaluation_total_train_task_count += 1
        for keys in value['train'][train_index].keys():
            if keys == 'input':
                evaluation_temp_train_input.append(value['train'][train_index][keys])
                subquestion_prompt_sentence += f"Example {example_number}\n" \
                                   f"If input grids are like that\n" \
                                   f"{value['train'][train_index][keys]},\n"
                solve_prompt_sentence += f"Example {example_number}\n" \
                                   f"If input grids are like that\n" \
                                   f"{value['train'][train_index][keys]},\n"
            else:
                evaluation_temp_train_output.append(value['train'][train_index][keys])
                subquestion_prompt_sentence += f"then this grids change to output grids below\n" \
                                   f"{value['train'][train_index][keys]}.\n\n"
                solve_prompt_sentence += f"then this grids change to output grids below\n" \
                                   f"{value['train'][train_index][keys]}.\n\n"
            evaluation_train_count += 1
        example_number += 1


    for test_index in range(len(value['test'])):
        evaluation_total_test_task_count += 1
        quiz_prompt_sentence = ''
        for keys in value['test'][test_index].keys():
            if keys == 'input':
                evaluation_temp_test_input.append(value['test'][test_index][keys])
                subquestion_prompt_sentence += f"Quiz\n" \
                                   f"If input grids are like that\n" \
                                   f"{value['test'][test_index][keys]},\n" \
                                   f"then output grids?\n\n" \
                                    f"========="
                quiz_prompt_sentence += f"Quiz\n" \
                                   f"If input grids are like that\n" \
                                   f"{value['test'][test_index][keys]},\n" \
                                   f"then output grids?\n\n" \
                                   f"========="
            else:
                evaluation_temp_test_output.append(value['test'][test_index][keys])
                completion_sentence = f"{value['test'][test_index][keys]}"

        subquestion_prompt_sentence += CoT_subquestion_prompt2
        evaluation_test_count += 1
        evaluation_subquestion_prompt_sentence.append(subquestion_prompt_sentence)
        evaluation_completion_sentence.append(completion_sentence)
        evaluation_task_id.append(file_name)
        evaluation_quiz_prompt_sentence.append(quiz_prompt_sentence)
        evaluation_solve_prompt_sentence.append(solve_prompt_sentence)

        if test_index == 0:
            break

for names in ['train', 'test']:
    if names == 'train':
        training_prompts = training_temp_train_input
        training_completions = training_temp_train_output
        evaluation_prompts = evaluation_temp_train_input
        evaluation_completions = evaluation_temp_train_output
    else:
        training_prompts = training_temp_test_input
        training_completions = training_temp_test_output
        evaluation_prompts = evaluation_temp_test_input
        evaluation_completions = evaluation_temp_test_output

if os.path.exists('data/l2m') == False:
    os.makedirs('data/l2m')

with open(f"data/l2m/Decompose_evaluation_dataset_CoT.jsonl", "w") as f:
    for task_id, subquestion_prompt, completion, solve_prompt, quiz_prompt in zip(evaluation_task_id ,evaluation_subquestion_prompt_sentence, evaluation_completion_sentence, evaluation_solve_prompt_sentence, evaluation_quiz_prompt_sentence):
        data_jsonl = OrderedDict()
        data_jsonl['task_id'] = task_id
        data_jsonl['subquestion_prompt'] = subquestion_prompt
        data_jsonl['completion'] = completion
        data_jsonl['solve_prompt'] = solve_prompt
        data_jsonl['quiz_prompt'] = quiz_prompt
        f.write(json.dumps(data_jsonl, ensure_ascii=False)+'\n')

print(f'evaluation_task_count: {evaluation_task_count}')
print(f'evaluation_train_count: {evaluation_train_count}')
print(f'evaluation_total_train_task_count: {evaluation_total_train_task_count}')
print(f'evaluation_test_count: {evaluation_test_count}')
print(f'evaluation_total_test_task_count: {evaluation_total_test_task_count}')
