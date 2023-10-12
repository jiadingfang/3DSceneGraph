import re
import json
import numpy as np
import networkx as nx

################################################
# load processed scene text
################################################
split = 'tiny_automated'
scene_name = 'Allensville'
scene_text_path = 'scene_text/{}/{}.scn'.format(split, scene_name)
with open(scene_text_path) as f:
    scene_text = f.read()

# use json to load text
scene_data = json.loads(scene_text)
print('num of objects: ', len(scene_data['objects']))
print('num of rooms: ', len(scene_data['rooms']))

################################################
# Create networkx graph
################################################
graph = nx.Graph(scene=scene_name)

# Add nodes for each object
for object_dict in scene_data['objects']:
    # graph.add_node(i, type='object')
    id = object_dict['id']
    node_name = 'object_{}'.format(id)
    graph.add_node(node_name, type='object')
    for key, value in object_dict.items():
        graph.nodes[node_name][key] = value

# Add nodes for each room  
for object_dict in scene_data['rooms']:
    # graph.add_node(i, type='room')
    id = object_dict['id']
    node_name = 'room_{}'.format(id)
    graph.add_node(node_name, type='room')
    for key, value in object_dict.items():
        graph.nodes[node_name][key] = value

# print('networkx graph data: ', graph.nodes.data)

# Connect objects to the rooms they are located in
object_node_name_list = [node_name for node_name in graph.nodes if 'object' in node_name]
for object_node_name in object_node_name_list:
    object_node = graph.nodes[object_node_name]
    # print('object_node: ', object_node)
    parent_room_id = object_node['parent_room']
    parent_room_name = 'room_' + str(parent_room_id)
    room_location = np.array(graph.nodes[parent_room_name]['location']) 
    object_location = np.array(graph.nodes[object_node_name]['location'])

    distance_room_object = np.linalg.norm(room_location - object_location)
    graph.add_edge(object_node_name, parent_room_name, weight=distance_room_object)
    print('distance_room_object: ', distance_room_object)

# Add edge between neighbor rooms
room_node_name_list = [node_name for node_name in graph.nodes if 'room' in node_name]
for i in range(len(room_node_name_list)):
    for j in range(i+1, len(room_node_name_list)):
        room_name_a = room_node_name_list[i]
        room_name_b = room_node_name_list[j]
        room_node_a = graph.nodes[room_name_a]
        room_node_b = graph.nodes[room_name_b]
        room_a_location = np.array(room_node_a['location'])
        room_b_location = np.array(room_node_b['location'])
        distance_room_a_room_b = np.linalg.norm(room_a_location - room_b_location)
        print('distance_room_a_room_b: ', distance_room_a_room_b)
        graph.add_edge(room_name_a, room_name_b, weight=distance_room_object)

# print('edges weights: ', [graph.edges[edge]['weight'] for edge in graph.edges])
print('graph stats: ', graph)


# # Visualize graph
# import matplotlib.pyplot as plt
# nx.draw(graph, with_labels=True)
# plt.show()

