
## Compositionality
This experiment part is conducted to determine the compositionality of the LLM using given DSLs.
DSLs are given by \tot\data\prototype_arc\dsl.txt with python-coded.
DSLs and tasks are given by \tot\prompts\arc.py
In \tot\tasks\arc.py, ARCTask make LLM to generate answer. And ARCEnv apply the chosen dsl to current state and object.
You can add your api in \tot\models.py.

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
The following minimal script will attempt to solve the arc (might be a bit slow as it's using GPT-4):
```python
import argparse
from tot.methods.bfs import arc_solve
from tot.tasks.arc import ARCTask
import json
import os
import time

args = argparse.Namespace(backend='tot3', temperature=0.7, task='arc', naive_run=False, prompt_sample='standard', method_generate='sample', method_evaluate='value', method_select='greedy', n_generate_sample=3, n_evaluate_sample=1, n_select_sample=1)

task = ARCTask()
for i in range(0, 98):
    if not os.path.exists('arc_result'):
        os.mkdir('arc_result')
    ys, infos = arc_solve(args, task, i)
    with open(f'arc_result/{i}.json', 'w') as f:
        json.dump(infos, f, indent=4)
    # if len(ys)>=1:
    #     print(ys[0])  ##This is to print out the output for each step
```
You can set your step number in \tot\tasks\arc.py, ARCTask self.steps and self.stops (Please set the same number)

## Result (for one task)
```json
{
    "steps": [
        {
            "step": 0,
            "dsl_ys": [
                ""
            ],
            "new_dsl_ys": [
                "obj_color(state, object1, 2)",
                "obj_color(state, object1, 2)"
            ],
            "values": [
                20.0,
                20.0
            ],
            "select_new_ys": [
                "obj_color(state, object1, 2)",
                "obj_color(state, object1, 2)"
            ]
        },
        {
            "step": 1,
            "dsl_ys": [
                "obj_color(state, object1, 2)",
                "obj_color(state, object1, 2)"
            ],
            "new_dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)"
            ],
            "values": [
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "select_new_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)"
            ]
        },
        {
            "step": 2,
            "dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)"
            ],
            "new_dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)"
            ],
            "values": [
                0.001,
                0.001,
                0.001,
                0.001,
                0.001
            ],
            "select_new_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)"
            ]
        },         
        {
            "step": 3,
            "dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)"
            ],
            "new_dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)"
            ],
            "values": [
                20.0,
                20.0,
                20.0,
                20.0
            ],
            "select_new_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)"
            ]
        },
        {
            "step": 4,
            "dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)"
            ],
            "new_dsl_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)"
            ],
            "values": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "select_new_ys": [
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)",
                "obj_color(state, object1, 2)->obj_color(state, object2, 2)->obj_color(state, object3, 2)->obj_color(state, object4, 2)->obj_color(state, object5, 2)"
            ]
        }
    ]
}
```
