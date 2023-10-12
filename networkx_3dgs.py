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
# graph = nx.Graph(scene=scene_name)
graph = nx.DiGraph(scene=scene_name)

# Add nodes for each room  
for object_dict in scene_data['rooms']:
    id = object_dict['id']
    node_name = 'room_{}'.format(id)
    graph.add_node(node_name, type='room')
    for key, value in object_dict.items():
        graph.nodes[node_name][key] = value
    # initialize child_objects list
    graph.nodes[node_name]['child_objects'] = []
    
# Add nodes for each object
for object_dict in scene_data['objects']:
    id = object_dict['id']
    node_name = 'object_{}'.format(id)
    graph.add_node(node_name, type='object')
    for key, value in object_dict.items():
        graph.nodes[node_name][key] = value
        
        # add child objects information for each room
        if key == 'parent_room':
            parent_room_name = 'room_' + str(value)
            graph.nodes[parent_room_name]['child_objects'].append(node_name)

# print('networkx graph data: ', graph.nodes.data)

object_node_name_list = [node_name for node_name in graph.nodes if 'object' in node_name]
room_node_name_list = [node_name for node_name in graph.nodes if 'room' in node_name]

# # Connect objects to the rooms they are located in
# object_node_name_list = [node_name for node_name in graph.nodes if 'object' in node_name]
# for object_node_name in object_node_name_list:
#     object_node = graph.nodes[object_node_name]
#     # print('object_node: ', object_node)
#     parent_room_id = object_node['parent_room']
#     parent_room_name = 'room_' + str(parent_room_id)
#     room_location = np.array(graph.nodes[parent_room_name]['location']) 
#     object_location = np.array(graph.nodes[object_node_name]['location'])

#     distance_room_object = np.linalg.norm(room_location - object_location)
#     graph.add_edge(object_node_name, parent_room_name, weight=distance_room_object)
#     print('distance_room_object: ', distance_room_object)

n_neighbors = 3
# Add edge between neighbor rooms
for i in range(len(room_node_name_list)):
    # for j in range(i+1, len(room_node_name_list)):
    room_distance_dict = {}
    for j in range(len(room_node_name_list)):
        if i == j:
            continue
        room_name_a = room_node_name_list[i]
        room_name_b = room_node_name_list[j]
        room_node_a = graph.nodes[room_name_a]
        room_node_b = graph.nodes[room_name_b]
        room_a_location = np.array(room_node_a['location'])
        room_b_location = np.array(room_node_b['location'])
        distance_room_a_room_b = np.linalg.norm(room_a_location - room_b_location)
        # print('distance_room_a_room_b: ', distance_room_a_room_b)
        room_distance_dict[(room_name_a, room_name_b)] = distance_room_a_room_b
    
    # filter out the top closest edges to add tothe graph
    sorted_room_distance_list = sorted(room_distance_dict.items(), key=lambda x:x[1], reverse=False)
    for i in range(min(n_neighbors, len(sorted_room_distance_list))):
        room_distance_pair = sorted_room_distance_list[i]
        # print('room_distance_pair: ', room_distance_pair)
        graph.add_edge(*room_distance_pair[0], weight=room_distance_pair[1])
print('graph stats after adding edges between rooms: ', graph)

# Add edges between objects in a room
for room_node_name in room_node_name_list:
    room_node = graph.nodes[room_node_name]
    child_objects_list = room_node['child_objects']

    for i in range(len(child_objects_list)):
        object_distance_dict = {}
        for j in range(len(child_objects_list)):
            if i == j:
                continue
            child_name_a = child_objects_list[i]
            child_name_b = child_objects_list[j]
            child_node_a = graph.nodes[child_name_a]
            child_node_b = graph.nodes[child_name_b]
            # print('child_node_a: ', child_node_a)
            object_a_location = np.array(child_node_a['location'])
            object_b_location = np.array(child_node_b['location'])
            # print('object_a_location: ', object_a_location)
            distaance_object_a_object_b = np.linalg.norm(object_a_location - object_b_location)
            # print('distaance_object_a_object_b: ', distaance_object_a_object_b)
            object_distance_dict[(child_name_a, child_name_b)] = distaance_object_a_object_b

        # filter out the top closest edges to add to the graph
        sorted_object_distance_list = sorted(object_distance_dict.items(), key=lambda x:x[1], reverse=False)
        for i in range(min(n_neighbors, len(sorted_object_distance_list))):
            object_distance_pair = sorted_object_distance_list[i]
            # print('object_distance_pair: ', object_distance_pair)
            graph.add_edge(*object_distance_pair[0], weight=object_distance_pair[1])

# print('edges weights: ', [graph.edges[edge]['weight'] for edge in graph.edges])
print('graph stats after adding edges between objects in a room: ', graph)

# Add a loop edge between a room and the closest object in this room (so the agent can go in and out of a room)
for room_node_name in room_node_name_list:
    room_node = graph.nodes[room_node_name]
    room_location = np.array(room_node['location'])
    room_objects_distance_dict = {}
    if len(room_node['child_objects']) > 0:
        for object_name in room_node['child_objects']:
            object_node = graph.nodes[object_name]
            object_location = np.array(object_node['location'])
            room_object_distance = np.linalg.norm(room_location - object_location)
            room_objects_distance_dict[(room_node_name, object_name)] = room_object_distance

        # find the closest object to room location and add loop edge
        sorted_room_object_distance_list = sorted(room_objects_distance_dict.items(), key=lambda x:x[1], reverse=False)
        room_object_pair = sorted_room_object_distance_list[0]
        room_name, object_name = room_object_pair[0]
        room_object_distance = room_object_pair[1]
        graph.add_edge(room_name, object_name, weight=room_object_distance)
        graph.add_edge(object_name, room_name, weight=room_object_distance)

print('graph stats after adding edges between object and room: ', graph)

# Visualize graph
import matplotlib.pyplot as plt
nx.draw(graph, with_labels=True)
plt.show()

