import os
import openai
import backoff 
import time

# Set variable realted the azure openai.  
openai.api_type = "azure"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 

completion_tokens = prompt_tokens = 0

# Call the OpenAI API
@backoff.on_exception(backoff.expo, openai.error.OpenAIError)
def completions_with_backoff(**kwargs):
    time.sleep(15)
    return openai.ChatCompletion.create(**kwargs)

def gpt(prompt, model="gpt-4", temperature=0.7, max_tokens=4096 , n=1, stop=None) -> list:
    messages = [{"role": "user", "content": prompt}]
    return chatgpt(messages, model=model, temperature=temperature, max_tokens=max_tokens, n=n, stop=stop)

def chatgpt(messages, model="gpt-4", temperature=0.7, max_tokens=4096 , n=1, stop=None) -> list:
    global completion_tokens, prompt_tokens
    outputs = []
    temp_list = []
    while n > 0:
        cnt = min(n, 20)
        n -= cnt
        res = completions_with_backoff(engine=model, messages=messages, temperature=temperature, max_tokens=max_tokens, n=cnt, stop=stop)
        outputs.extend([choice["message"]["content"] for choice in res["choices"]])

    return outputs
