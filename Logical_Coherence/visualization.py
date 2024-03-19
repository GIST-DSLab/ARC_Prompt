import pandas as pd
from utils import *
from tqdm import tqdm

def convert(x):
    x = str(x)
    return x.replace('\n', '').replace('  ', ' ') 

index = 4
cot_dir_path = f"result/[CoT]result_{index}/"
l2m_dir_path = f"result/[L2M]result_{index}/"
tot_dir_path = f"result/[ToT]result_{index}/"

cot_file_name = f'cot_predict{index}'
l2m_file_name = f'L2M_result{index}'
tot_file_name = f'tot_result{index}'

cot_result = pd.read_csv(cot_dir_path + cot_file_name+'.csv', converters={"code": lambda x: str(x)})
l2m_result = pd.read_csv(l2m_dir_path + l2m_file_name+'.csv', converters={"code": lambda x: str(x)})
tot_result = pd.read_csv(tot_dir_path + tot_file_name+'.csv', converters={"code": lambda x: str(x)})

for result, save_dir, save_name in [(cot_result, cot_dir_path, cot_file_name), (l2m_result, l2m_dir_path, l2m_file_name), (tot_result, tot_dir_path, tot_file_name)]:
    print(f'================== current: {save_name} ==================')
    count = []
    correct_list = []
    incorrect_list = []
    correct_list.append(result[result['refine_prediction'] == result['label']])
    incorrect_list.append(result[result['refine_prediction'] != result['label']])
    print(f'len correct_list: {len(correct_list[0])}')
    print(f'len incorrect_list: {len(incorrect_list[0])}')
    for mode in ['correct', 'incorrect']:
        target = correct_list if mode == 'correct' else incorrect_list
        html = plot_2d_grid(target[0]['task_id'], target[0],mode=mode)
        write_file(plot_html=html, trial=str(index), method_name='', total_count=100, correct=target[0]['task_id'].shape[0], mode=mode, save_dir=save_dir, save_name=save_name)

