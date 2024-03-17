
## Compositionality
## Directory structure
```
├─arc_reult: 
| The result directory contains results and preprocessed data for Chain of Thought, Least to Most, and Tree of Thoughts.
├─arc_reult_12: 
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
```prototype_arc.py```: This code solve ARC tasks with tree of thoughts.

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
```
python prototype_arc.py
```

## What is the compositionality?
**Compositionality refers to the ability to generate complex linguistic expressions using simpler ones.** This characteristic allows individuals to effectively tackle more complex tasks by breaking sub-tasks down into simpler steps, supporting the notion that humans can solve more complex tasks when faced with them. Strong compositionality enables the resolution of complex tasks and facilitates transparent descriptions of the process, which is also an important aspect from the perspective of LLMs. This section tests compositionality by treating ARC tasks as stepwise compositions of simpler functions.

## How to experiment evaluate the logical coherence of LLM?
So, this experiment part is conducted to determine the compositionality of the LLM using given DSLs.
DSLs are given by ```tot\data\prototype_arc\dsl.txt``` with python-coded.
DSLs and tasks are given by ```tot\prompts\arc.py```.
In ```tot\tasks\arc.py```, ARCTask make LLM to generate answer. And ARCEnv apply the chosen dsl to current state and object.
You can add your api in ```tot\models.py```.

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
