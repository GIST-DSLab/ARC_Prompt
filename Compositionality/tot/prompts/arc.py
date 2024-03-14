# TODO prompt 내용 넣기
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
# TODO prompt 내용 넣기
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

# TODO prompt 내용 넣기
propose_prompt = '''Given an instruction and several choices, decide which choice is most promising. Analyze each choice in detail, then conclude in the last line "The best choice is {s}", where s the integer id of the choice.
'''

# TODO prompt 내용 넣기
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

Used DSLs:
{used_dsls}

Current_state(Changed by DSLs):
{current_state}

Evaluate the Current_state to solve this quiz(sure/maybe/impossible):
'''

#########################################################################
# TODO prompt 내용 넣기
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

Used DSLs:
{used_dsls}

Current_state:
{current_state}

According to the current state, and DSLs you have used, what will be the next DSL to solve the problem?
Select one DSL in each step with proper arguments.

I want you to answer the format is below
Don't make space between arguments.
- DSL name (with the arguments for the DSL):
- Description (Why you choose this DSL?):
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

What is the first DSL to solve the problem?
Select one DSL in each step with proper arguments.

I want you to answer the format is below.
Don't make space between arguments.
- DSL name (with the arguments for the DSL):
- Description (Why you choose this DSL?):

'''
#########################################################################
# TODO prompt 내용 넣기
dsl_cot_prompt = '''
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
DSL list

{dsl_list}
=========

{examples}

Quiz:
{quiz}

Current_state:
{y}
'''