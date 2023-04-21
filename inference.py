import os
import openai
import jsonlines
import pandas as pd
from dotenv import load_dotenv
import time
from transformers import GPT2Tokenizer
from tqdm import tqdm

load_dotenv()

#openai.organization = ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#openai.api_key = "키 값을 넣어주세요"
prompt_sentence = []
label_sentence = []
data = []
count = 0

# GPT2 tokenizer를 사용하는 이유는 비용을 계산하기 위함 -> OpenAI API는 token 당 돈을 내야하기 때문.
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# 아래의 evaluation_dataset.jsonl에 inference하고자한 데이터셋의 파일명을 넣으면 된다. 해당 데이터셋의 format은 prompt와 completion을 key로 갖는 dictionary
# 형태의 JSON LIST(jsonl) 이어야 한다.
with jsonlines.open('evaluation_dataset.jsonl') as read_file:
    for line in read_file.iter():
        data.append(line)

prompt_sentence = [x['prompt'] for x in data]
label_sentence = [x['completion'] for x in data]

using_prompt_sentence = []
using_label_sentence = []
prediction_list = []
except_count = 0
using_count = 0
all_tokens = 0
error_list = []

# 아래의 for문이 OpenAI의 API를 이용하여 inference하는 과정이다.
for prompt, label in tqdm(zip(prompt_sentence, label_sentence)):
    label_len = len(label)
    max_tokens = label_len
    count += 1
    
    #아래의 try-except구문은 OpenAI의 API에서 제한한 최대 token 수를 넘는 data를 skip해주기 위한 용도이다.
    #이때 1500이라는 값을 len_prompt_tokens과 비교해주는데 1500은 개인적으로 정한 임의의 숫자이며 실제 OpenAI의 API에서는 query로 날린 prompt의 token의 수와 결과로 받을
    #completion(model의 output 결과)의 token 수가 합쳐서 대략 2100을 넘기면 안된다.
    #정리하자면 아래의 구문은 prompt가 1500 token 이하만 사용하기 위한 용도이다.
    #아래의 구문이 없다면 inference과정 중 오류가 발생할 것이다.
    try:
        len_prompt_tokens = len(tokenizer(prompt)['input_ids'])
    except:
        except_count += 1
        continue

    if len_prompt_tokens > 1500:
        except_count += 1
        continue

    # 아래의 openai.Completion.create는 해당 모델에게 prompt를 던졌을때 결과를 얻기 위해서 API를 호출하는 부분으로 
    # try-except 구문으로 감싸준 이유는 위에서 prompt의 token수와 아래의 completion(response의 completion)의 token 수의 합이 대략 2100이상이며 오류를 발생시키므로
    # 이것을 방지하기 위해서 try-except을 해준 것이다.
    try:
        response = openai.Completion.create(
            model='davinci:ft-graduated-student:arcsolver-davinci-v2-2023-03-28-15-21-33',
            prompt=prompt,
            temperature=0,
            max_tokens=max_tokens,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n"]
        )
    except:
        error_list.append(count)
        except_count += 1
        continue

    prediction_list.append(response['choices'][0]['text'])
    all_tokens += len_prompt_tokens
    using_prompt_sentence.append(prompt)
    using_label_sentence.append(label)
    using_count += 1

    if all_tokens/1000*0.12 >= 15 or using_count == 100:
        break

df = pd.DataFrame({
    "prompt":using_prompt_sentence,
    "prediction": prediction_list,
    "label": using_label_sentence
})
df.to_csv('prediction.csv', index=None)

a = pd.read_csv('prediction.csv')
b = a['prediction']
c = a['label']

count = 0
for pred, label in zip(b,c):
    if pred == label:
        count += 1

print(f'accuracy: {count/len(b)}')
print(f'except_count: {except_count}')
print(f'cost: ${all_tokens/1000*0.12}')
print(f'사용할 수 있는 데이터 개수: {using_count}')

with open('error_count_log.txt', 'w') as f:
    f.write(f'{error_list}')


# print(response)

# with open('prediction.', 'w') as f:
#     f.write(response['choices'][0]['text'])

# print(openai.Model.list())

