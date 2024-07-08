import re
import os
import sympy
import pandas as pd
from model.tasks.base import Task
from model.prompts.arc import * 
import json
import copy
import re
import ast

class ARCEnv:
    def __init__(self, dsl_file='dsl.txt'):
        self.dsl_list = ''
        with open(os.path.join('data', dsl_file), 'r', encoding='utf-8') as f:
            self.dsl_list = f.read()

    
    # rotate_left_state function is a counterclockwise rotation about the given state. Only for square not rectengular.
    def rotate_left_state(self, state, objects):
        N = len(state)
        rotated_state = copy.deepcopy(state)
        new_objects={}
        if N == len(state[0]):
            for x in range(N):
                for y in range(N):
                    rotated_state[N-1-y][x] = state[x][y]
            for object in objects: 
                new_obj=[]
                try:
                    for [x, y] in object: # 이 부분에서 object가 objects[object]로 되어야지 오류가 발생하지 않을 것 같음 - 지원님/석기님한테 물어보기
                        new_x=N-1-y
                        new_y=x
                        new_obj.append([new_x, new_y])
                    new_objects[object]=new_obj
                except:
                    rotated_state, new_objects = state, objects # 위의 부분처럼하면 오류가 발생하기 때문에 state 및 object의 변화를 주지 않기 위해서
            return rotated_state, new_objects

    # rotate_right_state function is a clockwise rotation about the given state. Only for square not rectengular.
    def rotate_right_state(self, state, objects):
        N = len(state)
        rotated_state = copy.deepcopy(state)
        new_objects={}
        if N == len(state[0]):
            for x in range(N):
                for y in range(N):
                    rotated_state[y][N-1-x] = state[x][y]
            for object in objects:
                new_obj=[]
                for [x, y] in objects[object]:
                    new_x=y
                    new_y=N-1-x
                    new_obj.append([new_x, new_y])
                new_objects[object]=new_obj
            
            return rotated_state, new_objects

    # vertical_flip function is a flip by x-axis about the given state.
    def vertical_flip(self, state, objects):
        temp_state = copy.deepcopy(state)
        N = len(state)
        M = len(state[0])
        for  i in range(N):
            for j in range(M):
                temp_state[N-1-i][j] = state[i][j]
        new_objects={}
        for object in objects:
            new_obj=[]
            for [x, y] in objects[object]:
                new_x=N-1-x
                new_y=y
                new_obj.append([new_x, new_y])
            new_objects[object]=new_obj
        return temp_state, new_objects

    # horizontal_flip function is a flip by y-axis about the given state.
    def horizontal_flip(self, state, objects):
        N = len(state)
        M = len(state[0])
        temp_state = copy.deepcopy(state)

        for i in range(N):
            for j in range(M):
                temp_state[i][M-1-j] = state[i][j]
        new_objects={}
        for object in objects:
            new_obj=[]
            for [x, y] in objects[object]:
                new_x=x
                new_y=M-1-y
                new_obj.append([new_x, new_y])
            new_objects[object]=new_obj
        return temp_state, new_objects
    
    # move right all pixels in the selected object.
    def move_right(self, state, obj, objects):
        move_state = copy.deepcopy(state)
        new_obj=[]
        
        for x, y in obj:
            move_state[x][y] = 0
        for x, y in obj:
            new_x, new_y = x, y + 1
            if 0 <= new_x < len(state) and 0 <= new_y < len(state[0]):
                move_state[new_x][new_y] = state[x][y]
                new_obj.append([new_x, new_y])
        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
        
        return move_state, objects

    # move left all pixels in the selected object.
    def move_left(self, state, obj, objects):
        move_state = copy.deepcopy(state)
        new_obj=[]
        
        for x, y in obj:
            move_state[x][y] = 0
        for x, y in obj:
            new_x, new_y = x, y - 1
            if 0 <= new_x < len(state) and 0 <= new_y < len(state[0]):
                move_state[new_x][new_y] = state[x][y]
                new_obj.append([new_x, new_y])
        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
            
        return move_state, objects

    # move up all pixels in the selected object.
    def move_up(self, state, obj, objects):
        move_state = copy.deepcopy(state)
        new_obj=[]
        
        for x, y in obj:
            move_state[x][y] = 0
        for x, y in obj:
            new_x, new_y = x-1, y
            if 0 <= new_x < len(state) and 0 <= new_y < len(state[0]):
                move_state[new_x][new_y] = state[x][y]
                new_obj.append([new_x, new_y])
        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
                
        return move_state, objects

    # move down all pixels in the selected object.
    def move_down(self, state, obj, objects):
        move_state = copy.deepcopy(state)
        new_obj=[]
        
        for x, y in obj:
            move_state[x][y] = 0
        for x, y in obj:
            new_x, new_y = x+1, y
            if 0 <= new_x < len(state) and 0 <= new_y < len(state[0]):
                move_state[new_x][new_y] = state[x][y]
                new_obj.append([new_x, new_y])
            
        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
        return move_state, objects

    # make a clockwise rotation about the given object.
    def rotate_right_obj(self, state, obj, objects):
        rotate_state = copy.deepcopy(state)
        new_obj=[]
        max_x = max(x for x, _ in obj)
        min_x = min(x for x, _ in obj)
        max_y = max(y for _, y in obj)
        min_y = min(y for _, y in obj)
            
        fixed_x=(max_x+min_x)//2
        fixed_y=(max_y+min_y)//2
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                rotate_state[x][y] = 0 
                
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                moved_x = y - fixed_y + fixed_x
                moved_y = -x + fixed_x + fixed_y
                if 0 <= moved_x < len(state) and 0 <= moved_y < len(state[0]):
                    rotate_state[moved_x][moved_y] = state[x][y]
                    new_obj.append([moved_x, moved_y])

        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
                
        for x in range(len(state)):
            for y in range(len(state[0])):
                state[x][y] = rotate_state[x][y]
            
        return state, objects

    # make a counterclockwise rotation about the given object.
    def rotate_left_obj(self, state, obj, objects):
        rotate_state = copy.deepcopy(state)
        new_obj=[]
        max_x = max(x for x, _ in obj)
        min_x = min(x for x, _ in obj)
        max_y = max(y for _, y in obj)
        min_y = min(y for _, y in obj)
            
        fixed_x=(max_x+min_x)//2
        fixed_y=(max_y+min_y)//2
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                rotate_state[x][y] = 0 

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                moved_x = -y + fixed_y + fixed_x
                moved_y = x - fixed_x + fixed_y
                if 0 <= moved_x < len(state) and 0 <= moved_y < len(state[0]):
                    rotate_state[moved_x][moved_y] = state[x][y]
                    new_obj.append([moved_x, moved_y])

        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
        for x in range(len(state)):
            for y in range(len(state[0])):
                state[x][y] = rotate_state[x][y]
            
        return state, objects

    # make a vertical flip of the selected object
    def vertical_flip_obj(self, state, obj, objects): 
        flip_state = copy.deepcopy(state)
        new_obj=[]
        max_x = max(x for x, _ in obj)
        min_x = min(x for x, _ in obj)
        
        for x, y in obj:
            flip_state[x][y] = 0 
        for x, y in obj:
            flip_state[max_x+min_x-x][y]=state[x][y]
            new_obj.append([max_x+min_x-x, y])
        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
        
        return flip_state, objects

    # make a horizontal flip of the selected object
    def horizontal_flip_obj(self, state, obj, objects): 
        flip_state = copy.deepcopy(state)
        new_obj=[]
        max_y = max(y for _, y in obj)
        min_y = min(y for _, y in obj)
        
        for x, y in obj:
            flip_state[x][y] = 0 
        for x, y in obj:
            flip_state[x][max_y+min_y-y]=state[x][y]
            new_obj.append([x, max_y+min_y-y])
        for object in objects:
            if obj == objects[object]:
                objects[object]=new_obj
        return flip_state, objects

    # make X-line in one pixel until they reach the end of the grid
    def X_line(self, state, r, c, color, objects):
        X_state = copy.deepcopy(state)
        x_move={-1, 1}
        y_move={-1, 1}
        
        for i in x_move:
            for j in y_move:
                moved_x, moved_y = r + i, c + j
                while 0 <= moved_x < len(state) and 0 <= moved_y < len(state[0]):
                    X_state[moved_x][moved_y] = color
                    moved_x+=i
                    moved_y+=j
            
        return X_state, objects

    # make horizontal line between two pixel
    def horizontal_line(self, state, r1, c1, r2, c2, color, objects):
        line_state = copy.deepcopy(state)
        if r1 == r2:
            if c1<c2:
                if c2<=len(state[0]):
                    for i in range(c1+1, c2):
                        line_state[r1][i]=color
            else :
                if c1<=len(state[0]):
                    for i in range(c2+1, c1):
                        line_state[r1][i]=color
                
        return line_state, objects

    # make vertical line between two pixel
    def vertical_line(self, state, r1, c1, r2, c2, color, objects):
        line_state = copy.deepcopy(state)
        
        if c1 == c2:
            if r1<r2:
                if r2<=len(state):
                    for i in range(r1+1, r2):
                        line_state[i][c1]=color
            else :
                if r1<=len(state):
                    for i in range(r2+1, r1):
                        line_state[i][c1]=color
                
        return line_state, objects

    # make diagonal line between two pixel
    def diagonal_line(self, state, r1, c1, r2, c2, color, objects):
        line_state = copy.deepcopy(state)
        
        if abs(r1-r2) == abs(c1-c2):
            dr=1 if r2>r1 else -1
            dc=1 if c2>c1 else -1
            
            r, c = r1+dr, c1+dc
            while r != r2 and c != c2:
                line_state[r][c]=color
                r += dr
                c += dc
        return line_state, objects

    # change the color of the selected object
    def obj_color(self, state, obj, color, objects):
        color_state = copy.deepcopy(state)
        
        for x, y in obj:
            color_state[x][y] = color
            
        return color_state, objects

    # change the color of the selected pixel
    def pixel_color(self, state, r, c, color, objects):
        temp_state = copy.deepcopy(state)
        temp_state[r][c] = color
        return temp_state, objects

    def complete(self, state, objects):
        return state, objects
    
    def step(self, state, object, dsl): ###################################################
        if dsl=='' or dsl=='None':
            return state, object
        else:
            dsl = dsl.replace("`", "")
            action=dsl.split('(')[0]
            args=dsl.split('(')[1][:-1]
            if args[-1]==')':
                args=args[:-1].split(', ')
            else: args=args.split(', ')
            if action == 'rotate_left_state' and len(args)==1:
                return self.rotate_left_state(state, object)
            elif action == 'rotate_right_state' and len(args)==1:
                return self.rotate_right_state(state, object)
            elif action == 'horizontal_flip' and len(args)==1:
                return self.horizontal_flip(state, object)
            elif action == 'vertical_flip' and len(args)==1:
                return self.vertical_flip(state, object)
            elif action == 'move_right' and len(args)==2:
                return self.move_right(state, object[args[1]], object)
            elif action == 'move_left' and len(args)==2:
                return self.move_left(state, object[args[1]], object)
            elif action == 'move_up' and len(args)==2:
                return self.move_up(state, object[args[1]], object)
            elif action == 'move_down' and len(args)==2:
                return self.move_down(state, object[args[1]], object)
            elif action == 'rotate_right_obj' and len(args)==2:
                return self.rotate_right_obj(state, object[args[1]], object)
            elif action == 'rotate_left_obj' and len(args)==2:
                return self.rotate_left_obj(state, object[args[1]], object)
            elif action == 'vertical_flip_obj' and len(args)==2:
                return self.vertical_flip_obj(state, object[args[1]], object)
            elif action == 'horizontal_flip_obj' and len(args)==2:
                return self.horizontal_flip_obj(state, object[args[1]], object)
            elif action == 'X_line' and len(args)==4:
                return self.X_line(state, int(args[1]), int(args[2]), int(args[3]), object)
            elif action == 'horizontal_line' and len(args)==6:
                return self.horizontal_line(state, int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]), object)
            elif action == 'vertical_line' and len(args)==6:
                return self.vertical_line(state, int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]), object)
            elif action == 'diagonal_line' and len(args)==6:
                return self.diagonal_line(state, int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5]), object)
            elif action == 'obj_color' and len(args)==3:
                return self.obj_color(state, object[args[1]], int(args[2]), object)
            elif action == 'pixel_color' and len(args)==4:
                return self.pixel_color(state, int(args[1]), int(args[2]), int(args[3]), object)
            elif action == 'complete' and len(args)==1:
                return self.complete(state, object)
            else:
                # raise ValueError(f'dsl {dsl} not recognized')
                return state, object

class ARCTask(Task):
    # Set the variables.
    def __init__(self, dsl_file='dsl.txt', folder='arc.json'):
        super().__init__()
        path = os.path.join('data/', folder)
        self.data = []
        with open(path, 'r') as f:
            self.data.append(json.load(f))
        self.value_cache = {}
        self.steps = 5
        self.stops = ['\n'] * 5
        self.env = ARCEnv(dsl_file)

    def __len__(self) -> int:
        return len(self.data)
        
    # Read given task idx information from json file.
    def get_input(self, idx: int):
        '''
        Example 1
        If input grids are like that
        [[0, 0, 0, 8, 0, 0], [0, 0, 8, 8, 8, 0], [0, 8, 0, 8, 8, 0], [8, 8, 8, 0, 0, 0], [0, 8, 8, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
        then this grids change to output grids below
        [[0, 8, 0, 0, 8], [8, 8, 0, 8, 8], [0, 0, 0, 0, 0], [0, 8, 0, 0, 8], [8, 8, 0, 8, 8]].

        Example 2
        If input grids are like that
        [[8, 8, 8, 8, 0, 0], [8, 8, 8, 8, 8, 8], [0, 8, 8, 0, 8, 8], [0, 8, 8, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
        then this grids change to output grids below
        [[8, 8, 0, 8, 8], [8, 8, 0, 8, 8], [0, 0, 0, 0, 0], [8, 8, 0, 8, 8], [8, 8, 0, 8, 8]].

        Example 3
        If input grids are like that
        [[0, 0, 0, 8, 0, 0], [0, 8, 8, 8, 8, 0], [8, 8, 8, 8, 8, 0], [0, 8, 8, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
        then this grids change to output grids below
        [[0, 8, 0, 0, 8], [8, 8, 0, 8, 8], [0, 0, 0, 0, 0], [0, 8, 0, 0, 8], [8, 8, 0, 8, 8]].
        '''
        target_data = self.data[0][idx]
        example_number = 1
        examples_prompt = ''
        quiz_prompt = ''
        for train_index in range(len(target_data['train'])):
            for keys in target_data['train'][train_index].keys():
                if keys == 'input':
                    examples_prompt += f"Example {example_number}\n" \
                                    f"If input grids are like that\n" \
                                    f"{target_data['train'][train_index][keys]},\n"
                elif keys == 'objects':
                    examples_prompt += f"and the object information is like that\n" \
                                    f"{target_data['train'][train_index][keys]},\n"
                else:
                    examples_prompt += f"then this grids change to output grids below\n" \
                                    f"{target_data['train'][train_index][keys]}.\n\n"

            example_number += 1
        '''
        Quiz
        If input grids are like that
        [[0, 0, 8, 8, 0, 0], [8, 8, 8, 8, 0, 0], [8, 8, 0, 8, 8, 0], [0, 8, 8, 8, 8, 0], [0, 8, 8, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
        then output grids?
        '''
        for test_index in range(len(target_data['test'])):
            for keys in target_data['test'][test_index].keys():
                if keys == 'input':
                    quiz_prompt += f"Quiz\n" \
                                f"If input grids are like that\n" \
                                f"{target_data['test'][test_index][keys]},\n"
                                
                elif keys == 'objects':
                    quiz_prompt += f"The object information is like that\n"\
                                f"{target_data['test'][test_index][keys]}.\n\n"
                    original_object=target_data['test'][test_index][keys]
                else:
                    quiz_prompt += f"then output grids?\n" 
        return examples_prompt, quiz_prompt, original_object, target_data['test'][test_index]['input']

    # 해당 함수 안 쓰고 있는데 주석 처리 끝난 후 한번 더 다시 확인해보기 - 우창
    def test_output(self, idx: int, output: str):
        expression = output.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]
        numbers = re.findall(r'\d+', expression)
        problem_numbers = re.findall(r'\d+', self.data[idx])
        if sorted(numbers) != sorted(problem_numbers):
            return {'r': 0}
        try:
            return {'r': int(sympy.simplify(expression) == 24)}
        except Exception as e:
            return {'r': 0}

    # Wrap the prompt that used to predict dsl about the task.
    def standard_prompt_wrap(self, examples: str, quiz: str, object: str, dsl_y: str='', state_y: str='') -> str:
        if dsl_y == '':
            prompt = dsl_standard_init_prompt.format(examples=examples, quiz=quiz, object=object, dsl_list=self.env.dsl_list)
        else:
            used_dsls = ''
            prompt = dsl_standard_prompt.format(examples=examples, quiz=quiz, object=object, used_dsls=dsl_y, current_state=state_y, dsl_list=self.env.dsl_list)
        
        return prompt

    # Wrap the prompt that used to self-evaluate the given suggestion(Value).
    def value_prompt_wrap(self, task, examples, quiz, dsl_y, state_y):
        return value_prompt.format(dsl_list=self.env.dsl_list, examples=examples, quiz=quiz, used_dsls=dsl_y, current_state=state_y)

    # UnWrap the prompt that used to self-evaluate the given suggestion(Value).
    @staticmethod
    def value_outputs_unwrap(value_outputs: list) -> float:
        value_names = [_.split('\n')[-1] for _ in value_outputs]
        value_map = {'impossible': 0.001, 'maybe': 1, 'sure': 20}  
        value = sum(value * target_value.count(name) for name, value in value_map.items() for target_value in value_names)
        return value
