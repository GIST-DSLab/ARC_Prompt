import itertools
import numpy as np
from functools import partial
from tot.models import gpt
import re
import copy


def decomposing_parsing_info(output_list):
    subquestions_pattern = r"Q[1-9].*"
    temp_list = []
    for outputs in output_list:
        subquestions_match = re.search(subquestions_pattern, outputs[0])
        subquestions_p = re.compile(subquestions_pattern)
        temp_list.append(subquestions_p.findall(outputs))
    return temp_list

def reasoning_parsing_info(output_list, is_last=False):
    reasoning_pattern = r"((.|\n)*)" if is_last else r"A[1-9].*"
    temp_list = []
    for outputs in output_list:
        subquestions_match = re.search(reasoning_pattern, outputs[0])
        subquestions_p = re.compile(reasoning_pattern)
        if is_last:
            temp_list.append(subquestions_p.findall(outputs)[0])
        else:
            temp_list.append(subquestions_p.findall(outputs))
    return temp_list

def reasoning_get_value(task, examples, quiz, current_subquestions, subanswers_ys, new_subanswers_ys, n_evaluate_sample):
    value_prompt = task.reasoning_value_prompt_wrap(examples, quiz, current_subquestions, subanswers_ys, new_subanswers_ys)
    value_outputs = gpt(value_prompt, n=n_evaluate_sample, stop=None)
    value = task.reasoning_value_outputs_unwrap(value_outputs)
    return value

def reasoning_get_votes(task, examples, quiz, current_subquestions, subanswers_ys, new_subquesions_ys, n_evaluate_sample):
    vote_prompt = task.reasoning_vote_prompt_wrap(examples, quiz, current_subquestions, subanswers_ys, new_subquesions_ys)
    vote_outputs = gpt(vote_prompt, n=n_evaluate_sample, stop=None)
    values = task.reasoning_vote_outputs_unwrap(vote_outputs, len(new_subquesions_ys))
    return values

def reasoning_get_values(task, examples, quiz, current_subquestions, subanswers_ys, new_subanswers_ys, n_evaluate_sample):
    ids = list(range(len(new_subanswers_ys)))
    value_list = []
    for i in ids:
        value = reasoning_get_value(task, examples, quiz, current_subquestions, subanswers_ys, new_subanswers_ys[i], n_evaluate_sample)
        value_list.append(value)
    return value_list

def reasoning_get_samples(task, examples, quiz, subquestions, subanswers, n_generate_sample, is_last, stop):
    prompt = task.reasoning_standard_prompt_wrap(examples, quiz, subquestions, subanswers)
    if prompt == -1:
        return -1
    try:
        samples = gpt(prompt, n=n_generate_sample, stop=None)
        new_subanswers_ys = []
        if is_last:
            new_subanswers_ys = reasoning_parsing_info(samples, is_last=True)
        else:
            new_subanswers_ys = reasoning_parsing_info(samples)
        return [['\n'.join([subanswers[0], _[0]])] if subanswers[0] != '' else _ for _ in new_subanswers_ys]
    except:
        return -1

def decomposing_get_votes(task, examples, quiz, new_subquesions_ys, n_evaluate_sample):
    vote_prompt = task.decomposing_vote_prompt_wrap(examples, quiz, new_subquesions_ys)
    vote_outputs = gpt(vote_prompt, n=n_evaluate_sample, stop=None)
    values = task.decomposing_vote_outputs_unwrap(vote_outputs, len(new_subquesions_ys))
    return values

def decomposing_get_samples(task, examples, quiz, n_generate_sample, stop):
    prompt = task.decomposing_cot_prompt_wrap(examples, quiz)
    samples = gpt(prompt, n=n_generate_sample, stop=None)
    new_subquesions_ys = []
    new_subquesions_ys = decomposing_parsing_info(samples)
    return new_subquesions_ys

def decomposing_arc(args, task, idx, to_print=True):
    global gpt
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    examples, quiz, state = task.get_input(idx)  # input
    subquestions_ys = ['']  # current output candidates
    infos = []
    new_subquestions_ys = []
    # dsl generation
    new_subquestions_ys = decomposing_get_samples(task, examples, quiz, args.n_generate_sample, stop=task.stops)
    # new_dsl_ys = list(itertools.chain(*new_dsl_ys))


    ids = list(range(len(new_subquestions_ys)))
    # dsl evaluation
    values = decomposing_get_votes(task, examples, quiz, new_subquestions_ys, args.n_evaluate_sample)

    # selection
    if args.method_select == 'sample':
        ps = np.array(values) / sum(values)
        select_ids = np.random.choice(ids, size=args.n_select_sample, p=ps).tolist()
    elif args.method_select == 'greedy':
        select_id = sorted(ids, key=lambda x: values[x], reverse=True)[:args.n_select_sample]
    select_new_ys = new_subquestions_ys[select_id[0]]

    # log
    if to_print: 
        print({'total_subquestions_ys': new_subquestions_ys, 'values': values, 'select_new_ys': select_new_ys})
    
    infos.append({'total_subquestions_ys': new_subquestions_ys, 'values': values, 'select_new_ys': select_new_ys})
    subquestions_ys = select_new_ys
    
    if to_print: 
        print(f"subquestions_ys: {subquestions_ys}")
    return subquestions_ys, {'steps': infos}

def reasoning_arc(args, task, idx, subquestions, to_print=True):
    global gpt
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    examples, quiz, state = task.get_input(idx)  # input
    subanswers_ys = ['']  # current output candidates
    infos = []

    for step in range(len(subquestions)):
        # dsl generation
        current_subquestions = subquestions[:step+1]
        
        if step == len(subquestions) - 1:
            new_subanswers_ys = reasoning_get_samples(task, examples, quiz, current_subquestions, subanswers_ys, args.n_generate_sample, is_last=True, stop=task.stops)
        else:
            new_subanswers_ys = reasoning_get_samples(task, examples, quiz, current_subquestions, subanswers_ys, args.n_generate_sample, is_last=False, stop=task.stops)
        
        if new_subanswers_ys == -1:
            return -1, -1
        ids = list(range(len(new_subanswers_ys)))

        # dsl evaluation
        if step == len(subquestions) - 1:
            values = reasoning_get_values(task, examples, quiz, current_subquestions, subanswers_ys, new_subanswers_ys, args.n_evaluate_sample)
        else:
            values = reasoning_get_votes(task, examples, quiz, current_subquestions, subanswers_ys, new_subanswers_ys, args.n_evaluate_sample)

        # selection
        if args.method_select == 'sample':
            ps = np.array(values) / sum(values)
            select_ids = np.random.choice(ids, size=args.n_select_sample, p=ps).tolist()
        elif args.method_select == 'greedy':
            select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:args.n_select_sample]
        select_new_ys = new_subanswers_ys[select_ids[0]]

        # log
        if to_print: 
            print(f"step: {step}, current_subquestions: {current_subquestions}, select_new_ys: {select_new_ys}")
        
        infos.append({'step': step, 'current_subquestions': current_subquestions, 'new_subanswers_ys': new_subanswers_ys, 'values': values, 'select_new_ys': select_new_ys})
        subanswers_ys = select_new_ys
    
    return subanswers_ys, {'steps': infos}