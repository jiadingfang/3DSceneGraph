import re
import json
import numpy as np
import networkx as nx

class GraphSim:
    """
    Scene graph structured as networkx object. Allows agent traversing as simulator.
    """
    def __init__(self, scene_text_path, n_neighbords=3, scene_name=None, debug=True):
        # hyper parameters
        self.n_neighbors = n_neighbords
        self.debug = debug

        # load scene text
        with open(scene_text_path) as f:
            self.scene_text = f.read()

        # use json to load text
        self.scene_data = json.loads(self.scene_text)
        if self.debug:
            print('num of objects: ', len(self.scene_data['objects']))
            print('num of rooms: ', len(self.scene_data['rooms']))

        # create networkx
        self.graph = nx.DiGraph(scene=scene_name)

        # Add nodes for each room  
        for object_dict in self.scene_data['rooms']:
            id = object_dict['id']
            node_name = 'room_{}'.format(id)
            self.graph.add_node(node_name, type='room')
            for key, value in object_dict.items():
                self.graph.nodes[node_name][key] = value
            # initialize child_objects list
            self.graph.nodes[node_name]['child_objects'] = []

        # Add nodes for each object
        for object_dict in self.scene_data['objects']:
            id = object_dict['id']
            node_name = 'object_{}'.format(id)
            self.graph.add_node(node_name, type='object')
            for key, value in object_dict.items():
                self.graph.nodes[node_name][key] = value
                
                # add child objects information for each room
                if key == 'parent_room':
                    parent_room_name = 'room_' + str(value)
                    self.graph.nodes[parent_room_name]['child_objects'].append(node_name)

        # prepare node lists for objects and rooms
        self.object_node_name_list = [node_name for node_name in self.graph.nodes if 'object' in node_name]
        self.room_node_name_list = [node_name for node_name in self.graph.nodes if 'room' in node_name]

        # Add edge between neighbor rooms
        for i in range(len(self.room_node_name_list)):
            # for j in range(i+1, len(room_node_name_list)):
            room_distance_dict = {}
            for j in range(len(self.room_node_name_list)):
                if i == j:
                    continue
                room_name_a = self.room_node_name_list[i]
                room_name_b = self.room_node_name_list[j]
                room_node_a = self.graph.nodes[room_name_a]
                room_node_b = self.graph.nodes[room_name_b]
                room_a_location = np.array(room_node_a['location'])
                room_b_location = np.array(room_node_b['location'])
                distance_room_a_room_b = np.linalg.norm(room_a_location - room_b_location)
                # print('distance_room_a_room_b: ', distance_room_a_room_b)
                room_distance_dict[(room_name_a, room_name_b)] = distance_room_a_room_b
            
            # filter out the top closest edges to add tothe graph
            sorted_room_distance_list = sorted(room_distance_dict.items(), key=lambda x:x[1], reverse=False)
            for i in range(min(self.n_neighbors, len(sorted_room_distance_list))):
                room_distance_pair = sorted_room_distance_list[i]
                # print('room_distance_pair: ', room_distance_pair)
                self.graph.add_edge(*room_distance_pair[0], weight=room_distance_pair[1])
        if self.debug:
            print('graph stats after adding edges between rooms: ', self.graph)


        # Add edges between objects in a room
        for room_node_name in self.room_node_name_list:
            room_node = self.graph.nodes[room_node_name]
            child_objects_list = room_node['child_objects']

            for i in range(len(child_objects_list)):
                object_distance_dict = {}
                for j in range(len(child_objects_list)):
                    if i == j:
                        continue
                    child_name_a = child_objects_list[i]
                    child_name_b = child_objects_list[j]
                    child_node_a = self.graph.nodes[child_name_a]
                    child_node_b = self.graph.nodes[child_name_b]
                    # print('child_node_a: ', child_node_a)
                    object_a_location = np.array(child_node_a['location'])
                    object_b_location = np.array(child_node_b['location'])
                    # print('object_a_location: ', object_a_location)
                    distaance_object_a_object_b = np.linalg.norm(object_a_location - object_b_location)
                    # print('distaance_object_a_object_b: ', distaance_object_a_object_b)
                    object_distance_dict[(child_name_a, child_name_b)] = distaance_object_a_object_b

                # filter out the top closest edges to add to the graph
                sorted_object_distance_list = sorted(object_distance_dict.items(), key=lambda x:x[1], reverse=False)
                for i in range(min(self.n_neighbors, len(sorted_object_distance_list))):
                    object_distance_pair = sorted_object_distance_list[i]
                    # print('object_distance_pair: ', object_distance_pair)
                    self.graph.add_edge(*object_distance_pair[0], weight=object_distance_pair[1])
        if self.debug:
            print('graph stats after adding edges between objects in a room: ', self.graph)

        # Add a loop edge between a room and the closest object in this room (so the agent can go in and out of a room)
        for room_node_name in self.room_node_name_list:
            room_node = self.graph.nodes[room_node_name]
            room_location = np.array(room_node['location'])
            room_objects_distance_dict = {}
            if len(room_node['child_objects']) > 0:
                for object_name in room_node['child_objects']:
                    object_node = self.graph.nodes[object_name]
                    object_location = np.array(object_node['location'])
                    room_object_distance = np.linalg.norm(room_location - object_location)
                    room_objects_distance_dict[(room_node_name, object_name)] = room_object_distance

                # find the closest object to room location and add loop edge
                sorted_room_object_distance_list = sorted(room_objects_distance_dict.items(), key=lambda x:x[1], reverse=False)
                room_object_pair = sorted_room_object_distance_list[0]
                room_name, object_name = room_object_pair[0]
                room_object_distance = room_object_pair[1]
                self.graph.add_edge(room_name, object_name, weight=room_object_distance)
                self.graph.add_edge(object_name, room_name, weight=room_object_distance)
        if self.debug:
            print('graph stats after adding edges between object and room: ', self.graph)

        # visualization
        if self.debug:
            import matplotlib.pyplot as plt
            nx.draw(self.graph, with_labels=True)
            plt.show()


if __name__=='__main__':
    split = 'tiny_automated'
    scene_name = 'Allensville'
    scene_text_path = 'scene_text/{}/{}.scn'.format(split, scene_name)
    graph_sim = GraphSim(scene_text_path)