import itertools
import numpy as np
from functools import partial
from model.models import gpt
import re
import copy

def  parsing_info(temp_list, new_dsl_ys):
    dsl_pattern = r"- DSL name \(with the arguments for the DSL\): ((.|\n)*)"
    description_pattern = r"- Description \(Why you choose this DSL\?\): (.*)"
    for output in temp_list:
        dsl_match = re.search(dsl_pattern, output)
        dsl_p = re.compile(dsl_pattern)
        if dsl_match:
            extracted_array = dsl_match.group()
        else:
            extracted_array = None
        for i in range(len(dsl_p.findall(output))):
            if type(dsl_p.findall(output)[0]) == tuple:
                if dsl_p.findall(output)[0][i].split('\n')[-1] == '.':
                    continue
                temp = dsl_p.findall(output)[0][i].split('\n')[0]
            else:
                temp = dsl_p.findall(output)[i]
            new_dsl_ys.append(temp)

def arc_get_value(task, examples, quiz, dsl_y, state_y, n_evaluate_sample, cache_value=True):
    value_prompt = task.value_prompt_wrap(task, examples, quiz, dsl_y, state_y)
    if cache_value and value_prompt in task.value_cache:
        return task.value_cache[value_prompt]
    print('generating value..')
    value_outputs = gpt(value_prompt, n=n_evaluate_sample, stop=None)
    value = task.value_outputs_unwrap(value_outputs)
    print('got value')
    if cache_value:
        task.value_cache[value_prompt] = value
    return value

def arc_get_values(task, examples, quiz, new_dsl_ys, state_ys, n_evaluate_sample, cache_value=True):
    ids = list(range(len(new_dsl_ys)))
    value_list = []
    for dsl_y, state_y in zip(new_dsl_ys, state_ys):  # each partial output
            value = arc_get_value(task, examples, quiz, dsl_y, state_y, n_evaluate_sample, cache_value=cache_value)
            value_list.append(value)
    return value_list

def arc_get_votes(task, examples, quiz, new_dsl_ys, state_ys, n_evaluate_sample):
    vote_prompt = task.vote_prompt_wrap(examples, quiz, new_dsl_ys, state_ys)
    vote_outputs = gpt(vote_prompt, n=n_evaluate_sample, stop=None)
    values = task.vote_outputs_unwrap(vote_outputs, len(ys))
    return values

def arc_get_proposals(task, examples, quiz, dsl_y, state_y): 
    propose_prompt = task.propose_prompt_wrap(examples, quiz, dsl_y, state_y)
    proposals = gpt(propose_prompt, n=1, stop=None)[0].split('\n')
    return [y + _ + '\n' for _ in proposals]

def arc_get_samples(task, examples, quiz, object, dsl_y, state_y, n_generate_sample, prompt_sample, stop):
    if prompt_sample == 'standard':
        prompt = task.standard_prompt_wrap(examples, quiz, object, dsl_y, state_y)
    elif prompt_sample == 'cot':
        prompt = task.cot_prompt_wrap(examples, quiz, dsl_y, state_y)
    else:
        raise ValueError(f'prompt_sample {prompt_sample} not recognized')
    samples = gpt(prompt, n=n_generate_sample, stop=None)
    print("got samples")
    new_dsl_ys = []
    parsing_info(samples, new_dsl_ys)
    return [dsl_y + '->' + _ if len(dsl_y) >= 1 else _ for _ in new_dsl_ys]

def arc_solve(args, task, idx, to_print=True):
    global gpt
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    examples, quiz, object, state = task.get_input(idx)  # input
    dsl_ys = ['']  # current output candidates
    dsl_tree = {}
    state_ys = [[]]
    object_ys = [[]]
    infos = []
    new_dsl_ys = []
    for step in range(task.steps):
        for dsl_y, state_y, object_y in zip(dsl_ys, state_ys, object_ys):
            new_state_ys = []
            new_object_ys = []
            # dsl generation
            if args.method_generate == 'sample':
                if len(state_y) == 0:
                    new_dsl_ys = arc_get_samples(task, examples, quiz, object, '', state, args.n_generate_sample, prompt_sample=args.prompt_sample, stop=task.stops[step])
                else:
                    arr=arc_get_samples(task, examples, quiz, object_y, dsl_y, state_y, args.n_generate_sample, prompt_sample=args.prompt_sample, stop=task.stops[step])
                    new_dsl_ys+=arr    
            elif args.method_generate == 'propose':
                new_dsl_ys = [arc_get_proposals(task, examples, quiz, dsl_y, state_y) for dsl_y, state_y in zip(dsl_ys, state_ys)]
            # new_dsl_ys = list(itertools.chain(*new_dsl_ys))

            # apply dsl
        for dsl in new_dsl_ys:
            split_dsl = dsl.split("->")
            temp_state = copy.deepcopy(state)
            temp_object = copy.deepcopy(object)
            for i in range(len(split_dsl)):
                temp_state, temp_object = task.env.step(temp_state, temp_object, split_dsl[i]) #modified
                if temp_state==-1:
                    with open('error_occured.txt', 'a') as f:
                        f.write(f'{idx}\n')
            new_state_ys.append(temp_state)
            new_object_ys.append(temp_object)
        # state_ys = [task.env.step(state, dsl) for state, dsl in zip(state_ys, new_dsl_ys)]

        ids = list(range(len(new_dsl_ys)))
        # dsl evaluation
        if args.method_evaluate == 'vote':
            values = arc_get_votes(task, examples, quiz, new_dsl_ys, new_state_ys, args.n_evaluate_sample)
        elif args.method_evaluate == 'value':
            # values = arc_get_values(task, examples, quiz, new_object_ys, new_dsl_ys, new_state_ys, args.n_evaluate_sample)
            values = arc_get_values(task, examples, quiz, new_dsl_ys, new_state_ys, args.n_evaluate_sample)

        if args.method_select == 'sample':
            ps = np.array(values) / sum(values)
            select_ids = np.random.choice(ids, size=args.n_select_sample, p=ps).tolist()
        elif args.method_select == 'greedy':
            select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:args.n_select_sample]
        select_new_ys = [new_dsl_ys[select_id] for select_id in select_ids]
        select_new_object = [new_object_ys[select_id] for select_id in select_ids]
        select_new_state = [new_state_ys[select_id] for select_id in select_ids]

        if to_print: 
            print({'step': step, 'dsl_ys': dsl_ys, 'new_dsl_ys': new_dsl_ys, 'values': values, 'select_new_ys': select_new_ys})
        
        infos.append({'step': step, 'dsl_ys': dsl_ys, 'new_dsl_ys': new_dsl_ys, 'values': values, 'select_new_ys': select_new_ys})
        dsl_ys = select_new_ys
        state_ys = select_new_state
        object_ys = select_new_object
        new_dsl_ys = []
    
    if to_print: 
        print(f"dsl_ys: {dsl_ys}, state_ys: {state_ys}")
    return dsl_ys, {'steps': infos}