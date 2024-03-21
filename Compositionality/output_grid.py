from ARC_Prompt.Compositionality.tot.tasks.arc import ARCEnv
import json
import pandas as pd
env=ARCEnv(dsl_file='dsl.txt')
task_id_list=[]
dsl_list=[]
task_list=[]
with open("ARC_Prompt\\Compositionality\\data\\arc.json") as json_file:
    data=json.load(json_file)
    for idx, task in enumerate(data):
        if idx!=19 and idx!=24 and idx!=48 and idx!=57 and idx!=60 and idx!=76 and idx!=96: #After the newly experiment, I'll change the code.
            num=str(idx)
            with open(f"ARC_Prompt\\Compositionality\\arc_result\\{num}.json") as dsl_file:
                dsl=json.load(dsl_file)
                print(f'now:{idx}')
                final_dsl=dsl['steps'][-1]['select_new_ys'][-1]
                dsl_list.append(final_dsl)
                split_dsl = final_dsl.split("->")
                temp_state = task['test'][0]['input']
                temp_object = task['test'][0]['objects']
                for command in split_dsl:
                    temp_state, temp_object = env.step(state=temp_state, object=temp_object, dsl=command)
                task_list.append(temp_state)
                task_id_list.append(idx)
            
df = pd.DataFrame({
    "task_id": task_id_list,
    "dsl": dsl_list,
    "prediction":task_list,
    },
    dtype=object)

df.to_csv('Result.csv', index=False)