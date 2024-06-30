import argparse
from model.methods.bfs import arc_solve
from model.tasks.arc import ARCTask
import json
import os
import openai

# Set variable related with Azure OpenAI
openai.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 
args = argparse.Namespace(backend=openai.deployment_name, temperature=0.7, task='arc', naive_run=False, prompt_sample='standard', method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=3, n_evaluate_sample=1, n_select_sample=2)

task = ARCTask()

# Solve ARC task with tot prompts and DSLs
for i in range(99):
    if not os.path.exists('result\\dsl_output'):
        os.mkdir('result\\dsl_output')

    ys, infos = arc_solve(args, task, i)

    with open(f'result\\dsl_output\\{i}.json', 'w') as f:
        json.dump(infos, f, indent=4)
