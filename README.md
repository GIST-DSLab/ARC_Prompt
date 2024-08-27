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

3. Set environment variables.
```
export AZURE_OPENAI_API_KEY="REPLACE_WITH_YOUR_KEY_VALUE_HERE"
export AZURE_OPENAI_ENDPOINT="REPLACE_WITH_YOUR_ENDPOINT_HERE"
export AZURE_OPENAI_DEPLOYMENT_NAME="REPLACE_WITH_YOUR_DEPLOYMENT_NAME_HERE"
```
4. Clone this repository & install the required packages.
```
git clone https://github.com/GIST-DSLab/ARC_Prompt.git
cd ARC_Prompt
pip install -r requirements.txt
```
5. Follow **Quick Start** instructions for each experiment.
   1) [Logical Coherence](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Logical_Coherence/README.md#quick-start)
   2) [Compositionality](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Compositionality/README.md#quick-start)
   3) [Productivity](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Productivity/README.md#quick-start)


## [Logical Coherence](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Logical_Coherence)

### Comparison Across Prompting Techniques
The accuracy is based on solving 100 random
ARC tasks with CoT, LtM, and ToT prompts, each repeated 5 times. The accuracy outside the parentheses
refers to the accuracy when only the results are correct, while the accuracy inside the parentheses indicates
the accuracy when both the results and the process are correct.

<div align="center">
  
|Iteration|Chain of thought|Least to Most|Tree of Thoughts|
|:---:|:---:|:---:|:---:|
|1|11%(3%)|6%(4%)|7%(3%)|
|2|10%(2%)|7%(4%)|4%(1%)|
|3|10%(5%)|6%(3%)|7%(2%)|
|4|10%(4%)|4%(2%)|7%(4%)|
|5|10%(6%)|5%(2%)|6%(2%)|

</div>

### Inferential Coherence of LLMs

We conducted five repeated experiments using CoT on 400 tasks from the ARC Training set. Then, for the tasks that were answered correctly at least once, we augmented 100 problems using re-arc and measured Inferential Coherence, repeating this experiment five times. The results are shown in the figure below

![3 1_cdf-1](https://github.com/user-attachments/assets/80c3c380-4aac-43c6-9742-bdcc8b2fb7d0)|![3 1_pdf-1](https://github.com/user-attachments/assets/f9a372e4-f36c-47c4-acb7-b88a03520358)|
---|---|



<!--
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
-->

## [Compositionality](https://github.com/GIST-DSLab/ARC_Prompt/tree/master/Compositionality)

### LLM DSL understanding 

The result of LLM DSL understaing experiment is 81% using weighted average accuracy with the number of tasks at each step as weight as shown in the equation.

$$
p = \frac{\sum_{n=1}^{10} w_n \cdot a_n}{\sum_{n=1}^{10} w_n}
$$

In this equation, $$\textbf{p}$$ refers to the single-step accuracy, $$w_n$$ represents the number of tasks at step $$\textbf{n}$$, and $$a_n$$ represents the accuracy at step $$\textbf{n}$$. Based on this, we estimated the single-step accuracy to be 81%.

### Main Compoaitionality

To measure the compositionality of the LLM, experiments were conducted on 158 tasks. The results, based on whether the test output and human description were provided, are shown in the table below.


<div align="center">
   
|      | w/o Human Description     | w/ Human Description  | 
|:-----:|:-----:|:-----:|
| w/o Test Output     | 2%(5%)        | 8%(15%)      | 
| w/ Test Output    | 9%(17%)       | 14%(29%)     | 

</div>

The above table is the average accuracy from 10 repeated experiment based on the presence or absence of test output and human descriptions. The accuracy values in parentheses are the estimates obtained when LLMs understand the given DSL perferctly. We make the equation to estimate the result if LLM understand the given DSL perfectly.

$$
y = \frac{\sum_{n=1}^{10} w_n \cdot (p \cdot x)^n}{\sum_{n=1}^{10} w_n}
$$

In this equation, $$\textbf{n}$$ represents the number of steps, $$w_n$$ denotes the number of problems at step $$\textbf{n}$$, $$\textbf{p}$$ refers to the single-step accuracy, specifically the 0.81 performance obtained from LLM DSL understanding experiment, and $$\textbf{x}$$ indicates the difficulty of the problem. We assumed that the difficulty of the problem can vary depending on the information provided to the LLMs.


<!--
The accuracy is based on solving the problems in the training set, 260 questions with the same input/output dimensions, with ToT prompts and DSLs.
<div align="center">
  
|          | Entry | Easy  | Medium | Hard  | Etc   | Total |
|:--------:|:-----:|:-----:|:------:|:-----:|:-----:|:-----:|
| Tasks    | 5     | 152    | 65     | 10    | 28    | 260    |
| Correct  | 0     | 1     | 0      | 0     | 1     | 2     |
| Accuracy | 0.000% | 0.006% | 0.000%  | 0.000% | 0.036% | 0.008% |

</div>
-->

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

