import re
import os
import sympy
import pandas as pd
from tot.tasks.base import Task, DATA_PATH
from tot.prompts.arc_reasoning import * 
import json
import copy
from glob import glob

class ARCTask(Task):
    def __init__(self, folder='evaluation'):
        super().__init__()
        path = os.path.join(DATA_PATH, folder)
        self.data = []
        self.data_list = glob(os.path.join(path, '*.json'))
        for i in range(len(self.data_list)):
            with open(self.data_list[i], 'r') as f:
                self.data.append(json.load(f))
        self.value_cache = {}
        self.steps = 4 
        self.stops = ['\n'] * 4
        self.steps = 0
        self.current_idx = 0

    def __len__(self) -> int:
        return len(self.data)
    
    def get_input(self, idx: int):
        target_data = self.data[idx]
        self.current_file_name = self.data_list[idx]
        example_number = 1
        quiz_number = 1
        examples_prompt = ''
        quiz_prompt = ''
        for train_index in range(len(target_data['train'])):
            for keys in target_data['train'][train_index].keys():
                if keys == 'input':
                    examples_prompt += f"Example {example_number}\n" \
                                    f"If input grids are like that\n" \
                                    f"{target_data['train'][train_index][keys]},\n"
                else:
                    examples_prompt += f"then this grids change to output grids below\n" \
                                    f"{target_data['train'][train_index][keys]}.\n\n"

            example_number += 1

        for test_index in range(len(target_data['test'])):
            for keys in target_data['test'][test_index].keys():
                if quiz_number > 1:
                    break
                if keys == 'input':
                    quiz_prompt += f"Quiz\n" \
                                    f"If input grids are like that\n" \
                                    f"{target_data['test'][test_index][keys]},\n" \
                                    f"then output grids?\n\n" 
                    quiz_number += 1
        return examples_prompt, quiz_prompt, target_data['test'][test_index][keys]
    
    def test_output(self, idx: int, output: str):
        expression = output.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]
        numbers = re.findall(r'\d+', expression)
        problem_numbers = re.findall(r'\d+', self.data[idx])
        if sorted(numbers) != sorted(problem_numbers):
            return {'r': 0}
        try:
            return {'r': int(sympy.simplify(expression) == 24)}
        except Exception as e:
            return {'r': 0}

    def reasoning_standard_prompt_wrap(self, examples: str, quiz: str, subquestions: list, subanswers: list) -> str:
        prompt = reasoning_standard_prompt.format(examples=examples, quiz=quiz)
        try:
            if subquestions:
                subanswers_list = subanswers[0].split('\n')

            for i in range(len(subquestions)):
                if i == len(subquestions) - 1:
                    prompt += f"{subquestions[i]}\n"
                else:
                    prompt += f"{subquestions[i]}\n{subanswers_list[i]}\n\n"
        except:
            return -1

        return prompt

    def decomposing_cot_prompt_wrap(self, examples: str, quiz: str) -> str:
        return decomposing_cot_prompt.format(examples=examples, quiz=quiz)
    
    def reasoning_value_prompt_wrap(self, examples, quiz, subquestions, subanswers, new_subanswers_ys):
        prompt = reasoning_value_prompt.format(examples=examples, quiz=quiz)
        split_answers = new_subanswers_ys[0].split('\n')
        for i in range(len(subquestions)):
            if i == len(subquestions) - 1:
                temp = new_subanswers_ys[0].split('\n')[-1]
                prompt += f"{subquestions[i]}\n{temp}\n"
            else:
                prompt += f"{subquestions[i]}\n{split_answers[i]}\n\n"
        
        prompt += f'\nEvaluate the Current_state to solve this quiz(sure/maybe/impossible):'

        return prompt
    
    def reasoning_value_outputs_unwrap(self, value_outputs: list) -> float:
        value_names = [_.split('\n')[-1] for _ in value_outputs]
        value_map = {'impossible': 0.001, 'maybe': 1, 'sure': 20}  # TODO: ad hoc
        value = sum(value * target_value.count(name) for name, value in value_map.items() for target_value in value_names)
        return value
    
    def decomposing_vote_prompt_wrap(self, examples: str, quiz: str, ys: list) -> str:
        prompt = decomposing_vote_prompt.format(examples=examples, quiz=quiz)
        for i, y in enumerate(ys, 1):
            subquestions = '\n'.join(y)
            prompt += f"\nChoice {i}:\n{subquestions}\n"
        return prompt

    def decomposing_vote_outputs_unwrap(self, vote_outputs: list, n_candidates: int) -> list:
        vote_results = [0] * n_candidates
        for vote_output in vote_outputs:
            pattern = r".*best choice is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(n_candidates):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
        return vote_results
    
    def reasoning_vote_prompt_wrap(self, examples: str, quiz: str, subquestions:list,  subanswers: list, ys:list) -> str:
        prompt = reasoning_vote_prompt.format(examples=examples, quiz=quiz)
        if subquestions:
            subanswers_list = subanswers[0].split('\n')

        for i in range(len(subquestions)):
            if i == len(subquestions) - 1:
                prompt += f"\n{subquestions[i]}\n"
            else:
                prompt += f"\n{subquestions[i]}\n{subanswers_list[i]}\n"

        prompt += f'=======\n'

        for i, y in enumerate(ys):
            temp = y[0].split('\n')[-1] if y != [] else 'None'
            prompt += f'\nAnswer {i}:\n{temp}\n'

        return prompt
    
    def reasoning_vote_outputs_unwrap(self, vote_outputs: list, n_candidates: int) -> list:
        vote_results = [0] * n_candidates
        for vote_output in vote_outputs:
            pattern = r".*best answer is .*(\d+).*"
            match = re.match(pattern, vote_output, re.DOTALL)
            if match:
                vote = int(match.groups()[0]) - 1
                if vote in range(n_candidates):
                    vote_results[vote] += 1
            else:
                print(f'vote no match: {[vote_output]}')
                with open('[ToT]vote_no_match.txt', 'a') as f:
                    f.write(f'task_file: {self.current_file_name}\nvote no match: {vote_output}\n\n)')
        return vote_results
