import itertools
import numpy as np
from functools import partial
from model.models import gpt
import re
import copy
import json
import ast
from model.errors import ParseError
from model.prompts.arc import sample_format_prompt, value_format_prompt, test_output_info, add_info, reuse_value_format_prompt

# Parse instructions from LLM response.
def parsing_info(temp_list, new_dsl_ys, step):
    dsl_pattern = r"- dsl \(with the arguments for the DSL\): ((.|\n)*)"
    pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)
    description_pattern = r"- Description \(Why you choose this DSL\?\): (.*)"
    total_result_json_list = []
    result_json_list = []

    for output in temp_list:
        matches = pattern.findall(output)
        for match in matches:
            try:
                if 'dsl' not in match and 'step' not in match:
                    continue

                if 'step' in match:
                    match=match.replace("step:", "step")

                if 'dsl' in match:
                    match=match.replace("dsl:", "dsl")

                if 'value' in match:
                    match=match.replace("value:", "value")

                if 'description' in match:
                    match=match.replace("description:", "description")

                try:
                    parsed_log = json.loads(match)
                except json.JSONDecodeError as e:
                    try:
                        parsed_log = json.loads(match.replace("'", '"'))
                    except json.JSONDecodeError as e:
                        try:
                            parsed_log = json.loads(match.replace('"', "'"))
                        except json.JSONDecodeError as e:
                            try:
                                parsed_dict = ast.literal_eval(match)
                                parsed_log = json.dumps(parsed_dict)
                            except Exception as e:
                                ParseError(f"error message: {e}\nMatch value: {match}")

                if 'step' in parsed_log.keys():
                    if parsed_log['step'] == 'complete':
                        parsed_log['step'] = step
                    else:
                        parsed_log['step'] = int(parsed_log['step'])

                total_result_json_list.append(parsed_log)

                if 'step' not in parsed_log.keys() or ('dsl' not in parsed_log.keys() and 'value' not in parsed_log.keys()):
                    continue

                if parsed_log['step'] == step:
                    if 'dsl' in parsed_log.keys():
                        new_dsl_ys.append(parsed_log['dsl'])
                    result_json_list.append(parsed_log)

            except json.JSONDecodeError as e:
                pass

    return total_result_json_list, result_json_list

# LLM self-evaluate the response result to LLM.
def arc_get_value(task, examples, quiz, dsl_y, state_y, test_output_info, add_info, n_evaluate_sample, object, step, assistant_prompt, cache_value=True, previous_values='None'):
    value_prompt = task.value_prompt_wrap(task, examples, quiz, dsl_y, state_y, object=object, step=step, test_output_info=test_output_info,add_info=add_info, previous_values=previous_values)
    if cache_value and value_prompt in task.value_cache:
        value_map = { 0.001: 'impossible', 1: 'maybe', 20: 'sure'}
        value_name = value_map[task.value_cache[value_prompt]]

        return task.value_cache[value_prompt], f"Reuse value_cache({value_prompt}: {task.value_cache[value_prompt]})", [0], [0], [0], \
            [json.loads(reuse_value_format_prompt.format(current_step=step, value=value_name, current_grid=state_y))], [json.loads(reuse_value_format_prompt.format(current_step=step, value=value_name, grid=state_y))], \
            [json.loads(reuse_value_format_prompt.format(current_step=step, value=value_name, current_grid=state_y))], [0]

    print('generating value..')
    assistant_prompt = assistant_prompt.format(current_step=step)
    value_outputs, message, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, outputs, use_total_outputs_index = gpt(value_prompt, n=n_evaluate_sample, stop=None, assistant_prompt=assistant_prompt, mode='value', step=step)
    total_result_json, result_json = parsing_info(value_outputs, [], step)
    result_json[0]['grid'] = state_y
    value = task.value_outputs_unwrap(result_json)
    print('got value')
    if cache_value:
        task.value_cache[value_prompt] = value
    return value, message, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, outputs, total_result_json, result_json, use_total_outputs_index

# LLM self-evaluate each suggestion that created by reasoning_get_samples.
def arc_get_values(task, examples, quiz, new_dsl_ys, state_ys, test_output_info, add_info, n_evaluate_sample, object, step, assistant_prompt, cache_value=True, previous_values='None'):
    ids = list(range(len(new_dsl_ys)))
    value_list = []
    message_list = []
    num_tokens_input_list = []
    num_tokens_output_list = []
    num_tokens_total_list = []
    total_outputs = []
    total_result_json = []
    result_json = []
    use_total_outputs_index = []
    for dsl_y, state_y in zip(new_dsl_ys, state_ys):
        try:# each partial output
            value, message, num_tokens_input, num_tokens_output, num_tokens_total, output, full_json, a_json, use_output_index = arc_get_value(task, examples, quiz, dsl_y, state_y, test_output_info, add_info, n_evaluate_sample, object=object, step=step, cache_value=cache_value, assistant_prompt=assistant_prompt, previous_values=previous_values)
        except Exception as e:
            print(e)
        value_list.append(value)
        message_list.append(message)
        num_tokens_input_list.append(num_tokens_input)
        num_tokens_output_list.append(num_tokens_output)
        num_tokens_total_list.append(num_tokens_total)
        total_outputs.append(output)
        total_result_json.append(full_json)
        result_json.append(a_json)
        use_total_outputs_index.append(use_output_index)
    return value_list, message_list, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, total_outputs, total_result_json, result_json, use_total_outputs_index

def arc_get_samples(task, examples, quiz, object, dsl_y, state_y, test_output_info, add_info, n_generate_sample, n_selected_sample, prompt_sample, stop, assistant_prompt, step, start_flag=False):
    if prompt_sample == 'standard':
        assistant_prompt = assistant_prompt.format(current_step=step)
        prompt = task.standard_prompt_wrap(examples=examples, quiz=quiz, object=object, dsl_y=dsl_y, state_y=state_y, step=step, test_output_info=test_output_info, add_info=add_info)
    else:
        raise ValueError(f'prompt_sample {prompt_sample} not recognized')
    print("got samples")
    new_dsl_ys = []
    num_of_generation = n_generate_sample if start_flag else n_generate_sample * 2
    total_result_json_list = []
    result_json_list = []
    total_message = []
    total_num_tokens_input_list = []
    total_num_tokens_output_list = []
    total_num_tokens_total_list = []
    total_outputs = []
    use_total_outputs_index = []
    while True:
        target_num = num_of_generation - len(new_dsl_ys)
        samples, message, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, outputs, use_output_index = gpt(prompt,n=target_num,stop=None,assistant_prompt=assistant_prompt, mode='sample', step=step)
        total_result_json, result_json = parsing_info(samples, new_dsl_ys, step)
        total_outputs.append(outputs)
        use_total_outputs_index.append(use_output_index)
        total_message += message
        total_num_tokens_input_list += num_tokens_input_list
        total_num_tokens_output_list += num_tokens_output_list
        total_num_tokens_total_list += num_tokens_total_list
        total_result_json_list += total_result_json
        result_json_list += result_json
        if len(new_dsl_ys) == num_of_generation:
            break
    return [dsl_y + '->' + _ if len(dsl_y) >= 1 else _ for _ in new_dsl_ys], total_result_json_list, result_json_list, total_message, total_num_tokens_input_list, total_num_tokens_output_list, total_num_tokens_total_list, total_outputs, use_total_outputs_index

# Solve tasks(predict how to use DSLs to solve given task)
def arc_solve(args, task, idx, input_price, output_price, include_test_output, additional_info, df_add_info, to_print=True):
    global gpt
    gpt = partial(gpt, model=args.backend, temperature=args.temperature)
    print(gpt)
    examples, quiz, object, state, label_grid = task.get_input(idx)  # input
    dsl_ys = ['']  # current output candidates
    dsl_tree = {}
    state_ys = [[]]
    object_ys = [[]]
    infos = []
    new_dsl_ys = []
    tatal_result_log = {'samples': [], 'values': [], 'selections': []}
    complete_dsls = []
    complete_grids = []
    complete_corrects = []
    complete_objects = []
    test_output_info_prompt = ''
    add_info_prompt = ''
    select_value_json_result = None
    num_selected_sample = args.n_select_sample


    if include_test_output:
        test_output_info_prompt = test_output_info.format(test_output=label_grid)

    if additional_info:
        target_column = None
        if additional_info == 'MC-LARC':
            # target_column = 'description_output_mc_larc'
            target_column = 'description_output'
        elif additional_info == 'LARC':
            target_column = 'description_output'
        elif additional_info == 'Fast-Flexible':
            target_column = 'select_final_description'

        add_info_prompt = add_info.format(add_info=df_add_info[df_add_info['problem'] == idx][target_column].values[0])

    for step in range(1, task.steps+1):
        new_state_ys = []
        new_object_ys = []

        for dsl_y, state_y, object_y in zip(dsl_ys, state_ys, object_ys):
            # dsl generation
            if len(state_y) == 0:
                new_dsl_ys, total_result_json_list, result_json_list, message, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, total_samples_outputs, use_total_outputs_index = arc_get_samples(task, examples, quiz, object, '', state, test_output_info_prompt, add_info_prompt, args.n_generate_sample, num_selected_sample, prompt_sample=args.prompt_sample, stop=task.stops[step], assistant_prompt=sample_format_prompt, step=step, start_flag=True)
            else:
                arr, total_result_json_list, result_json_list, message, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, total_samples_outputs, use_total_outputs_index = arc_get_samples(task, examples, quiz, object_y, dsl_y, state_y, test_output_info_prompt, add_info_prompt, args.n_generate_sample, num_selected_sample, prompt_sample=args.prompt_sample, stop=task.stops[step], assistant_prompt=sample_format_prompt, step=step)
                new_dsl_ys+=arr

        # apply dsl
        corrects = []
        for dsl in new_dsl_ys:
            split_dsl = dsl.split("->")
            temp_state = copy.deepcopy(state)
            temp_object = copy.deepcopy(object)
            for i in range(len(split_dsl)):
                temp_state, temp_object = task.env.step(temp_state, temp_object, split_dsl[i])
            if np.array_equal(temp_state, label_grid):
                corrects.append(True)
            else:
                corrects.append(False)
            new_state_ys.append(temp_state)
            new_object_ys.append(temp_object)

        tatal_result_log['samples'].append(
            {
                'step': step,
                'prompt': message,
                'dsl': new_dsl_ys,
                'prev_object': object,
                'after_object': new_object_ys,
                'prev_grid': state,
                'after_grid': new_state_ys,
                'label_grid': label_grid,
                'corrects': corrects,
                'step_result': result_json_list,
                'total_result': total_result_json_list,
                "total_outputs": total_samples_outputs,
                "use_total_outputs_index": use_total_outputs_index,
                "num_input_tokens": [num_tokens_input_list],
                "num_output_tokens": [num_tokens_output_list],
                "num_total_tokens": [num_tokens_total_list],
                "step_cost": [sum(num_tokens_input_list) * input_price + sum(num_tokens_output_list) * output_price],
            }
        )


        ids = list(range(len(new_dsl_ys)))
        # dsl evaluation
        if step == 1:
            values, messages, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, total_values_outputs, total_result_json, result_json, use_total_outputs_index = arc_get_values(task, examples, quiz, new_dsl_ys, new_state_ys, test_output_info_prompt, add_info_prompt, args.n_evaluate_sample, object=object, step=step, assistant_prompt=value_format_prompt)
        else:
            values, messages, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, total_values_outputs, total_result_json, result_json, use_total_outputs_index = arc_get_values(task, examples, quiz, new_dsl_ys, new_state_ys, test_output_info_prompt, add_info_prompt, args.n_evaluate_sample, object=object, step=step, assistant_prompt=value_format_prompt, previous_values=select_value_json_result)
            # TODO previous_values(value_history)를 이어붙여야 함.

        tatal_result_log['values'].append(
            {
                'step': step,
                'prompt': messages,
                'dsl': new_dsl_ys,
                'values': values,
                'object': object,
                'grid': state,
                'label_grid': label_grid,
                'corrects': corrects,
                'step_result': result_json,
                'total_result': total_result_json,
                "total_outputs": total_values_outputs,
                "use_total_outputs_index": use_total_outputs_index,
                "num_input_tokens": [num_tokens_input_list],
                "num_output_tokens": [num_tokens_output_list],
                "num_total_tokens": [num_tokens_total_list],
                "step_cost": [sum([sum(x) for x in num_tokens_input_list])* input_price + sum([sum(x) for x in num_tokens_output_list]) * output_price],
            }
        )

        # select the dsl and its state and object information.
        # TODO complete이 나왔을때에는 어떻게 처리를 할 것인가?
        select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:num_selected_sample]
        select_new_ys = [new_dsl_ys[select_id] for select_id in select_ids]
        select_new_object = [new_object_ys[select_id] for select_id in select_ids]
        select_new_state = [new_state_ys[select_id] for select_id in select_ids]
        select_value_json_result = [result_json[select_id] if select_value_json_result == None else select_value_json_result[i] + result_json[select_id] for i, select_id in enumerate(select_ids)]
        select_corrects = [corrects[select_id] for select_id in select_ids]

        tatal_result_log['selections'].append(
            {
                'step': step,
                'selected_ids': select_ids,
                'selected_dsl': select_new_ys,
                'selected_object': select_new_object,
                'selected_grid': select_new_state,
                'selected_corrects': select_corrects,
                'label_grid': label_grid,
                'selected_values_json': select_value_json_result,
                'complete_dsls': complete_dsls,
                'complete_grids': complete_grids,
                'complete_objects': complete_objects,
                'complete_corrects': complete_corrects,
            }
        )

        if to_print: 
            print({'step': step, 'dsl_ys': dsl_ys, 'new_dsl_ys': new_dsl_ys, 'values': values, 'select_new_ys': select_new_ys})
        
        infos.append({'step': step, 'dsl_ys': dsl_ys, 'new_dsl_ys': new_dsl_ys, 'values': values, 'select_new_ys': select_new_ys})

        i = len(select_new_ys) - 1
        while i >= 0:
            if 'complete' in select_new_ys[i]:
                num_selected_sample -= 1
                complete_dsls.append(select_new_ys.pop(i))
                complete_grids.append(select_new_state.pop(i))
                complete_objects.append(select_new_object.pop(i))
                complete_corrects.append(select_corrects.pop(i))
            i -= 1

        dsl_ys = select_new_ys
        state_ys = select_new_state
        object_ys = select_new_object
        new_dsl_ys = []

        if num_selected_sample == 0:
            break
    
    if to_print: 
        print(f"dsl_ys: {dsl_ys}, state_ys: {state_ys}")
    return dsl_ys, {'steps': infos}, tatal_result_log
