import json

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def remove_input_by_order(data, order):
    del data['train'][order]
    return data

file_path = 'HF_Augmented_Data/MoveToBoundary_112_Aug.json'
data = read_json_file(file_path)

###############################################
order_to_remove = 3 # 삭제하고 싶은 input의 순서
###############################################

data = remove_input_by_order(data, order_to_remove)
with open(file_path, 'w') as file:
    json.dump(data, file)