import os.path

import pandas as pd

# CSV 파일을 pandas DataFrame으로 불러옵니다.
base_dir = 'result/[CoT-re-arc_correct]result_'

for i in range(0,5):
    df = pd.read_csv(f'{base_dir}{i}/cot_predict{i}.csv', converters={"code": lambda x: str(x)})

    if os.path.exists(f'{base_dir}{i}/[refine]cot_predict{i}.csv'):
        os.remove(f'{base_dir}{i}/[refine]cot_predict{i}.csv')

    task_ids_list = df['task_id'].unique().tolist()

    for id in task_ids_list:
        df_a = df[df['task_id'] == id]
        # try 값이 1부터 100까지 빠짐없이 존재해야 하므로, 이를 set으로 만듭니다.
        if len(df_a) == 100:
            continue
        expected_try_values = set(range(1, 101))

        # 현재 존재하는 try 값을 set으로 만듭니다.
        existing_try_values = set(df_a['try'])

        # 빠진 try 값을 찾습니다.
        missing_try_values = expected_try_values - existing_try_values

        # 빠진 try 값들에 대해 새로운 행을 생성합니다.
        missing_rows = pd.DataFrame({
            'task_id': [id] * len(missing_try_values),
            'try': list(missing_try_values),
            'prompt': [None] * len(missing_try_values),
            'answer': [None] * len(missing_try_values),
            'description': [None] * len(missing_try_values),
            'prediction': [None] * len(missing_try_values),
            'label': [None] * len(missing_try_values),
            'correct_flag': [False] * len(missing_try_values),
        })

        # 원래 DataFrame에 추가합니다.
        df = pd.concat([df, missing_rows], ignore_index=True)

    df.to_csv(f'{base_dir}{i}/[refine]cot_predict{i}.csv', index=False)

    df_check = pd.read_csv(f'{base_dir}{i}/[refine]cot_predict{i}.csv', converters={"code": lambda x: str(x)})
    num_each_task = df_check.groupby('task_id')['correct_flag'].count().reindex(task_ids_list, fill_value=0)
    num_each_task.to_csv(f'{base_dir}{i}/[refine]num_each_task{i}.csv')