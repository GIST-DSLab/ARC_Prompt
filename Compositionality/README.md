# Compositionality
## Directory Structure
```
├─arc_reult: contains results and preprocessed data for CoT, LtM, and ToT.
|
├─arc_reult_12: ???????????????????????????????????????????????????????????
|
├─arc_reult(task-5,step-4,gen-5,eval-1,sel-3): ???????????????????????????????????????????????????????????
|
├─arc_reult copy: ???????????????????????????????????????????????????????????
|
├─tot
|  ├─data: contains ???????????????????????????????????????????????????????????
|  ├─methods: contains a code for prompting techniques such as generation, vote, parsing, and regularization parser.
|  ├─prompts: contains a prompt code used when each prompting technique generates suggestions or evaluates value.
|  ├─tasks: contains codes that manage ARC tasks and their prompts.
```


## Explanation about Python Codes
```prototype_arc.py```: solves ARC tasks with ToT.

```quickly_start.py```: ???????????????????????????????????????????????????????????


## Quick Start
The following minimal script will attempt to solve ARC tasks (it might be a bit slow as it's using GPT-4):
```
cd Compositionality
python prototype_arc.py
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


## An Example Result for One Task
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
