# Reasoning Abilities of Large Language Models: In-Depth Analysis on the Abstraction and Reasoning Corpus
This repository is the experiment code for "Reasoning Abilities of Large Language Models: In-Depth Analysis on the Abstraction and Reasoning Corpus"

> [Reasoning Abilities of Large Language Models: In-Depth Analysis on the Abstraction and Reasoning Corpus](https://arxiv.org/abs/2403.11793) </br>
> </br>
> Seungpil Lee, Woochang Sim, Donghyeon Shin, Sanha Hwang, Wongyu Seo, Jiwon Park, Seokki Lee, Sejin Kim, Sundong Kim

The existing methods for evaluating the inference abilities of Large Language Models (LLMs) have been result-centric,
making it difficult to assess the inference process. We introduce a new approach using the Abstract
and Reasoning Corpus (ARC) dataset to evaluate the inference and contextual understanding abilities of large
language models in a process-centric manner. ARC demands rigorous logical structures for problem-solving,
making it a benchmark that facilitates the comparison of model inference abilities with humans. Experimental
results confirm that while large language models possess weak inference abilities, they still lag in terms of
logical coherence, compositionality, and productivity. Our experiments highlight the reasoning capabilities of
LLMs, proposing development paths for achieving human-level reasoning.

![1710421234908-a8370feb-4cad-4839-bc28-138199ff19ad_1](https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/e69669f2-2046-40e3-982f-ff909eabc7a9)


## Setup
1. Follow instructions from [Create and deploy an Azure OpenAI Service resource](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource?pivots=web-portal).

2. Follow instructions from [Quickstart: Get started using GPT-35-Turbo and GPT-4 with Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Cpython&pivots=programming-language-python).

3. Set environment variables
```
export AZURE_OPENAI_API_KEY="REPLACE_WITH_YOUR_KEY_VALUE_HERE"
export AZURE_OPENAI_ENDPOINT="REPLACE_WITH_YOUR_ENDPOINT_HERE"
export AZURE_OPENAI_DEPLOYMENT_NAME="REPLACE_WITH_YOUR_DEPLOYMENT_NAME_HERE"
```
4. Clone this repo and install packages in **requirements.txt** with the following code.
```
git clone https://github.com/GIST-DSLab/ARC_Prompt.git
cd ARC_Prompt
pip install -r requirements.txt
```
5. Follow the instructions for each part of the experiment.
   1) [Logical Coherence](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Logical_Coherence)
   2) [Compositionality](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Compositionality)
   3) [Productivity](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Productivity)

## [Logical Coherence](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Logical_Coherence)
The accuracy is based on solving 100 random
ARC tasks with CoT, LtM, and ToT prompts, each repeated 5 times. The accuracy outside the parentheses
refers to the accuracy when only the results are correct, while the accuracy inside the parentheses indicates
the accuracy when both the results and the process are correct.

<div align="center">
  
|Iteration|Chain of thought|Least to Most|Tree of Thoughts|
|:---:|:---:|:---:|:---:|
|1|11%(3%)|6%(4%)|7%(3%)|
|2|10%(2%)|7%(4%)|5%(1%)|
|3|10%(5%)|6%(3%)|7%(2%)|
|4|10%(4%)|4%(2%)|7%(4%)|
|5|12%(6%)|5%(2%)|6%(2%)|

</div>

Analyzing LLMs’ reasoning capabilities by task difficulty, following prior categorization from [ARC-Game](https://github.com/volotat/ARC-Game). The
number of ARC tasks corresponding to each category is listed in the table, and the experiment was performed
5 times for each task.

<div align="center">
  
|| Entry     | Easy     | Medium  | Hard   |
|:-----:|:-----:|:-----:|:-----:|:-----:|
| Tasks     | 2        | 20      | 46     | 14      |
| Trials    | 10       | 100     | 230    | 70      |
| CoT       | 100.00%  | 30.00%  | 0.00%  | 0.00%   |
| LtM       | 20.00%   | 19.00%  | 0.00%  | 2.85%   |
| ToT       | 50.00%   | 22.00%  | 0.00%  | 0.00%   |
| Average | 56.67% | 23.67% | 0.00% | 0.95% |

</div>

If you want to get more detail about logical coherence, please refer to [this link](./Logical_Coherence/).

## [Compositionality](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Compositionality)
The experiment results are as follows: out of 99 tasks, LLM was not able to solve
any tasks. 

If you want to get more detail about compositionality, please refer to [this link](./Compositionality).

## [Productivity](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Productivity)
Based on 160 ARC tasks classified by [ConceptARC](https://github.com/victorvikram/ConceptARC), we evaluated the validity of a
total of 2,913 generated examples.

|Problem Category|Total available|The number of generated data|The number of valid augmentated data|Ratio(valid/generated)|
|:---:|:---:|:---:|:---:|:---:|
|Above Below|58|158|34|21.52%|
|Center|65|236|35|14.83%|
|Clean Up|106|183|83|45.36%|
|Complete Shape|58|147|37|25.17%|
|Copy|27|153|4|2.61%|
|Count|56|202|29|14.36%|
|Extend To Boundary|37|167|8|4.79%|
|Extract Objects|44|176|21|11.93%|
|Filled Not Filled|58|203|29|14.29%|
|Horizontal Vertical|32|114|7|6.14%|
|Inside Outside|52|191|24|12.57%|
|Move To  Boundary|36|165|12|7.27%|
|Order|47|162|26|16.05%|
|Same Different|107|246|76|30.89%|
|Top Bottom 2D|92|255|59|23.14%|
|Top Bottom 3D|55|215|25|11.63%|
|Total|930|2913|509|17.12%|

If you want to get more detail about compositionality, please refer to [this link](./Productivity).

## Citation
If you find this repo useful for your research, please consider citing our paper:
```
@misc{lee2024reasoning,
      title={Reasoning Abilities of Large Language Models: In-Depth Analysis on the Abstraction and Reasoning Corpus}, 
      author={Seungpil Lee and Woochang Sim and Donghyeon Shin and Sanha Hwang and Wongyu Seo and Jiwon Park and Seokki Lee and Sejin Kim and Sundong Kim},
      year={2024},
      eprint={2403.11793},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

