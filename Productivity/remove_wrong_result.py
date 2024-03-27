import json
from utils import read_data_from_json, remove_input_by_order

file_path = 'HF_Augmented_Data/MoveToBoundary_112_Aug.json'
data = read_data_from_json(file_path)

###############################################
order_to_remove = 3 # Remove the example index after we should wrong generated example.
###############################################

# Remove target example index and then save it.
data = remove_input_by_order(data, order_to_remove)
with open(file_path, 'w') as file:
    json.dump(data, file)
