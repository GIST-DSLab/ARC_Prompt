import PnP
import os
import json
import numpy as np
import copy

# type = "tr" or "ev", j_num = 1 ~ 400, pair = "train" or "test" ,p_num = 0 ~ 9, io = 0 ~ 1
def get_grid ():
    with open("arc_no_object.json", 'r') as f:
        data = json.load(f)
    return data
    
# PnP result is a grid with object indices, so it is necessary to convert it to list of grid coordinate
def PnP_result_to_grid_coord (PnP_result):
    gg = PnP_result[-1] # the last element of PnP_result is the grid

    m = np.amax(gg) # number of objects
    
    obj_coord_list = []
    for i in range(m):
        obj_coord_list.append([])
    
    # append the grid coordinates of each object to the list
    for i in range(len(gg)):
        for j in range(len(gg[0])):
            if gg[i][j] != 0:
                obj_coord_list[gg[i][j]-1].append([i, j])

    return obj_coord_list


        

if __name__ == "__main__":
    data = get_grid()

    new = []
    # walk through the data and add the objects after every input grid
    for i in range(len(data)):
        # two exepctions that has error on PnP result
        if i == 39 or i == 117:
            pass
            
        else:
            new_2 = {}
            for j in ['train', 'test']:
                new_3 = []
                for k in range(len(data[i][j])):
                    new_4 = {}
                    for l in ['input', 'output']:
                        if l == 'input':
                            obj = PnP.get_object(data[i][j][k][l])
                            m = 0
                            new_5 = {}
                            for m in range(len(PnP_result_to_grid_coord(obj))):
                                objectname = 'object'+str(m+1)
                                new_5[objectname] = PnP_result_to_grid_coord(obj)[m]

                            new_4['input'] = data[i][j][k]['input']
                            new_4['objects'] = new_5    
                        else: # l == 'output'
                            new_4['output'] = data[i][j][k]['output']

                    new_3.append(new_4)
                    

                if j == 'train':
                    new_2['train'] = new_3
                else: # j == 'test'
                    new_2['test'] = new_3

            new.append(new_2)

    # if no file -> create, if file -> overwrite
    file_path = 'arc_obj_w.json'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump(new, f, indent=4)
    else:
        print(f"The file {file_path} already exists.")
        with open(file_path, 'w') as f:
            json.dump(new, f, indent=4)
            