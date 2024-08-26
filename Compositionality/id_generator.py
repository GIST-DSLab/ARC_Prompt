import os
import json
import pandas as pd

# Make the task_id_map.csv file
with open('data\\arc_no_object.json', 'r') as file:
    data = json.load(file)

data_list=[]
arc_name_list=[]

arc_dataset_folder_path = 'data\\arc_dataset'
for filename in os.listdir(arc_dataset_folder_path):
    if filename.endswith('.json'):
        with open(os.path.join(arc_dataset_folder_path, filename), 'r') as arc_file:
            arc_data = json.load(arc_file)

            for i in range(len(data)):
                if data[i] == arc_data:
                    print(f'Found match: {filename}')
                    data_list.append(i)
                    arc_name_list.append(filename)


df = pd.DataFrame({
    "pre_task_id": data_list,
    "aft_task_id": arc_name_list,
    },
    dtype=object)

df.to_csv('result\\task_id_map.csv', index=False)
