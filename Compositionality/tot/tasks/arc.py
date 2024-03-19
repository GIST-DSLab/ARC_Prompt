import re
import os
import sympy
import pandas as pd
from tot.tasks.base import Task
from tot.prompts.arc import * 
import json
import copy
import re
import ast

class ARCEnv:
    def __init__(self, dsl_file='dsl.txt'):
        self.dsl_list = ''
        with open(os.path.join('./data', dsl_file), 'r', encoding='utf-8') as f:
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
                for [x, y] in object:
                    new_x=N-1-y
                    new_y=x
                    new_obj.append([new_x, new_y])
                new_objects[object]=new_obj
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
        N = len(state)  # state의 높이를 얻습니다.
        M = len(state[0])  # state의 너비를 얻습니다.
        temp_state = copy.deepcopy(state)  # 원본 state의 깊은 복사본을 생성합니다.

        for i in range(N):
            for j in range(M):  # 중앙을 기준으로 왼쪽과 오른쪽을 교환합니다.
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
    def __init__(self, dsl_file='dsl.txt', folder='arc.json'):
        super().__init__()
        path = os.path.join('data/', folder)
        # TODO arc dataset folder에서 json 파일읽어오는 부분 구현하기(그전에 구현해둔 것 있음)
        # TODO arc json에서 train(example)과 test(quiz) 따로 분리해두기 
        self.data = []
        with open(path, 'r') as f:
            self.data.append(json.load(f))
        self.value_cache = {}
        self.steps = 10
        self.stops = ['\n'] * 5
        self.env = ARCEnv(dsl_file)

    def __len__(self) -> int:
        return len(self.data)
    
    # TODO get_input을 다른 task들과 달리 리턴을 튜플로 하는 형식으로 바꿔야할 듯 -> (examples, quiz)
    # get_input은 solve 혹은 naive_solve에서 for loop전에 호출되고 그 이후에 호출되지 않음 
    # => 즉 get_input을 통해 풀어야 할 문제 셋팅을 가져옴 
    def get_input(self, idx: int):
        # TODO 해당 부분을 아래와 같은 형식이 될 수 있도록 코드 수정하기(아래는 대략적인 예시)
        # examples 부분
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
        # quiz 부분
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
    
    # TODO 아마 아래 모든 인자값들을 examples, quiz, y로 바꿔야 할 듯(이때 y는 thoughts(action 혹은 dsl)임)

    def test_output(self, idx: int, output: str):
        # TODO log 기록 용도 - examples, quiz, y, description 등을 기록하기
        expression = output.strip().split('\n')[-1].lower().replace('answer: ', '').split('=')[0]
        numbers = re.findall(r'\d+', expression)
        problem_numbers = re.findall(r'\d+', self.data[idx])
        if sorted(numbers) != sorted(problem_numbers):
            return {'r': 0}
        try:
            # print(sympy.simplify(expression))
            return {'r': int(sympy.simplify(expression) == 24)}
        except Exception as e:
            # print(e)
            return {'r': 0}

    # TODO examples, quiz, y 등을 인자로 받고 staandard_prompt 문자열 안에 format으로 붙여넣기
    def standard_prompt_wrap(self, examples: str, quiz: str, object: str, dsl_y: str='', state_y: str='') -> str:
        if dsl_y == '':
            prompt = dsl_standard_init_prompt.format(examples=examples, quiz=quiz, object=object, dsl_list=self.env.dsl_list)
        else:
            # TODO y에서 LLM이 선택한 dsl만 파싱하기
            used_dsls = ''
            prompt = dsl_standard_prompt.format(examples=examples, quiz=quiz, object=object, used_dsls=dsl_y, current_state=state_y, dsl_list=self.env.dsl_list)
        
        return prompt

    # TODO examples, quiz, y 등을 인자로 받고 cot_prompt_wrap 문자열 안에 format으로 붙여넣기
    def cot_prompt_wrap(self, examples: str, quiz: str, dsl_y: str='', state_y: str='') -> str:
        return cot_prompt.format(input=x) + y
    
    # TODO examples, quiz, y 등을 인자로 받고 propose_prompt_wrap 문자열 안에 format으로 붙여넣기
    def propose_prompt_wrap(self, examples: str, quiz: str, dsl_y: str='', state_y: str='') -> str:
        if dsl_y == '':
            prompt = dsl_standard_init_prompt.format(examples=examples, quiz=quiz, dsl_list=self.env.dsl_list)
        else:
            # TODO y에서 LLM이 선택한 dsl만 파싱하기
            used_dsls = ''
            prompt = dsl_standard_prompt.format(examples=examples, quiz=quiz, used_dsls=dsl_y, current_state=state_y)

        # TODO 아래 부분은 ARC에 맞게 수정하기
        # current_numbers = get_current_numbers(y if y else x)
        # if current_numbers == '24':
        #     prompt = cot_prompt.format(input=x) + 'Steps:' + y
        #     # print([prompt])
        # else:
        #     prompt = propose_prompt.format(input=current_numbers)

        return prompt
    
    # TODO examples, quiz, y 등을 인자로 받고 value_prompt_wrap 문자열 안에 format으로 붙여넣기
    # ? value_last_step_prompt가 ARC에 필요할까?
    def value_prompt_wrap(self, task, examples, quiz, dsl_y, state_y):
        # last_line = y.strip().split('\n')[-1]
        # if 'left: ' not in last_line:  # last step
        #     ans = last_line.lower().replace('answer: ', '')
        #     # print([value_last_step_prompt.format(input=x, answer=ans)])
        #     return value_last_step_prompt.format(input=x, answer=ans)
        # current_numbers = get_current_numbers(y)
        return value_prompt.format(dsl_list=self.env.dsl_list, examples=examples, quiz=quiz, used_dsls=dsl_y, current_state=state_y)
    
    # TODO 어떤식으로 value 측정할 것인지 고민하고 해당 내용을 바탕으로 value_prompt 구성하기
    # value_outputs으로 얻은 결과를 평가하는 부분
    @staticmethod
    def value_outputs_unwrap(value_outputs: list) -> float:
        value_names = [_.split('\n')[-1] for _ in value_outputs]
        value_map = {'impossible': 0.001, 'maybe': 1, 'sure': 20}  # TODO: ad hoc
        value = sum(value * target_value.count(name) for name, value in value_map.items() for target_value in value_names)
        return value
