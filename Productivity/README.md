# Productivity
## Directory Structure
```
├─GPT_DATA: contains codes for experiments.
|
├─HF_Augmented_Data: contains all of the experimental results.
|
├─visualization: contains visualization files for results.
```


## Explanation about Python Codes
```GPT_DATA/GPT3.5_prompt.py```: augments example inputs with GPT-3.5.

```GPT_DATA/GPT4.0_prompt.py```: augments example inputs with GPT-4.

```GPT_DATA/GPT_prompt.py```: generates prompts for Inverse Transformation Prompting (ITP).

```GPT_DATA/hand_filter.py```: removes inadequate results with heuristic rules.


## Quick Start
```
python GPT_DATA/GPT_prompt.py
python GPT_DATA/GPT3.5_prompt.py or python GPT_DATA/GPT4.0_prompt.py
python GPT_DATA/hand_filter.py
```

## What is Productivity?
We conduct experiments using ARC tasks to understand how well LLMs can generate new expressions based on inherent logical concepts. 
Productivity involves two main steps: inferring specific rules for generating images from example images and natural language expressions and using those rules to generate new, unseen images. 
However, solving ARC tasks, experimented on in the previous sections so far, is unsuitable for confirming these two processes.
For precise evaluation, we propose a new experiment: _Given an ARC task and a basic rule shared with similar ARC tasks, can LLMs generate valid examples of the given task?_ 
If LLMs can understand a relationship between the given ARC task and the abstract rule, they should be able to infer specific rules for the given task and generate new valid examples. 
Through this, we want to see if LLMs can imitate human thinking productivity.


## How to Experiment to Evaluate the Productivity of LLM?
1. Guessing input data by some characteristics in ARC Problem
2. Augmentation Process

![overall_process_productivity_page-0001](https://github.com/GIST-DSLab/ARC_Prompt/assets/22788924/d4cefef0-b6df-4141-8751-6893ebf8bea4)

Prompt(역변환 방법 프롬프트) is written for each Task (Concept ARC has 16 Tasks)

* dotted input(pink and green one) is augmentation target.
* Chat GPT makes other inputs that are suitable to the given output

  i. Make prompt file(Prompt.json) with GPT_prompt.py
  
  ii. Use GPT API (GPT3.5_prompt.py / GPT4.0_prompt.py) to make augmented data
  
  iii. Choose only appropriate results by hand_filter.py


If you want to use this method with other prompts, you may change the prompt in GPT_prompt.py

3. Code File(GPT_DATA) to augment Concept ARC

   i. GPT3.5_prompt.py

     This file is using GPT-3.5 API to make ARC examples

   ii. GPT4.0_prompt.py

     This file is using GPT-4.0 API to make ARC examples

   iii. GPT_prompt.py

     This code is making prompt json file

      * You should change this file if you would like to change prompt.

   iv. Prompt.json

     This json file is that I have used to augment concept.

     This json file is composed of input, output, task(Concept ARC Task e.g. AboveBelow, Center,...), result, test_input and test_output.

     1) input: input data from concept ARC(train)
     2) output: output data from concept ARC(train)
     3) task: task name from concept ARC
     4) result: this array is for complement from chat-GPT, which means it is okay to be empty.
     5) test_input: this array is just for deliver to Result file(to adapt ARC interface) <- this array is not so important
     6) test_output: this array is just for deliver to Result file(to adapt ARC interface) <- this array is not so important


## Results
|Problem Category|Total available|The number of generated data|The number of valid augmentated data|Ratio(valid/generated)|
|:---:|:---:|:---:|:---:|:---:|
|[Above Below](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/AboveBelow.pdf)|58|158|34|21.52%|
|[Center](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/Center.pdf)|65|236|35|14.83%|
|[Clean Up](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/CleanUp.pdf)|106|183|83|45.36%|
|[Complete Shape](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/CompleteShape.pdf)|58|147|37|25.17%|
|[Copy](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/Copy.pdf)|27|153|4|2.61%|
|[Count](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/Count.pdf)|56|202|29|14.36%|
|[Extend To Boundary](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/ExtendToBoundary.pdf)|37|167|8|4.79%|
|[Extract Objects](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/ExtractObjects.pdf)|44|176|21|11.93%|
|[Filled Not Filled](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/FilledNotFilled.pdf)|58|203|29|14.29%|
|[Horizontal Vertical](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/HorizontalVertical.pdf)|32|114|7|6.14%|
|[Inside Outside](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/InsideOutside.pdf)|52|191|24|12.57%|
|[Move To  Boundary](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/MoveToBoundary.pdf)|36|165|12|7.27%|
|[Order](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/Order.pdf)|47|162|26|16.05%|
|[Same Different](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/SameDifferent.pdf)|107|246|76|30.89%|
|[Top Bottom 2D](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/TopBottom2D.pdf)|92|255|59|23.14%|
|[Top Bottom 3D](https://github.com/GIST-DSLab/Augmentation_with_GPT/blob/main/visualization/TopBottom3D.pdf)|55|215|25|11.63%|
|Total|930|2913|509|17.12%|


## Etc
We modify [tanchongmin's code](https://github.com/tanchongmin/ARC-Challenge) to make the visualization code and use it to visualize the ARC grid. 
