from model.tasks.arc import ARCEnv
import json
import pandas as pd

# Set the variables.
env=ARCEnv(dsl_file='dsl.txt')
task_id_list=[]
dsl_list=[]
task_list=[]
output=[]
task_id_map = pd.read_csv('result\\task_id_map.csv', converters={"code": lambda x: str(x)})

# Make the prediction output grids with productivity experiment result(DSLs)
with open("data\\arc.json") as json_file:
    data=json.load(json_file)
    for idx, task in enumerate(data):
        num=str(idx)
        with open(f"result\\dsl_output\\{num}.json") as dsl_file:
            dsl=json.load(dsl_file)
            print(f'now:{idx}')
            if len(dsl['steps'][-1]['select_new_ys']) == 0:
                task_list.append([])
                dsl_list.append('')
                output.append(task['test'][0]['output'])
                task_id_list.append(str(task_id_map[task_id_map['pre_task_id'] == idx].aft_task_id.values[0]))
                continue
            final_dsl=dsl['steps'][-1]['select_new_ys'][-1]
            dsl_list.append(final_dsl)
            split_dsl = final_dsl.split("->")
            temp_state = task['test'][0]['input']
            temp_output = task['test'][0]['output']
            output.append(temp_output)
            temp_object = task['test'][0]['objects']
            for command in split_dsl:
                try:
                    temp_state, temp_object = env.step(state=temp_state, object=temp_object, dsl=command)
                except:
                    temp_state = []
            task_list.append(temp_state)
            task_id_list.append(str(task_id_map[task_id_map['pre_task_id'] == idx].aft_task_id.values[0]))
            
df = pd.DataFrame({
    "task_id": task_id_list,
    "dsl": dsl_list,
    "prediction":task_list,
    "label": output,
    },
    dtype=object)

df.to_csv('result\\Result.csv', index=False)
