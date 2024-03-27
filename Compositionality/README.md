# Compositionality
## Directory Structure
```
├─arc_result: contains results that consist of every step with selected DSLs
|
├─data: contains JSONL file for ARC tasks and TXT file for DSLs
|
├─model
|  ├─methods: contains a code for prompting techniques such as generation, vote, parsing, and regularization parser.
|  ├─prompts: contains a prompt code used when each prompting technique generates suggestions or evaluates value.
|  ├─tasks: contains codes that manage ARC tasks and their prompts.
```


## Explanation about Python Codes
```tot_arc_solver.py```: solves ARC tasks with ToT.

```Pnp.py```: Detects the object for each ARC tasks' input grid.

More explanation is in this paper : [Unraveling the ARC Puzzle: Mimicking Human Solutions with Object-Centric Decision Transformer](https://openreview.net/forum?id=F9QfmL6IjZ)


## Quick Start
0. Check environment variables & move to the compositionality directory.
```
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_DEPLOYMENT_NAME

cd Compositionality
```
1. Run ARC solver.
```
python obj_create.py
python tot_arc_solver.py
```
2. Apply result dsls to generate expected output grids.
```
python output_grid.py
```
3. Visualize result.
```
python visualize.py
```
4. Check visualization results (HTML files) that are located in each subdirectory of the result directory.
```
xdg-open result/result_correct.html
xdg-open result/result_incorrect.html
```
5. Move to the origin directory.
```
cd ..
```

## What is Compositionality?
**Compositionality refers to the ability to generate complex linguistic expressions using simpler ones.** 
This characteristic allows individuals to effectively tackle more complex tasks by breaking sub-tasks down into simpler steps, supporting the notion that humans can solve more complex tasks when faced with them. 
Strong compositionality enables the resolution of complex tasks and facilitates transparent descriptions of the process, which is also an important aspect from the perspective of LLMs. 
This section tests compositionality by treating ARC tasks as stepwise compositions of simpler functions.


## How to Experiment to Evaluate Compositionality of LLM?
The experiment is conducted to determine the compositionality of the LLM using given DSLs.
DSLs are given by ```tot\data\prototype_arc\dsl.txt``` with python-coded.
DSLs and tasks are given by ```tot\prompts\arc.py```.
In ```tot\tasks\arc.py```, the ARCTask class makes LLM generate an answer and the ARCEnv class applies the chosen DSL to the current state and object.
You can add your API in ```tot\models.py```.

The below figures represent all of the processes of the experiment.

<img src="https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/9fd63bba-acaf-427b-9c20-6e2a4cb32d70"  width="100%" height="100%"/>
 Since LLMs correctly understand the innated rules in DSLs, LLM generates valid outputs with required actions such as coloring, rotating, drawing a line, and flipping when we give information about DSL, current state, and object.

</br>
</br>

<img src="https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/c3bf3d8b-91e4-4a43-b613-a3608aacbeac"  width="100%" height="100%"/>
 An example of the single step in an experimental process. 
 The LLM solver observes the current state and chooses the DSL from the list. Then, the LLM validator evaluates the selected DSLs by score. 
 Based on the score, the top two states are sent to the next step.


## Results
The accuracy is based on solving 99 random ARC tasks with ToT prompt and DSL. These tasks are included in Logical_Coherence experiment. 

<div align="center">
  
|| Entry     | Easy     | Medium  | Hard   |
|:-----:|:-----:|:-----:|:-----:|:-----:|
| Tasks     | 2        | 19      | 46     | 14      |
| Correct     | 0        | 0      | 3     | 0      |
| ToT       | 0.00%   | 0.00%  | 6.52%  | 0.00%   |

</div>

## Etc
We modify [tanchongmin's code](https://github.com/tanchongmin/ARC-Challenge) to make the visualization code and use it to visualize the ARC grid. 
