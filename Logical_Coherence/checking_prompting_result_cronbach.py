import pandas as pd
import pingouin as pg

total_cot_results = dict()
total_l2m_results = dict()
total_tot_results = dict()
total_train_cot_results = dict()

tot_file_name = f'tot_result0'
tot_dir_path = f"result/[ToT]result_0/"

train_cot_dir_path = f"result/[CoT-train]result_0/"
train_cot_file_name = f'cot_predict0'

tot_a = pd.read_csv(tot_dir_path + tot_file_name + '.csv', converters={"code": lambda x: str(x)})
train_cot_a = pd.read_csv(train_cot_dir_path + train_cot_file_name + '.csv', converters={"code": lambda x: str(x)})

task_ids_list = tot_a['task_id'].tolist()
train_task_ids_list = train_cot_a['task_id'].tolist()

for id in task_ids_list:
    total_cot_results[id] = []
    total_l2m_results[id] = []
    total_tot_results[id] = []

for id in train_task_ids_list:
    total_train_cot_results[id] = []

for index in range(0,5):
    tot_file_name = f'tot_result{index}'
    tot_dir_path = f"result/[ToT]result_{index}/"
    l2m_dir_path = f"result/[L2M]result_{index}/"
    l2m_file_name = f'L2M_result{index}'
    cot_dir_path = f"result/[CoT]result_{index}/"
    cot_file_name = f'cot_predict{index}'
    train_cot_dir_path = f"result/[CoT-train]result_{index}/"
    train_cot_file_name = f'cot_predict{index}'

    tot_a = pd.read_csv(tot_dir_path + tot_file_name + '.csv', converters={"code": lambda x: str(x)})
    l2m_a = pd.read_csv(l2m_dir_path + l2m_file_name + '.csv', converters={"code": lambda x: str(x)})
    cot_a = pd.read_csv(cot_dir_path + cot_file_name + '.csv', converters={"code": lambda x: str(x)})
    train_cot_a = pd.read_csv(train_cot_dir_path + train_cot_file_name + '.csv', converters={"code": lambda x: str(x)})

    for row in tot_a.iterrows():
        total_tot_results[row[1]['task_id']].append(1 if row[1]['correct_flag'] == True else 0)

    for row in l2m_a.iterrows():
        total_l2m_results[row[1]['task_id']].append(1 if row[1]['correct_flag'] == True else 0)

    for row in cot_a.iterrows():
        total_cot_results[row[1]['task_id']].append(1 if row[1]['correct_flag'] == True else 0)

    for row in train_cot_a.iterrows():
        if row[1]['task_id'] == '5269061':
            row[1]['task_id'] = '05269061'
        elif row[1]['task_id'] == '5.12E+65':
            row[1]['task_id'] = '5117e062'
        elif row[1]['task_id'] == '8.90E+14':
            row[1]['task_id'] = '890034e9'
        total_train_cot_results[row[1]['task_id']].append(1 if row[1]['correct_flag'] == True else 0)


df_total_tot = pd.DataFrame(total_tot_results).T
df_total_l2m = pd.DataFrame(total_l2m_results).T
df_total_cot = pd.DataFrame(total_cot_results).T
df_total_train_cot = pd.DataFrame(total_train_cot_results).T

df_tot_cronbach_alpha = pg.cronbach_alpha(data=df_total_tot)
df_l2m_cronbach_alpha = pg.cronbach_alpha(data=df_total_l2m)
df_cot_cronbach_alpha = pg.cronbach_alpha(data=df_total_cot)
df_train_cot_cronbach_alpha = pg.cronbach_alpha(data=df_total_train_cot)

print('\n=============== tot ================')
print(df_tot_cronbach_alpha)
print('\n=============== l2m ================')
print(df_l2m_cronbach_alpha)
print('\n=============== cot ================')
print(df_cot_cronbach_alpha)
print('\n=============== train-cot ================')
print(df_train_cot_cronbach_alpha)
