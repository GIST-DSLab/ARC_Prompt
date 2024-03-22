import pandas as pd
from utils import *
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


tot_dir_path="result\\Result.csv"
tot_result=pd.read_csv(tot_dir_path)
save_dir = 'result'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)


print(f'================== current ==================')
count = []
correct_list = []
incorrect_list = []
correct_list.append(tot_result[tot_result['prediction'] == tot_result['label']])
incorrect_list.append(tot_result[tot_result['prediction'] != tot_result['label']])
print(f'len correct_list: {len(correct_list[0])}')
print(f'len incorrect_list: {len(incorrect_list[0])}')
for mode in ['correct', 'incorrect']:
    target = correct_list if mode == 'correct' else incorrect_list
    html = plot_2d_grid(target[0]['task_id'], target[0],mode=mode)
    write_file(plot_html=html, trial=str(0), method_name='', total_count=len(correct_list)+len(incorrect_list), correct=target[0]['task_id'].shape[0], mode=mode, save_dir=save_dir, save_name='result')