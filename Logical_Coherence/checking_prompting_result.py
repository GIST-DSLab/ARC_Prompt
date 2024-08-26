import pandas as pd
from utils import *
from tqdm import tqdm
import json

arc_level = None
entry_list = []
easy_list = []
medium_list = []
hard_list = []
tedious_list = []
multiple_solutions_list = []
unfixed_list = []

d = []
f = []
g = []

def check_level(x):
    x = str(x)

    # This case handle the error in the task_id
    if x == '576224':
        x = '00' + x
    elif x == '2.08E+20':
        x = '20818e16'
    elif x == '3560426':
        x = '0' + x

    # Return the level of the task based on its ID
    if x in entry_list:
        return 'Entry'
    elif x in easy_list:
        return 'Easy'
    elif x in medium_list:
        return 'Medium'
    elif x in hard_list:
        return 'Hard'
    elif x in tedious_list:
        return 'Tedious'
    elif x in multiple_solutions_list:
        return 'Multiple solutions'
    elif x in unfixed_list:
        return 'Unfixed'
    else:
        return 'Unknown'

# Load level data from JSON file that bring from ARC_Game repository
with open('data\levels.json', 'r') as f:
    arc_level = json.load(f)
    entry_list = list(arc_level['Entry'].keys())
    easy_list = list(arc_level['Easy'].keys())
    medium_list = list(arc_level['Medium'].keys())
    hard_list = list(arc_level['Hard'].keys())
    tedious_list = list(arc_level['Tedious'].keys())
    multiple_solutions_list = list(arc_level['Multiple solutions'].keys())
    unfixed_list = list(arc_level['Unfixed'].keys())

total_entry = 0
total_easy = 0
total_medium = 0
total_hard = 0
total_tedious = 0
total_multiple_solutions = 0
total_unfixed = 0

correct_entry = 0
correct_easy = 0
correct_medium = 0
correct_hard = 0
correct_tedious = 0
correct_multiple_solutions = 0
correct_unfixed = 0
target_correct_list = [correct_entry, correct_easy, correct_medium, correct_hard, correct_tedious, correct_multiple_solutions, correct_unfixed]
target_acc_list = [0 for _ in range(len(target_correct_list))]

cot_correct_list = [0 for _ in range(len(target_correct_list))]
l2m_correct_list = [0 for _ in range(len(target_correct_list))]
tot_correct_list = [0 for _ in range(len(target_correct_list))]

cot_acc_list = [0 for _ in range(len(target_correct_list))]
l2m_acc_list = [0 for _ in range(len(target_correct_list))]
tot_acc_list = [0 for _ in range(len(target_correct_list))]


target_str_list = ['Entry', 'Easy', 'Medium', 'Hard', 'Tedious', 'Multiple solutions', 'Unfixed']
each_num_list = [0 for _ in range(len(target_str_list))]

# Process results from different methods (Chain of tought, Least to Most, Tree of Thoughts) for multiple results
for index in range(0,5):
    tot_file_name = f'tot_result{index}'
    tot_dir_path = f"result/[ToT]result_{index}/"
    l2m_dir_path = f"result/[L2M]result_{index}/"
    l2m_file_name = f'L2M_result{index}'
    cot_dir_path = f"result/[CoT]result_{index}/"
    cot_file_name = f'cot_predict{index}'


    tot_a = pd.read_csv(tot_dir_path + tot_file_name+'.csv', converters={"code": lambda x: str(x)})
    l2m_a = pd.read_csv(l2m_dir_path + l2m_file_name+'.csv', converters={"code": lambda x: str(x)})
    cot_a = pd.read_csv(cot_dir_path + cot_file_name+'.csv', converters={"code": lambda x: str(x)})

    tot_a['level'] = tot_a['task_id'].apply(check_level)
    l2m_a['level'] = l2m_a['task_id'].apply(check_level)
    cot_a['level'] = cot_a['task_id'].apply(check_level)

     # Our experiments repreated 5 times about each method, so we consider this point to calculate the total number of each level.
    if index == 0:
        total_entry = cot_a['level'][cot_a['level'] == 'Entry'].shape[0] * 15
        total_easy = cot_a['level'][cot_a['level'] == 'Easy'].shape[0] * 15
        total_medium = cot_a['level'][cot_a['level'] == 'Medium'].shape[0] * 15
        total_hard = cot_a['level'][cot_a['level'] == 'Hard'].shape[0] * 15
        total_tedious = cot_a['level'][cot_a['level'] == 'Tedious'].shape[0] * 15
        total_multiple_solutions = cot_a['level'][cot_a['level'] == 'Multiple solutions'].shape[0] * 15
        total_unfixed = cot_a['level'][cot_a['level'] == 'Unfixed'].shape[0] * 15
        each_num_list = [total_entry / 15, total_easy / 15, total_medium / 15, total_hard / 15, total_tedious / 15, total_multiple_solutions / 15, total_unfixed / 15]

    # Check the correct tasks & calculate the number of correct tasks.
    for correct_index, correct_count in enumerate(target_correct_list):
        tot_temp = tot_a[tot_a['level'] == target_str_list[correct_index]]
        l2m_temp = l2m_a[l2m_a['level'] == target_str_list[correct_index]]
        cot_temp = cot_a[cot_a['level'] == target_str_list[correct_index]]
        target_correct_list[correct_index] += tot_temp[tot_temp['correct_flag'] == True].shape[0]
        target_correct_list[correct_index] += l2m_temp[l2m_temp['correct_flag'] == True].shape[0]
        target_correct_list[correct_index] += cot_temp[cot_temp['correct_flag'] == True].shape[0]
        cot_correct_list[correct_index] += cot_temp[cot_temp['correct_flag'] == True].shape[0]
        l2m_correct_list[correct_index] += l2m_temp[l2m_temp['correct_flag'] == True].shape[0]
        tot_correct_list[correct_index] += tot_temp[tot_temp['correct_flag'] == True].shape[0]

    tot_a.to_csv(tot_dir_path+tot_file_name+'_level.csv', index=None)
    l2m_a.to_csv(l2m_dir_path+l2m_file_name+'_level.csv', index=None)
    cot_a.to_csv(cot_dir_path+cot_file_name+'_level.csv', index=None)

total_num_list = [total_entry, total_easy, total_medium, total_hard, total_tedious, total_multiple_solutions, total_unfixed]

# Calculate accuracy for each category.
for i, total_num in enumerate(total_num_list):
    target_acc_list[i] = target_correct_list[i]/total_num
    cot_acc_list[i] = cot_correct_list[i]/(total_num / 3)
    l2m_acc_list[i] = l2m_correct_list[i]/(total_num / 3)
    tot_acc_list[i] = tot_correct_list[i]/(total_num / 3)
    

df = pd.DataFrame(index=target_str_list, data={'each_num': each_num_list, 'total_num': total_num_list, 'correct_num': target_correct_list, 'total_acc': target_acc_list, 'cot_acc': cot_acc_list, 'ltm_acc': l2m_acc_list, 'tot_acc': tot_acc_list})
df.to_csv('result/prompting_acc.csv')


