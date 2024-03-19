import argparse
from tot.methods.bfs import arc_solve
from tot.tasks.arc import ARCTask
import json
import os
import time
import openai

openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 
args = argparse.Namespace(backend=openai.deployment_name, temperature=0.7, task='arc', naive_run=False, prompt_sample='standard', method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=3, n_evaluate_sample=1, n_select_sample=1)

task = ARCTask()
for i in range(4, 5):
    if not os.path.exists('arc_result_1'):
        os.mkdir('arc_result_1')
    ys, infos = arc_solve(args, task, i)

    with open(f'arc_result_12/{i}.json', 'w') as f:
        json.dump(infos, f, indent=4)
