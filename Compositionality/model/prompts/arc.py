###########################################
# ARC + ARC example + test
standard_prompt = '''
Do you know ARC problem?

ARC is quiz and if we can solve this problem we understand and utilize several concepts such like 'object', 'count', 'color', 'move', 'row', 'column' and etc.
And ARC problem give you some example to understand these patterns.
So you can understand below pattern with several examples and then apply quiz's input to get right output.

=========

{examples}

Quiz:
{quiz}
'''
###########################################
# DSL definition and example usage
dsl_prompt = '''
To solve ARC problem, you can use DSLs below.

{dsl_list}

Arguments for the DSLs are mainly 'state' and 'object', but some requires 'color', 'row', 'column' and etc.
'state' is the current state of the grid, which is the entire grid.
'object' is the list of coordinates of the object, there may be multiple numbers of objects in the grid, but no DSL requires multiple objects.
'color' is the color of the pixel in the grid, which is the number between 0 to 9.
'row' and 'column' are the coordinate number of a pixel in the grid.

You can choose from here and apply DSL to solve the problem.

Here are the usage of DSLs and the reuslt.

In this example grid,
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0], 
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0], 
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5], 
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0], 
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

there are 6 objects
Object 1
[[1, 7], [1, 8], [2, 7], [2, 8]]
Object 2
[[2, 1], [2, 2], [3, 2], [3, 3]]
Object 3
[[5, 9], [6, 9], [7, 9]]
Object 4
[[6, 5], [6, 6]]
Object 5
[[7, 1], [8, 1]]
Object 6
[[8, 4], [9, 3], [9, 4]] 

The value of the grid is a color value that is between 0 to 9.
The value of the object is a list of coordinates of the object.


1.
Applying 'rotate_right_obj(state, object2)' with arguments,
state = [[],[],[],[],[],[],[],[],[]]

object = object2

the result becomes
[[],[],[],[],[],[],[],[],[]].

2.
Applying 'horizontal_flip' with arguments,

3.

4.

5.

6.


'''

###########################################
cot_prompt = '''
Do you know ARC problem?

It is similary below.

=========

Example 1

If input grids are like that
[[0, 3, 0, 0, 0, 0], [0, 3, 0, 2, 0, 0], [0, 0, 0, 2, 0, 0], [0, 8, 0, 0, 2, 2], [0, 0, 0, 0, 2, 2], [6, 6, 6, 0, 0, 0]],
then this grids change to output grids below
[[0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 3, 2], [0, 0, 0, 0, 0, 2], [0, 0, 0, 8, 2, 2], [0, 0, 0, 0, 2, 2], [0, 0, 0, 6, 6, 6]].

=========

You can understand the pattern of this problem with input-output pair about example1.
In above case, you can inference like below.

In example 1 case, all obejct move right. So if given input is below,
[[0, 3, 0, 0, 0, 0], [0, 3, 0, 2, 0, 0], [0, 0, 0, 2, 0, 0], [0, 8, 0, 0, 2, 2], [0, 0, 0, 0, 2, 2], [6, 6, 6, 0, 0, 0]],
then you can move object to right side.
[[0, 0, 0, 0, 3, 0], [0, 0, 0, 0, 3, 2], [0, 0, 0, 0, 0, 2], [0, 0, 0, 8, 2, 2], [0, 0, 0, 0, 2, 2], [0, 0, 0, 6, 6, 6]].

Like this concept, 'object', 'count', 'color', 'move', 'row', 'column' and etc, helps you to understand patterns of problem and solve it.

Below problem is other pattern to solve. So you can understand below pattern with several examples and apply quiz's input to get right output.

=========

{examples}

Quiz:
{quiz}

Current_state:
{y}
'''

propose_prompt = '''Given an instruction and several choices, decide which choice is most promising. Analyze each choice in detail, then conclude in the last line "The best choice is {s}", where s the integer id of the choice.
'''

value_prompt = '''
Do you know ARC problem?

ARC is quiz and if we can solve this problem we understand and utilize several concepts such like 'object', 'count', 'color', 'move', 'row', 'column' and etc.
And ARC problem give you some example to understand these patterns.
So you can understand below pattern with several examples and then apply quiz's input to get right output.

=========
{dsl_list}
=========

{examples}

{quiz}
=========
Below are the value information from the history of your previous evaluation. 
(If the current step is 1, there will be no history record.)

{previous_values}
=========
The information below consists of various details that indicate the current state.

Current step:
{current_step}

Used DSLs:
{used_dsls}

Current_state(Changed by DSLs):
{current_state}

Current_objects_information(Changed by DSLs):
{current_objects}

========
[Mission]

Evaluate the Current_state to solve this quiz(sure/maybe/impossible):
'''

#########################################################################
dsl_standard_prompt = '''
Do you know ARC problem?

ARC is a quiz and if we can solve this problem we understand and utilize several concepts such like 'object', 'count', 'color', 'move', 'row', 'column' and etc.
And ARC problem give you some example to understand these patterns.
So you can understand below pattern with several examples and then apply quiz's input to get right output.

=========
{dsl_list}
=========

Arguments for the DSLs are mainly 'state' and 'object', but some requires 'color', 'row', 'column' and etc.
'state' is the current state of the grid, which is the entire grid.
'object' is the list of coordinates of the object, there may be multiple numbers of objects in the grid, but no DSL requires multiple objects.
'color' is the color of the pixel in the grid, which is the number between 0 to 9.
'row' and 'column' are the coordinate number of a pixel in the grid.

The coordinates of the grid start from (0,0).
So, when there is a grid like [[0,0], [7,0]], the coordinate of 7 is (1,0).

You can choose from here and apply DSL to solve the problem.
You must input the according arguments to the DSL or it will not work.

=========

DSL Usage Examples:

In this example grid,
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0], 
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0], 
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5], 
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0], 
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

there are 6 objects
Object1
[[1, 7], [1, 8], [2, 7], [2, 8]]
Object2
[[2, 1], [2, 2], [3, 2], [3, 3]]
Object3
[[5, 9], [6, 9], [7, 9]]
Object4
[[6, 5], [6, 6]]
Object5
[[7, 1], [8, 1]]
Object6
[[8, 4], [9, 3], [9, 4]] 


If you apply "rotate_right_obj(state, object2)", the result becomes
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 5, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5],
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5],
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0],
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

If you apply "diagonal_line(state, 1, 1, 9, 9, 3)", the reusult becomes
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 3, 0, 0, 0, 0, 5, 5, 0],
[0, 0, 5, 3, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 3, 0, 0, 0, 5],
[0, 0, 0, 0, 0, 5, 3, 0, 0, 5],
[0, 5, 0, 0, 0, 0, 0, 3, 0, 5],
[0, 5, 0, 0, 5, 0, 0, 0, 3, 0],
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

If you apply, obj_color(state, object3, 7), the result becomes
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0]
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0]
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 7]
[0, 0, 0, 0, 0, 5, 5, 0, 0, 7]
[0, 5, 0, 0, 0, 0, 0, 0, 0, 7]
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0]
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]

Please choose the DSL from the list above and provide the proper arguments to solve the problem.
=========

{examples}

{quiz}

You must solve the given quiz within 10 steps!

Current step:
{current_step}

Used DSLs:
{used_dsls}

Current_state(Changed by DSLs):
{current_state}

Current_objects_information(Changed by DSLs):
{current_objects}

According to the current state, and DSLs you have used, what will be the next DSL to solve the problem?
Select one DSL in each step with proper arguments.

I want you to answer the format is below
Don't make space between arguments.

If you think the current state is correct, you can select the "complete" DSL.

The step starts at 1, and you need to write the appropriate DSL for the current step and the reason for selecting it in the following JSON format.

Such like below
{{
    'step': "{current_step}",
    'dsl': "(dsl with the arguments for the DSL)",
    'description': "(why you chose this DSL?)"
}}

All keys in the JSON should be enclosed in single quotes ('')
All values in the JSON should be enclosed in double quotes ("")
In the content of the description value, you must not use single quotes (') or double quotes (").

In this case, the step is fixed, so you only need to create the dsl and description.
'''
#########################################################################
dsl_standard_init_prompt = '''
Do you know ARC problem?

ARC is a quiz and if we can solve this problem we understand and utilize several concepts such like 'object', 'count', 'color', 'move', 'row', 'column' and etc.
And ARC problem give you some example to understand these patterns.
So you can understand below pattern with several examples and then apply quiz's input to get right output.

=========
{dsl_list}
=========

Arguments for the DSLs are mainly 'state' and 'object', but some requires 'color', 'row', 'column' and etc.
'state' is the current state of the grid, which is the entire grid.
'object' is the list of coordinates of the object, there may be multiple numbers of objects in the grid, but no DSL requires multiple objects.
'color' is the color of the pixel in the grid, which is the number between 0 to 9.
'row' and 'column' are the coordinate number of a pixel in the grid.

The coordinates of the grid start from (0,0).
So, when there is a grid like [[0,0], [7,0]], the coordinate of 7 is (1,0).

You can choose from here and apply DSL to solve the problem.
You must input the according arguments to the DSL or it will not work.

=========

DSL Usage Examples:

In this example grid,
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0], 
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0], 
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5], 
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0], 
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

there are 6 objects
Object1
[[1, 7], [1, 8], [2, 7], [2, 8]]
Object2
[[2, 1], [2, 2], [3, 2], [3, 3]]
Object3
[[5, 9], [6, 9], [7, 9]]
Object4
[[6, 5], [6, 6]]
Object5
[[7, 1], [8, 1]]
Object6
[[8, 4], [9, 3], [9, 4]] 


If you apply "rotate_right_obj(state, object2)", the result becomes
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 5, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5],
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5],
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0],
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

If you apply "diagonal_line(state, 1, 1, 9, 9, 3)", the reusult becomes
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 3, 0, 0, 0, 0, 5, 5, 0],
[0, 0, 5, 3, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 3, 0, 0, 0, 5],
[0, 0, 0, 0, 0, 5, 3, 0, 0, 5],
[0, 5, 0, 0, 0, 0, 0, 3, 0, 5],
[0, 5, 0, 0, 5, 0, 0, 0, 3, 0],
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

If you apply, obj_color(state, object3, 7), the result becomes
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0]
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0]
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 7]
[0, 0, 0, 0, 0, 5, 5, 0, 0, 7]
[0, 5, 0, 0, 0, 0, 0, 0, 0, 7]
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0]
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]

Please choose the DSL from the list above and provide the proper arguments to solve the problem.
=========

{examples}

Quiz:
{quiz}

You must solve the given quiz within 10 steps!

Current step:
{current_step}

What is the first DSL to solve the problem?
Select one DSL with proper arguments in each step.

I want you to answer the format is below.
Don't make space between arguments.

If you think the current state is correct, you can select the "complete" DSL.

The step starts at 1, and you need to write the appropriate DSL for the current step and the reason for selecting it in the following JSON format.

Such like below
{{
    'step': "{current_step}",
    'dsl': "(dsl with the arguments for the DSL)",
    'description': "(why you chose this DSL?)"
}}

All keys in the JSON should be enclosed in single quotes ('')
All values in the JSON should be enclosed in double quotes ("")
In the content of the description value, you must not use single quotes (') or double quotes (").
'''
#########################################################################
dsl_cot_prompt = '''
Do you know ARC problem?

ARC is a quiz and if we can solve this problem we understand and utilize several concepts such like 'object', 'count', 'color', 'move', 'row', 'column' and etc.
And ARC problem give you some example to understand these patterns.
So you can understand below pattern with several examples and then apply quiz's input to get right output.

=========
{dsl_list}
=========

Arguments for the DSLs are mainly 'state' and 'object', but some requires 'color', 'row', 'column' and etc.
'state' is the current state of the grid, which is the entire grid.
'object' is the list of coordinates of the object, there may be multiple numbers of objects in the grid, but no DSL requires multiple objects.
'color' is the color of the pixel in the grid, which is the number between 0 to 9.
'row' and 'column' are the coordinate number of a pixel in the grid.

The coordinates of the grid start from (0,0).
So, when there is a grid like [[0,0], [7,0]], the coordinate of 7 is (1,0).

You can choose from here and apply DSL to solve the problem.
You must input the according arguments to the DSL or it will not work.

=========

DSL Usage Examples:

In this example grid,
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0], 
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0], 
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5], 
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5], 
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0], 
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

there are 6 objects
Object1
[[1, 7], [1, 8], [2, 7], [2, 8]]
Object2
[[2, 1], [2, 2], [3, 2], [3, 3]]
Object3
[[5, 9], [6, 9], [7, 9]]
Object4
[[6, 5], [6, 6]]
Object5
[[7, 1], [8, 1]]
Object6
[[8, 4], [9, 3], [9, 4]] 


If you apply "rotate_right_obj(state, object2)", the result becomes
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 5, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
[0, 0, 0, 0, 0, 5, 5, 0, 0, 5],
[0, 5, 0, 0, 0, 0, 0, 0, 0, 5],
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0],
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

If you apply "diagonal_line(state, 1, 1, 9, 9, 3)", the reusult becomes
[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0],
[0, 5, 3, 0, 0, 0, 0, 5, 5, 0],
[0, 0, 5, 3, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 3, 0, 0, 0, 5],
[0, 0, 0, 0, 0, 5, 3, 0, 0, 5],
[0, 5, 0, 0, 0, 0, 0, 3, 0, 5],
[0, 5, 0, 0, 5, 0, 0, 0, 3, 0],
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

If you apply, obj_color(state, object3, 7), the result becomes
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 5, 5, 0]
[0, 5, 5, 0, 0, 0, 0, 5, 5, 0]
[0, 0, 5, 5, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
[0, 0, 0, 0, 0, 0, 0, 0, 0, 7]
[0, 0, 0, 0, 0, 5, 5, 0, 0, 7]
[0, 5, 0, 0, 0, 0, 0, 0, 0, 7]
[0, 5, 0, 0, 5, 0, 0, 0, 0, 0]
[0, 0, 0, 5, 5, 0, 0, 0, 0, 0]

Please choose the DSL from the list above and provide the proper arguments to solve the problem.
=========

{examples}

Quiz:
{quiz}

You must solve the given quiz within 10 steps!

Select one DSL with proper arguments in each step.

I want you to answer the format is below.
Don't make space between arguments.

If you think the current state is correct, you can select the "complete" DSL.

The output should be in the following JSON format:

such like below
{{
    'step': "(current_step)",
    'dsl': "(dsl with the arguments for the DSL)",
    'description': "(why you chose this DSL?)"
}}

All keys in the JSON should be enclosed in single quotes ('')
All values in the JSON should be enclosed in double quotes ("")
In the content of the description value, you must not use single quotes (') or double quotes (").
'''

add_info = '''
==========================
[Additional Information]

The information below is helpful for solving this problem. Use this information to select the appropriate DSL to solve the problem.

{add_info}

==========================
'''

test_output_info = '''
==========================
[Test output]

The test grid for the test input is as follows. 

Test Output:
{test_output}

Now you have both test input information and test output information. Based on this, generate(or select) the expected DSL and the necessary parameters step-by-step to transform the grid from the test input to the test output.

==========================
'''

cot_format_prompt = """
You must clearly state the name of the DSL function you will use and provide a description of why you chose that particular DSL. 
When selecting the DSL function name, be sure to include not only the function but also the arguments that will go into it. 
Refer to the provided DSL functions list and include the appropriate DSL arguments. 
For DSL functions involving objects, such as move_right, move_left, move_up, move_down, rotate_right_obj, rotate_left_obj, vertical_flip_obj, horizontal_flip_obj, and obx_color, do not include the object's coordinates. 
Instead, use the object names from the provided objects list.

And you can select the DSL function only one time for each step.

The output should be in the following JSON format:

{
    'step': "(current_step)",
    'dsl': "(dsl with the arguments for the DSL)",
    'description': "(why you chose this DSL?)"
}

All keys in the JSON should be enclosed in single quotes ('')
All values in the JSON should be enclosed in double quotes ("")
In the content of the description value, you must not use single quotes (') or double quotes (").

Step number starts from 1. So, If you want to use the DSL function for the first step, you should write "step": "1".

If you think the current state is correct, you can select the "complete" DSL.

I repeat, for functions that use objects, you must not provide arguments in the form of coordinates! 
You must use the key values from the provided object information!

Make sure to follow these instructions!
"""

sample_format_prompt = """
You must clearly state the name of the DSL function you will use and provide a description of why you chose that particular DSL. 
When selecting the DSL function name, be sure to include not only the function but also the arguments that will go into it. 
Refer to the provided DSL functions list and include the appropriate DSL arguments. 
For DSL functions involving objects, such as move_right, move_left, move_up, move_down, rotate_right_obj, rotate_left_obj, vertical_flip_obj, horizontal_flip_obj, and obx_color, do not include the object's coordinates. 
Instead, use the object names from the provided objects list.

And you can select the DSL function only one time for each step.

The output should be in the following JSON format:

{{
    'step': "{current_step}",
    'dsl': "(dsl with the arguments for the DSL)",
    'description': "(why you chose this DSL?)"
}}

All keys in the JSON should be enclosed in single quotes ('')
All values in the JSON should be enclosed in double quotes ("")
In the content of the description value, you must not use single quotes (') or double quotes (").

In this case, the step is fixed, so you only need to create the dsl and description.

If you think the current state is correct, you can select the "complete" DSL.

I repeat, for functions that use objects, you must not provide arguments in the form of coordinates! 
You must use the key values from the provided object information!

Make sure to follow these instructions!
"""

value_format_prompt = """
Evaluate whether the current state is appropriate to solve the ARC problem within 10 steps using the given information (DSL List, Current step, Used DSL, Current_state, Current_objects_information). 
If the likelihood of solving is very high, rate it as 'sure'; 
if uncertain, rate it as 'maybe'; 
and if unlikely, rate it as 'impossible'.

The output should be in the following JSON format:

{{
    'step': "{current_step}",
    'value': "(sure/maybe/impossible)",
    'description': "(why you chose this DSL?)"
}}

All keys in the JSON should be enclosed in single quotes ('')
All values in the JSON should be enclosed in double quotes ("")
In the content of the description value, you must not use single quotes (') or double quotes (").

In this case, the step is fixed, so you only need to create the dsl and description.

I repeat, for functions that use objects, you must not provide arguments in the form of coordinates! 
You must use the key values from the provided object information!

Make sure to follow these instructions!
"""

reuse_value_format_prompt = """
{{
    'step': {current_step},
    'grid': "{current_grid}',
    'value': (sure/maybe/impossible),
}}
"""

complete_question_prompt = """
You attempted to solve the test (Quiz) within 10 steps using the DSL list information and example pair information provided below.

The DSL list information, examples, and quiz(test) are as follows.

=========
[DSL List information]
{dsl_list}
=========
[Example pair information]
{examples}
=========
[Quiz information]
{quiz}
=========
[Objects infromation for the quiz]
{object}
=========
At this point, to solve the quiz (test) within 10 steps, you selected the necessary DSL and its parameters for each step as follows. 

{history}

However, now at the 10th step, you have not pressed "complete" yet. 

Will the problem be solved in the next step? 
In other words, will you press "complete" in the next step? Or do you need more steps to solve this problem?

Answer this as follows:

{{
    'next_dsl_is_complete': (True if you plan to use the complete DSL in the next step, otherwise False),
    'need_more_steps': (True if more steps are needed, otherwise False if it can be solved within 10 steps),
    'how_much_steps_do_you_need': (an integer indicating how many more steps are needed if more steps are required, or 0 if no more steps are needed)
}}
"""

complete_question_format_prompt = '''
{{
    'next_dsl_is_complete': (True if you plan to use the complete DSL in the next step, otherwise False),
    'need_more_steps': (True if more steps are needed, otherwise False if it can be solved within 10 steps),
    'how_much_steps_do_you_need': (an integer indicating how many more steps are needed if more steps are required, or 0 if no more steps are needed)
}}
'''