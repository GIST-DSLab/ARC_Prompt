import os
import openai
import backoff 
import time
import re
import json
import tiktoken
from model.errors import ParseError
import ast

# Set variable realted the azure openai.
model_name = "gpt-4o"
openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")

completion_tokens = prompt_tokens = 0

encoder = tiktoken.encoding_for_model(model_name)

# Call the OpenAI API
# @backoff.on_exception(backoff.expo, openai.error.OpenAIError, max_tries=9)
@backoff.on_exception(backoff.expo, openai.error.OpenAIError)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

def gpt(prompt, assistant_prompt=None, model="gpt-4", temperature=0.7, max_tokens=4096 , n=1, stop=None, mode=None, step=None) -> list:
    try:
        messages = [{"role": "user", "content": prompt}] if assistant_prompt is None else [{"role": "user", "content": prompt}, {"role": "assistant", "content": assistant_prompt}]
    except Exception as e:
        raise Exception(f"Error: {e}")
    return tot_chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop, mode=mode, step=step)
    
def tot_chatgpt(messages, model="gpt-4", temperature=0.7, max_tokens=4096 , n=1, stop=None, mode=None, step=None) -> list:
    global completion_tokens, prompt_tokens
    total_outputs = []
    outputs = []
    use_total_output_index = []
    temp_list = []
    num_tokens_input_list = []
    num_tokens_output_list = []
    num_tokens_total_list = []
    index = 0
    fail_count = 0

    time_out = 15 * 60
    start_time = time.time()

    while n > 0:
        cnt = min(n, 20)
        res = completions_with_backoff(engine=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
        total_outputs.extend([choice["message"]["content"] for choice in res["choices"]])
        num_tokens_input_list.append(len(encoder.encode(('').join([message['content'] for message in messages]))))
        num_tokens_output_list.append(len(encoder.encode(('').join([choice["message"]["content"] for choice in res["choices"]]))))
        num_tokens_total_list.append(num_tokens_input_list[-1] + num_tokens_output_list[-1])

        # TODO output
        for choice in res["choices"]:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > time_out:
                raise Exception(f"Timeout: {elapsed_time} seconds")

            json_flag = False
            if 'step' in choice["message"]["content"] and 'description' in choice["message"]["content"] and ('dsl' in choice["message"]["content"] or 'value' in choice["message"]["content"]):
                pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)
                matches = pattern.findall(choice["message"]["content"])
                for match in matches:
                    try:
                        match = match.replace("step:", "step")
                        match = match.replace("dsl:", "dsl") if mode == 'sample' else match.replace("value:", "value")
                        match = match.replace("description:", "description")

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
                                        fail_count += 1
                                        if fail_count > 10:
                                            raise Exception(f"Fail counts: {fail_count}. Failed to generate the output.")
                                        break

                        if mode == 'sample':
                            if 'dsl' not in parsed_log.keys() or 'step' not in parsed_log.keys():
                                continue
                        elif mode == 'value':
                            if 'value' not in parsed_log.keys() or 'step' not in parsed_log.keys() or 'value' not in parsed_log.keys():
                                continue

                        if parsed_log['step'] == 'complete':
                            parsed_log['step'] = step
                        else:
                            parsed_log['step'] = int(parsed_log['step'])

                        if parsed_log['step'] == step:
                            json_flag = True
                            break

                    except json.JSONDecodeError as e:
                        pass
                if json_flag:
                    outputs.append(choice["message"]["content"])
                    n -= 1
                    use_total_output_index.append(index)
                    index += 1

        # TODO finish reqson이 length나 다른 경우도 있을텐데 어떻게 처리할까?

        # TODO 원하는 step까지 생성이 안되었을 경우 어떻게 할까?

        if num_tokens_input_list[-1] >= 127_000:
            raise Exception(f"Input tokens exceed the limit: {num_tokens_input_list[-1]}")

    return outputs, messages, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, total_outputs, use_total_output_index

def cot_chatgpt(prompt, step, assistant_prompt=None, timeout=120, model="gpt-4", temperature=0.7, max_tokens=4096, n=1, stop=None, use_env=False, mode='solver', excluding_complete_step=False) -> list:
    messages = [{"role": "user", "content": prompt}]
    if assistant_prompt is not None:
        messages.append({"role": "assistant", "content": assistant_prompt})

    global completion_tokens, prompt_tokens
    outputs = []
    fail_count = 0
    prev_message = ""
    first_fail_flag = True
    success_flag = False
    num_tokens_input_list = []
    num_tokens_output_list = []
    num_tokens_total_list = []
    parsed_logs = []

    while True:
        try:
            res = completions_with_backoff(engine=model, messages=messages, temperature=temperature, max_tokens=max_tokens,n=n, stop=stop, timeout=timeout)
        except openai.error.OpenAIError as e:
            print(f"OpenAI API call failed: {e}")

        choices = res['choices']

        # Append each choice's message to outputs
        outputs.extend([choice["message"]["content"] for choice in choices])

        num_tokens_input_list.append(len(encoder.encode(('').join([message['content'] for message in messages]))))
        num_tokens_output_list.append(len(encoder.encode(('').join([choice["message"]["content"] for choice in choices]))))
        num_tokens_total_list.append(num_tokens_input_list[-1] + num_tokens_output_list[-1])

        # Check the finish reason
        finish_reason = choices[0]['finish_reason']
        if finish_reason == 'stop' or fail_count >= step+1:
            pattern = re.compile(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', re.DOTALL)
            matches = pattern.findall(" ".join(outputs))
            for match in matches:
                try:
                    if use_env:
                        if mode == 'solver':
                            if 'step' not in match or 'dsl' not in match:
                                continue

                            match = match.replace('\'', '"')
                            match = match.replace("step:", "step")
                            match = match.replace("dsl:", "dsl")

                            if 'description' in match:
                                match = match.replace("description:", "description")

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
                                            continue

                            if 'dsl' not in parsed_log.keys() or 'step' not in parsed_log.keys():
                                continue

                            if 'step' in parsed_log.keys():
                                if 'complete' in parsed_log['step']:
                                    parsed_log['step'] = parsed_logs[-1]['step'] + 1
                                else:
                                    parsed_log['step'] = int(parsed_log['step'])

                            if not excluding_complete_step:
                                if 'complete' in parsed_log['dsl']:
                                    parsed_logs.append(parsed_log)
                                    success_flag = True
                                    break

                            # TODO 이전 step과 동일한 step을 또 생성하면 어떻게 처리를 해줘야 하나?
                            if parsed_log['step'] in [current['step'] for current in parsed_logs]:
                                continue
                        elif mode == 'question':
                            match = match.replace('\'', '"')
                            match = match.replace("next_dsl_is_complete:", "next_dsl_is_complete")
                            match = match.replace("need_more_steps:", "need_more_steps")
                            match = match.replace("how_much_steps_do_you_need:", "how_much_steps_do_you_need")

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
                                            continue

                            parsed_logs.append(parsed_log)
                            success_flag = True
                            break
                    else:
                        if 'step' not in match:
                            continue
                        if 'grid' not in match:
                            raise json.JSONDecodeError('grid key not in match', match, 0)
                        parsed_log = json.loads(match.replace("'", '"'))

                    parsed_logs.append(parsed_log)
                except json.JSONDecodeError as e:
                    pass

            if mode=='solver' and parsed_logs == [] or parsed_logs[-1]['step'] < step and success_flag==False:
                if prev_message == choices[0]['message']['content']:
                    success_flag = False
                    break
                else:
                    prev_message = choices[0]['message']['content']
                    if use_env:
                        add_assistant_message = "\n!!!You need to consistently generate DSL based on the text (DSL) you previously created to solve the problem. Therefore, you must refer to what you generated earlier when selecting the subsequent DSL. You must continue generating DSL until you reach 10 steps or select the 'complete' DSL.!!!"
                    else:
                        add_assistant_message = "\n!!!Continue Generate!!!"
                    messages.append({"role": "assistant", "content": choices[0]["message"]["content"]+add_assistant_message})
                    input_tokens = len(encoder.encode(('').join([message['content'] for message in messages])))

                    if first_fail_flag and parsed_logs != []:
                        first_fail_flag = False
                        step_count = 1
                        if parsed_logs[-1]['step'] == str:
                            step_count = parsed_logs[-1]['step'].lower().split('step')[1] if 'step' in parsed_logs[-1]['step'].lower() else int(parsed_logs[-1]['step'])
                        elif parsed_logs[-1]['step'] == int:
                            step_count = parsed_logs[-1]['step']
                        fail_count = step_count
                    else:
                        fail_count += 1
                    print(f"*** Failed to parse the output. Fail counts is {fail_count}.***")
                    print(f"*** Output: {choices[0]['message']['content']} ***")

                    if fail_count >= step+1 or input_tokens >= 127_000:
                        success_flag = False
                        break
            elif mode=='solver' and parsed_logs[-1]['step'] > step:
                parsed_logs = [target for target in parsed_logs if target['step'] <= step]
                success_flag = True
                break
            else:
                success_flag = True
                break

        elif finish_reason == 'length':
            # Append the last part of the generated text as new input and continue generating
            messages.append({"role": "assistant", "content": choices[0]["message"]["content"]})

            input_tokens = len(encoder.encode(('').join([message['content'] for message in messages])))
            fail_count += 1
            if input_tokens >= 127_000:
                success_flag = False
                break
        else:
            fail_count += 1
    if use_env:
        return outputs, finish_reason, choices, messages, success_flag, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list, parsed_logs
    else:
        return outputs, finish_reason, choices, messages, success_flag, num_tokens_input_list, num_tokens_output_list, num_tokens_total_list
