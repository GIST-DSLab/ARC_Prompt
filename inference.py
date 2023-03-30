import os
import openai
import jsonlines
import pandas as pd
from dotenv import load_dotenv
import time
from transformers import GPT2Tokenizer
from tqdm import tqdm

load_dotenv()

openai.organization = "org-D9qOzGt4FPdshUSreOCpEyXZ"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"
prompt_sentence = []
label_sentence = []
data = []
count = 0

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

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

for prompt, label in tqdm(zip(prompt_sentence, label_sentence)):
    label_len = len(label)
    max_tokens = label_len
    count += 1

    try:
        len_prompt_tokens = len(tokenizer(prompt)['input_ids'])
    except:
        except_count += 1
        continue

    if len_prompt_tokens > 1500:
        except_count += 1
        continue

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

