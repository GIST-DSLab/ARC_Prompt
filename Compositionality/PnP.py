import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib import colors

cmap = colors.ListedColormap(
        [
            '#000000', # 0 black
            '#0074D9', # 1 blue
            '#FF4136', # 2 red
            '#2ECC40', # 3 green
            '#FFDC00', # 4 yellow
            '#AAAAAA', # 5 gray
            '#F012BE', # 6 pink
            '#FF851B', # 7 orange
            '#7FDBFF', # 8 skyblue
            '#870C25', # 9 maroon
            '#505050', # 10 black_select
            '#30A4F9', # 11 blue_select
            '#FF7166', # 12 red_select
            '#5EFC70', # 13 green_select
            '#FFFC30', # 14 yellow_select
            '#DADADA', # 15 gray_select
            '#F042EE', # 16 pink_select
            '#FFB54B', # 17 orange_select
            '#AFFBFF', # 18 skyblue_select
            '#B73C55'  # 19 maroon_select
        ])
# norm = colors.Normalize(vmin=0, vmax=9)
norm = colors.Normalize(vmin=0, vmax=19)


def get_node_number (col, i, j): ## start from 0 to (col * row -1)
    temp = i * (col) + j
    return temp

def find_near_node (grid, i ,j):
    temp = np.zeros(3*3).reshape((3,3))
    if grid[i][j] == 0: 
        return temp
    for r in [-1,0,1]:
        for c in [-1,0,1] :
            try :
                if grid [i + r][j + c] == grid [i][j] and i + r >= 0 and j + c >= 0:
                    if r == 0 or c == 0:
                        temp[r + 1][c + 1] = 1 # same color direct ajacent
                    else :
                        temp[r + 1][c + 1] = 2 # same color diagonal ajacent

                elif grid [i + r][j + c] != grid [i][j] and grid [i + r][j + c] != 0 and i + r >= 0 and j + c >= 0:
                    if r == 0 or c == 0:
                        temp[r + 1][c + 1] = 4 # different color direct ajacent
                    else :
                        temp[r + 1][c + 1] = 5 # different color diagonal ajacent
            except :
                continue
    temp[1][1] = 0
    return temp

def grid_to_adj(grid):
    row, col = len(grid), len(grid[0])
    num_node = row * col
    adj = np.zeros(num_node*num_node).reshape([num_node, num_node])
    for i in range (row):
        for j in range (col):
            if grid[i][j] == 0:
                continue
            temp = find_near_node(grid, i, j)
            curr_node = get_node_number(col, i, j)
            for r in [0,1,2]:
                for c in [0,1,2]:
                    if temp[r][c] != 0:
                        node_num = get_node_number(col, i + r - 1, j + c -1)
                        if curr_node < node_num :
                            adj[curr_node][node_num] = temp[r][c]    
                        else :
                            adj[node_num][curr_node] = temp[r][c]
    return np.array(adj)

# class ############################################################################################################
class node :
    def __init__(self, grid, i, j):
        self.color = grid[i][j]
        self.number = get_node_number(len(grid[0]), i, j)
        self.coordinate = [3 * j, 3 * (len(grid) - i - 1)]
        self.coor2 = [j,i]
        self.object = -1

def grid_to_node (grid):
    list_of_node = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            temp_node = node(grid, i, j)
            temp_node.color = grid[i][j]
            list_of_node.append(temp_node)
    return list_of_node

def grid_to_graph (nodes, adj):
    x = []
    y = []
    colors = []
    num_nodes = len(nodes)
    
    for ele in (nodes):
        x.append(ele.coordinate[0])
        y.append(ele.coordinate[1])
        colors.append(ele.color)
    
    plt.figure(figsize = (2 * math.sqrt(len(adj)), 2 * math.sqrt(len(adj))))
    for i in range(len(nodes)):
        plt.text(x[i] - 0.1, y[i] - 0.1, nodes[i].number , size = 25, color = 'white')
        
    for i in range(num_nodes) :
        for j in range(i, num_nodes) :
            ii = nodes[i].number
            jj = nodes[j].number

            if adj[ii][jj] == 0 :
                continue
            elif adj[ii][jj] == 4 or adj[ii][jj] == 5:
                plt.plot([x[i], x[j]], [y[i], y[j]], color = 'black', linewidth = 5)
            else :
                color = nodes[i].color
                color = get_color(color)
                plt.plot([x[i], x[j]], [y[i], y[j]], color = color[0], linewidth = 5)
    plt.axis('off')
    plt.scatter(x, y, s = 2500, c = colors, cmap = cmap, norm = norm)

    for i in range(len(nodes) - 1, -1, -1):
        if nodes[i].color == 0 :
            x.pop(i)
            y.pop(i)
            colors.pop(i)
        
    plt.axis('off')
    plt.scatter(x, y, s = 2500, c = colors, cmap = cmap, norm = norm)
    
def get_color(color) :
    if color == 0:
        color = '#000000', # 0 black
    if color == 1:
        color = '#0074D9', # 1 blue
    if color == 2:
        color = '#FF4136', # 2 red
    if color == 3:
        color = '#2ECC40', # 3 green
    if color == 4:
        color = '#FFDC00', # 4 yellow
    if color == 5:
        color = '#AAAAAA', # 5 gray
    if color == 6:
        color = '#F012BE', # 6 pink
    if color == 7:
        color = '#FF851B', # 7 orange
    if color == 8:
        color = '#7FDBFF', # 8 skyblue
    if color == 9:
        color = '#870C25', # 9 maroon
    return color  


def move_left (ele, val):
    ele.coordinate[0] -= val
def move_right (ele, val) :
    ele.coordinate[0] += val
def move_up (ele, val) :
    ele.coordinate[1] += val
def move_down (ele, val) :
    ele.coordinate[1] -= val
def move_rightup (ele, val) :
    val = val / 1.414
    ele.coordinate[1] += val 
    ele.coordinate[0] += val
def move_rightdown (ele, val) :
    val = val / 1.414
    ele.coordinate[1] -= val 
    ele.coordinate[0] += val
def move_leftup (ele, val) :
    val = val / 1.414
    ele.coordinate[1] += val 
    ele.coordinate[0] -= val
def move_leftdown (ele, val) :
    val = val / 1.414
    ele.coordinate[1] -= val 
    ele.coordinate[0] -= val
    
def make_cluster (nodes, adj):
    for i in range (len(adj)):
        for j in range(len(adj[0])):
            if adj[i][j] != 0:
                temp = adj[i][j]
                temp = (temp - 3) / 2
                if temp < 0: 
                    if nodes[i].coor2[0] == nodes[j].coor2[0] and nodes[i].coor2[1] < nodes[j].coor2[1]:
                        move_up(nodes[i], temp)
                        move_down(nodes[j], temp)
                    elif nodes[i].coor2[0] < nodes[j].coor2[0] and nodes[i].coor2[1] == nodes[j].coor2[1]:
                        move_right(nodes[j], temp)
                        move_left(nodes[i], temp)
                    elif nodes[i].coor2[0] < nodes[j].coor2[0] and nodes[i].coor2[1] < nodes[j].coor2[1]:
                        move_rightdown(nodes[j], temp)
                        move_leftup(nodes[i], temp)
                    elif nodes[i].coor2[0] > nodes[j].coor2[0] and nodes[i].coor2[1] < nodes[j].coor2[1]:
                        move_rightup(nodes[i], temp)
                        move_leftdown(nodes[j], temp)
                
                elif temp > 0: 
                    if nodes[i].coor2[0] == nodes[j].coor2[0] and nodes[i].coor2[1] < nodes[j].coor2[1]:
                        move_up(nodes[i], temp)
                        move_down(nodes[j], temp)
                    elif nodes[i].coor2[0] < nodes[j].coor2[0] and nodes[i].coor2[1] == nodes[j].coor2[1]:
                        move_right(nodes[j], temp)
                        move_left(nodes[i], temp)
                    elif nodes[i].coor2[0] < nodes[j].coor2[0] and nodes[i].coor2[1] < nodes[j].coor2[1]:
                        move_rightdown(nodes[j], temp)
                        move_leftup(nodes[i], temp)
                    elif nodes[i].coor2[0] > nodes[j].coor2[0] and nodes[i].coor2[1] < nodes[j].coor2[1]:
                        move_rightup(nodes[i], temp)
                        move_leftdown(nodes[j], temp)


def remove_black(nodes, adj):
    for i in range(len(nodes) - 1, -1, -1):
        if nodes[i].color == 0:
            num = nodes[i].number
            nodes.remove(nodes[i])
            for i in range(len(adj)):
                adj[num][i] = 0
                adj[i][num] = 0


def get_object (grid):
    adj = grid_to_adj(grid)
    nodes = grid_to_node(grid)
    # grid_to_graph(nodes,adj)
    make_cluster(nodes, adj)
    remove_black(nodes, adj)
    from sklearn.cluster import DBSCAN
    import pandas as pd
    cor = list()
    for i in range(len(nodes)):
        cor.append(nodes[i].coordinate)

    cor = np.array(cor)



    df = pd.DataFrame(cor)

    model = DBSCAN(eps=5, min_samples=1)
    model.fit(df)
    df['cluster'] = model.fit_predict(df)

    notblack = []
    for ele in nodes:
        notblack.append(ele.number)

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if i * len(grid[0]) + j not in notblack:
                temp = node(grid, i, j)
                temp.color = 0
                temp.number = i * len(grid[0]) + j
                temp.object = -1
                nodes.append(temp)
    for i, ele in enumerate(df['cluster']):
        nodes[i].object = ele

    nodes.sort(key = lambda x: x.number)
    node_ob = [[0 for c in grid[0]] for r in grid]

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            node_ob[i][j] = nodes[i * (len(grid[0])) + j].object + 1

    return nodes, adj, node_ob

if __name__ == "__main__":
    grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 5, 5, 0], 
            [0, 5, 5, 0, 0, 0, 0, 5, 5, 0], 
            [0, 0, 5, 5, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 5], 
            [0, 0, 0, 0, 0, 5, 5, 0, 0, 5], 
            [0, 5, 0, 0, 0, 0, 0, 0, 0, 5], 
            [0, 5, 0, 0, 5, 0, 0, 0, 0, 0], 
            [0, 0, 0, 5, 5, 0, 0, 0, 0, 0]]

    kk = get_object(grid) # nodes, adj, node_ob
    print(kk[2])
    


    for i in range(0, len(kk[2])):
        print(kk[2][i])

    print("###############")
        
        
    obj = get_object(grid)

    def PnP_result_to_grid_coord (PnP_result):
        gg = PnP_result[-1]

        m = np.amax(gg)
        
        obj_coord_list = []
        for i in range(m):
            obj_coord_list.append([])
        
        for i in range(len(gg)):
            for j in range(len(gg[0])):
                if gg[i][j] != 0:
                    obj_coord_list[gg[i][j]-1].append([i, j])

        return obj_coord_list

    for p in range(len(PnP_result_to_grid_coord(obj))):
        print("Object", p+1)
        print(PnP_result_to_grid_coord(obj)[p])

    