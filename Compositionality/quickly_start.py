import argparse
from tot.methods.bfs import solve
from tot.tasks.arc import Game24Task

args = argparse.Namespace(backend='arc-turbo-preview', temperature=0.7, task='game24', naive_run=False, prompt_sample=None, method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=1, n_evaluate_sample=3, n_select_sample=5)

task = Game24Task()
ys, infos = solve(args, task, 900)
print(ys[0])