import json
from utils import read_json_file, remove_input_by_order

file_path = 'HF_Augmented_Data/MoveToBoundary_112_Aug.json'
data = read_json_file(file_path)

###############################################
order_to_remove = 3 # 삭제하고 싶은 input의 순서
###############################################

data = remove_input_by_order(data, order_to_remove)
with open(file_path, 'w') as file:
    json.dump(data, file)