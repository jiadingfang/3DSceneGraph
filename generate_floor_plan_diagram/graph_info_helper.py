import re
import ast
import numpy as np
import json

test_text = """
    The current place is room_11 with information {'type': 'room', 'floor_area': 7.66, 'floor_number': 'A', 'id': 11, 'location': array([ 0.23, -0.02,  1.23]), 'scene_category': 'lobby', 'size': array([2.36, 1.97, 2.45]), 'volume': 9.15, 'parent_building': 2}
    You have visited places ['room_11']:
    It has 8 number of neighbors:
    The number 1 neighbor place is room_6 with information {'type': 'room', 'floor_area': 7.37, 'floor_number': 'A', 'id': 6, 'location': array([2.02, 1.43, 1.22]), 'scene_category': 'corridor', 'size': array([2.18, 2.84, 2.45]), 'volume': 6.81, 'parent_building': 2}
    The number 2 neighbor place is room_2 with information {'type': 'room', 'floor_area': 9.83, 'floor_number': 'A', 'id': 2, 'location': array([0.42, 2.4 , 1.13]), 'scene_category': 'bathroom', 'size': array([2.89, 2.93, 2.26]), 'volume': 13.85, 'parent_building': 2}
    The number 3 neighbor place is room_1 with information {'type': 'room', 'floor_area': 8.73, 'floor_number': 'A', 'id': 1, 'location': array([3.54, 0.29, 1.12]), 'scene_category': 'bathroom', 'size': array([2.58, 2.37, 2.25]), 'volume': 10.48, 'parent_building': 2}
    The number 4 neighbor place is room_5 with information {'type': 'room', 'floor_area': 7.16, 'floor_number': 'A', 'id': 5, 'location': array([1.79, 3.48, 1.23]), 'scene_category': 'corridor', 'size': array([1.93, 2.56, 2.45]), 'volume': 7.75, 'parent_building': 2}
    The number 5 neighbor place is object_11 with information {'type': 'object', 'action_affordance': ['fill', 'pick up', 'break', 'clean'], 'floor_area': 0.71, 'surface_coverage': 0.08, 'class_': 'vase', 'id': 11, 'location': array([-0.16,  0.78,  0.87]), 'material': ['metal', None], 'size': array([0.2 , 0.25, 0.2 ]), 'tactile_texture': 'bumpy', 'visual_texture': None, 'volume': 0.0, 'parent_room': 11}
    The number 6 neighbor place is object_12 with information {'type': 'object', 'action_affordance': ['fill', 'pick up', 'break', 'clean'], 'floor_area': 0.5, 'surface_coverage': 0.06, 'class_': 'vase', 'id': 12, 'location': array([-0.7 ,  0.72,  0.87]), 'material': ['ceramic', None], 'size': array([0.16, 0.17, 0.19]), 'tactile_texture': None, 'visual_texture': 'lined', 'volume': 0.0, 'parent_room': 11}
    The number 7 neighbor place is object_13 with information {'type': 'object', 'action_affordance': ['fill', 'pick up', 'break', 'clean'], 'floor_area': 0.64, 'surface_coverage': 0.02, 'class_': 'vase', 'id': 13, 'location': array([-0.82,  0.86,  0.85]), 'material': ['ceramic', None], 'size': array([0.27, 0.12, 0.16]), 'tactile_texture': None, 'visual_texture': 'lined', 'volume': 0.0, 'parent_room': 11}
    The number 8 neighbor place is object_14 with information {'type': 'object', 'action_affordance': ['fill', 'pick up', 'break', 'clean'], 'floor_area': 0.76, 'surface_coverage': 0.08, 'class_': 'vase', 'id': 14, 'location': array([-0.43,  0.79,  0.87]), 'material': ['ceramic', None], 'size': array([0.21, 0.28, 0.2 ]), 'tactile_texture': None, 'visual_texture': None, 'volume': 0.0, 'parent_room': 11}
    """


def replace_array_pattern(input_string):
    # Define a regular expression pattern to match the desired pattern
    pattern = r'array\((\[.*?\])\)'

    # Use re.sub to find all occurrences of the pattern and replace them
    replaced_string = re.sub(pattern, r'\1', input_string)

    return replaced_string


def graph_info_helper(text: str):
    # Extract information using regular expressions
    central_node = re.search(r"The current place is (\w+)", text).group(1)
    neighbors = re.findall(r"The number \d+ neighbor place is (\w+) with information (\{.*?\})", text)

    # Construct node list
    node_list = [central_node] + [neighbor[0] for neighbor in neighbors]

    # Construct node attribute dictionary
    node_attr_dict = {central_node: re.search(r"information (\{.*?\})", text).group(1)}
    for neighbor_name, neighbor_info in neighbors:
        node_attr_dict[neighbor_name] = neighbor_info

    return node_list, node_attr_dict


def get_node_name_and_attr(node_name: str, node_dict: dict) -> str:
    attr_str = node_dict[node_name]
    attr_str = replace_array_pattern(attr_str)
    attr_dict = eval(attr_str)
    res_str = node_name + '\n'
    for key, value in attr_dict.items():
        res_str += key + ": " + str(value) + '\n'
    return res_str


def get_node_pos(node_name: str, node_dict: dict):
    attr_str = node_dict[node_name]
    attr_str = replace_array_pattern(attr_str)
    attr_dict = eval(attr_str)
    assert 'location' in attr_dict.keys()
    try:
        return attr_dict['location']
    except KeyError:
        print("No location information")


def node_is_object(node_name: str, node_dict: dict):
    attr_str = node_dict[node_name]
    attr_str = replace_array_pattern(attr_str)
    attr_dict = eval(attr_str)
    return attr_dict['type'] == 'object'


def node_is_room(node_name: str, node_dict: dict):
    attr_str = node_dict[node_name]
    attr_str = replace_array_pattern(attr_str)
    attr_dict = eval(attr_str)
    return attr_dict['type'] == 'room'


if __name__ == '__main__':
    node_list, node_attr_dict = graph_info_helper(test_text)
    # Display node list and attributes
    print("Node List:", node_list)
    # for node, info in node_attr_dict.items():
    #     print(f"Node: {node}")
    #     print(f"Information: {info}")

    print("Node room_5 name:")
    print(get_node_name_and_attr('room_5', node_attr_dict))

    print("Node object_11 location:")
    print(get_node_pos('object_11', node_attr_dict))

    print("Is Node object_12 a room?")
    print(node_is_room('object_12', node_attr_dict))
