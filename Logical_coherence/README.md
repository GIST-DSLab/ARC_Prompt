# Logical coherence


## Directory structure
```
├─reult: 
| The result directory contains results and preprocessed data for Chain of Thought, Least to Most, and Tree of Thoughts. 
|
├─tot
|  ├─methods
| The methods directory has tot process code such as generation, vote, parsing and regularization  parser.
|  ├─prompts
| The prompts directory has prompts code that used when tot generate suggestion or evaluate value.
|  ├─tasks 
| The tasks directory has code that manage arc tasks and their prompts.
```

## Explanation about python code files

```arr_result.py```: This code seperate arc tasks following categorization from [ARC-Game](https://github.com/volotat/ARC-Game) and calculate the result about csv files that created by ```cot_solver.py```, ```ltm_solver.py```, ```tot_arc_solver.py```.

```cot_making_prompt.py```: This code make some prompt that used when LLM solve ARC tasks with chain of thought method.

```cot_solver.py```: This code solve ARC tasks with chain of thought.

```ltm_decomposing.py```: This code decompose the tasks to solve step-by-step by LLM.

```ltm_making_prompt.py```: This code generate prompt that used when LLM decompose the task to solve step-by-step.

```ltm_making_prompt_CoT.py```: This code generate prompt with chain of thought that used when LLM decompose the task to solve step-by-step.

```ltm_metric.py```: This code preprocess the result that made by ```ltm_solver.py```.

```tot_arc_solver.py```: This code solve ARC tasks with tree of thoughts.

```utils.py```: This code include visualization function that used when visualization.py call.

```visualization.py```: This code visualize the result about csv files that created by ```cot_solver.py```, ```ltm_solver.py```, ```tot_arc_solver.py```.

## Setup
1. Set up Azure OpanAI API key and write down api_key variable in the code
  
2. Write down api_base variable in the code

3. Install package
```
git clone https://github.com/GIST-DSLab/ARC_Prompt.git
cd ARC_Prompt
pip install -r requirements.txt
```
## Quick Start
1. Chain of thought
```
python cot_making_prompt.py
python cot_solver.py
```
2. Least to Most
```
python ltm_making_prompt.py or python ltm_makin_prompt_CoT.py
python ltm_decomposing.py
python ltm_solver.py
```
3. Tree of Thoughts
```
python tot_arc_solver.py
```
## What is the logical coherence?
**Logical coherence is the ability to understand a given logic and apply it consistently across different
contexts.** This concept is crucial in human cognitive processes as it facilitates the construction of
sentence structures based on consistent logic, which is essential for solving various tasks. Such
an ability is particularly relevant to the rule inference required in ARC tasks, where the challenge
is to identify common logical patterns among given examples and use them to deduce the most
logically coherent answer.

## How to conduct an experiment to evaluate the logical coherence of LLM?
To evalute the logical coherence of LLM with ARC tasks, We used a various prompt techniques such as chain of thought, least to most and tree of t thoughts

Below figures explain all of the process.

<img src="https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/132a2cf7-c10c-4756-8093-22e524fadf70"  width="50%" height="50%"/>

Three types of prompts are shown on the left. Although all prompts are described as a 2D array of
grids, we visualized them on the right for clarity. In default, all three techniques use prompts with two main
components: a sample task and a target task. However, LtM and ToT use a different combination of the target
task and its decomposition command. This deviation occurs because CoT strictly follows the given sub-task,
while LtM and CoT decompose the task on their own.

<img src="https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/01a1283f-e81e-434f-9af1-1d2467eb0cc7"  width="50%" height="50%"/>

Grey blocks illustrate prompt sets delivered to the LLM, including the sample task, target task, and
LLM’s prior responses, as shown in Fig. 8. Green blocks denote the final answer. CoT relies on a single grey
block, indicating that the LLM strictly follows the provided sub-tasks. Conversely, LtM and ToT prompt
the LLM to generate and address sub-tasks sequentially, represented by decomposed results (red) and
intermediate responses (blue). ToT further distinguishes itself from LtM by evaluating multiple suggestions
for sub-task handling and selecting the most effective one through a voting mechanism.


# result
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
