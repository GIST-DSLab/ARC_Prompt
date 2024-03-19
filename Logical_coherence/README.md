# Logical coherence


## Directory structure
```
├─data
|  ├─training: contains JSON files for ARC training tasks.
|  ├─evaluation: contains JSON files for ARC evaluation tasks.
|
├─result: contains results and preprocessed data for each trial for each prompting technique.
|
├─tot
|  ├─methods: contains a code for prompting techniques such as generation, vote, parsing, and regularization parser.
|  ├─prompts: contains a prompt code used when each prompting technique generates suggestions or evaluates value.
|  ├─tasks: contains codes that manage ARC tasks and their prompts.
```


## Explanation about Python codes

```acc_result.py```: classifies ARC tasks by difficulty from [ARC-Game](https://github.com/volotat/ARC-Game) and calculate results with csv files.

```cot_making_prompt.py```: generates prompts for ```cot_solver.py```.

```cot_solver.py```: solves ARC tasks with CoT.

```ltm_decomposing.py```: decomposes ARC tasks into small step-by-step sub-tasks.

```ltm_making_prompt.py```: generates prompts for decomposing ARC tasks into sub-tasks.

```ltm_making_prompt_CoT.py```: generates prompts for solving ARC tasks with generated sub-tasks.

```ltm_metric.py```: preprocesses the result that made by ```ltm_solver.py```.

```ltm_solver.py```: solves ARC tasks with LtM.

```metric.py```: ???????????????????????????????????????????????????

```tot_arc_solver.py```: solves ARC tasks with ToT.

```utils.py```: includes visualization functions for ```visualization.py```.

```visualization.py```: visualizes results.


## Quick Start
1. Chain of Thought ([CoT](https://arxiv.org/abs/2201.11903))
```
python cot_making_prompt.py
python cot_solver.py
```
2. Least to Most ([LtM](https://arxiv.org/abs/2205.10625))
```
python ltm_making_prompt.py or python ltm_makin_prompt_CoT.py
python ltm_decomposing.py
python ltm_solver.py
```
3. Tree of Thoughts ([ToT](https://arxiv.org/abs/2305.10601))
```
python tot_arc_solver.py
```


## What is the logical coherence?
**Logical coherence is the ability to understand a given logic and to apply it consistently across different
contexts.** 
This concept is crucial in human cognitive processes as it facilitates the construction of sentence structures based on consistent logic, which is essential for solving various tasks. 
Such an ability is particularly relevant to the rule inference required in ARC tasks, where the challenge is to identify common logical patterns among given examples and use them to deduce the most logically coherent answer.


## How to experiment to evaluate the logical coherence of LLM?
To evaluate the logical coherence of LLM with ARC tasks, We used various prompt techniques such as CoT, LtM, and ToT.

The below figures explain the process.

<img src="https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/132a2cf7-c10c-4756-8093-22e524fadf70"  width="50%" height="50%"/>

Three types of prompts are shown on the left. 
Although all prompts are described as a 2D array of grids, we visualized them on the right for clarity. 
By default, all three techniques use prompts with two main components: a sample task and a target task. 
However, LtM and ToT use a different combination of the target task and its decomposition command. 
This deviation occurs because CoT strictly follows the given sub-task, while LtM and CoT decompose the task on their own.

<img src="https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/01a1283f-e81e-434f-9af1-1d2467eb0cc7"  width="50%" height="50%"/>

Grey blocks illustrate prompt sets delivered to the LLM, including the sample task, target task, and LLM’s prior responses, as shown in the above figure. 
Green blocks denote the final answer. CoT relies on a single grey block, indicating that the LLM strictly follows the provided sub-tasks. 
Conversely, LtM and ToT prompt the LLM to generate and address sub-tasks sequentially, represented by decomposed results (red) and intermediate responses (blue). 
ToT further distinguishes itself from LtM by evaluating multiple suggestions for sub-task handling and selecting the most effective one through a voting mechanism.


## Results
The accuracy is based on solving 100 random ARC tasks with CoT, LtM, and ToT prompts, each repeated 5 times. 
The accuracy outside the parentheses refers to the accuracy when only the results are correct, while the accuracy inside the parentheses indicates the accuracy when both the results and the process are correct.

<div align="center">
  
|Iteration|Chain of thought|Least to Most|Tree of Thoughts|
|:---:|:---:|:---:|:---:|
|1|11%(3%)|6%(4%)|7%(3%)|
|2|10%(2%)|7%(4%)|5%(1%)|
|3|10%(5%)|6%(3%)|7%(2%)|
|4|10%(4%)|4%(2%)|7%(4%)|
|5|12%(6%)|5%(2%)|6%(2%)|

</div>

Analyzing LLMs’ reasoning capabilities by task difficulty, following prior categorization from [ARC-Game](https://github.com/volotat/ARC-Game). 
The number of ARC tasks corresponding to each category is listed in the table, and the experiment was performed 5 times for each task.

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

## Etc
We modify [tanchongmin's code](https://github.com/tanchongmin/ARC-Challenge) to make the visualization code and use it to visualize the ARC grid. 
