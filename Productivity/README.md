# Augmentation_with_GPT

What I did: Augmenting Concept ARC Problem

How to augment
1. Guessing input data by some characteristics in ARC Problem

<img width="603" alt="스크린샷 2023-11-20 143112" src="https://github.com/GIST-DSLab/Augmentation_with_GPT/assets/126467193/7cd459d7-0cfa-49aa-81f9-7b4ea71e943a">

2. Augmentation Process

<img width="1033" alt="스크린샷 2023-10-30 165149" src="https://github.com/GIST-DSLab/Augmentation_with_GPT/assets/126467193/06d91890-7855-4d8c-8aae-1718605553e4">

Prompt(역변환 방법 프롬프트) is written for each Task (Concept ARC has 16 Tasks)

* dotted input(pink and green one) is augmentation target.
* Chat GPT makes other inputs which is suitable to given output

  i. Make prompt file(Prompt.json) with GPT_prompt.py
  
  ii. Use GPT API (GPT3.5_prompt.py / GPT4.0_prompt.py) to make Augmented DATA
  
  iii. I have chosen appropriate input by hand_filter.py


If you want to use this method with other prompt, you may change prompt in GPT_prompt.py

3. Code File(GPT_DATA) to augment Concept ARC

   i. GPT3.5_prompt.py

     This file is using GPT-3.5 API to make ARC Demonstration

   ii. GPT4.0_prompt.py

     This file is using GPT-4.0 API to make ARC Demonstration

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


## Result Table
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

      
   v. hand_filter.py
   
   this python file is that I've used to filter inadequate data.
