import re
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

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
            pos = nx.spring_layout(self.graph, seed=7)
            # pos = nx.nx_agraph.graphviz_layout(self.graph)
            nx.draw(self.graph, pos, with_labels=True)
            edge_labels = nx.get_edge_attributes(self.graph, "weight")
            edge_labels = {key: np.round(value, decimals=2) for key, value in edge_labels.items()}
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels)
            plt.show()

    def calc_shortest_path_between_two_nodes(self, source_node, target_node):
        if self.debug:
            print('source_node: ', source_node)
            print('target_ndoe: ', target_node)
        if nx.has_path(self.graph, source=source_node, target=target_node):
            shortest_path_length = nx.shortest_path_length(self.graph, source=source_node, target=target_node, weight='weight')
            shortest_path_node_name_list = nx.shortest_path(self.graph, source=source_node, target=target_node)
            if self.debug:
                print('shortest_path_length: ', shortest_path_length)
                print('shortest_path_node_name_list: ', shortest_path_node_name_list)
            return shortest_path_length, shortest_path_node_name_list
        else:
            if self.debug:
                print('no valid path, return inf and []')
            return np.inf, []
        
    def calc_shortest_path_between_one_node_and_category(self, source_node, target_category):
        if self.debug:
            print('source_node: ', source_node)
            print('target_category: ', target_category)
        
        # find target nodes that matches the category name in object or room list
        target_nodes = [node_name for node_name in self.room_node_name_list if target_category == self.graph.nodes[node_name]['scene_category']]
        target_nodes += [node_name for node_name in self.object_node_name_list if target_category == self.graph.nodes[node_name]['class_']]
        if self.debug:
            print('target_nodes: ', target_nodes)

        shortest_path_list = []
        for target_node_name in target_nodes:
            shortest_path_pair = self.calc_shortest_path_between_two_nodes(source_node=source_node, target_node=target_node_name)
            shortest_path_list.append(shortest_path_pair)
        
        # find the shortest "shortest path" among all target nodes
        if len(shortest_path_list) > 0:
            sorted_shortest_path_list = sorted(shortest_path_list, key=lambda x:x[0], reverse=False)
            target_shortest_path_pair = sorted_shortest_path_list[0]
            if self.debug:
                print('target_shortest_path_pair: ', target_shortest_path_pair)
            return target_shortest_path_pair
        else:
            return np.inf, []
        
    def interactive_category_finding(self, source_node, target_category):
        if self.debug:
            print('source_node: ', source_node)
            print('target_category: ', target_category)
        
        travel_steps = 0
        category_found = False
        current_node = source_node
        trajectory_list = [current_node]
        trajectory_length = 0

        while not category_found and travel_steps < 10:
            neighbor_nodes = list(self.graph.successors(current_node))
            print("=============================================================================")
            print('The current place is {} with information {}'.format(current_node, self.graph.nodes[current_node]))
            print('You have visted places {}: '.format(trajectory_list))
            print('It has {} number of neighbors: '.format(len(neighbor_nodes)))
            for i, neighbor_node in enumerate(neighbor_nodes):
                print('The number {} neighbor place is {} with information {}'.format(i+1, neighbor_node, self.graph.nodes[neighbor_node]))
            next_id = int(input("Please input your desired place to do next from {}: ".format(list(range(1, 1 + len(neighbor_nodes))))))
            next_node = neighbor_nodes[next_id - 1]
            if next_node.startswith('object'):
                category_found = target_category == self.graph.nodes[next_node]['class_']
            else:
                category_found = target_category == self.graph.nodes[next_node]['scene_category']
            
            trajectory_list.append(next_node)
            trajectory_length += self.graph.edges[(current_node, next_node)]['weight']

            travel_steps += 1
            current_node = next_node
        
        print('trajectory length: ', trajectory_length)
        print('trajectory_list: ', trajectory_list)

        return trajectory_length, trajectory_list

if __name__=='__main__':
    split = 'tiny_automated'
    scene_name = 'Allensville'
    scene_text_path = 'scene_text/{}/{}.scn'.format(split, scene_name)
    graph_sim = GraphSim(scene_text_path=scene_text_path, n_neighbords=3, scene_name=scene_name, debug=True)
    # graph_sim.calc_shortest_path_between_two_nodes(source_node='object_7', target_node='object_28')
    graph_sim.calc_shortest_path_between_one_node_and_category(source_node='object_7', target_category='chair')
    graph_sim.interactive_category_finding(source_node='object_7', target_category='chair')