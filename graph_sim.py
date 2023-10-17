import os
import json
import numpy as np
import networkx as nx
from datetime import datetime
import matplotlib.pyplot as plt

from llm_call import CompletionCall, ChatCompletionCall
from graphs import GraphTypeOne, GraphTypeTwo

class GraphSim:
    """
    Scene graph structured as networkx object. Allows agent traversing as simulator.
    """
    def __init__(self, scene_text_path, n_neighbors=3, scene_name=None, debug=True):
        # hyper parameters
        self.n_neighbors = n_neighbors
        self.scene_name = scene_name
        self.debug = debug

        # load scene text
        with open(scene_text_path) as f:
            self.scene_text = f.read()

        # use json to load text
        self.scene_data = json.loads(self.scene_text)
        
        # create graph
        # self.graph = GraphTypeOne(scene_data=self.scene_data, n_neighbors=self.n_neighbors, scene_name=self.scene_name, debug=self.debug).graph
        graph_meta = GraphTypeTwo(scene_data=self.scene_data, n_neighbors=self.n_neighbors, scene_name=self.scene_name, debug=self.debug)
        self.graph = graph_meta.graph
        self.graph_description = graph_meta.graph_description

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
        object_node_name_list = [node_name for node_name in self.graph.nodes if 'object' in node_name]
        room_node_name_list = [node_name for node_name in self.graph.nodes if 'room' in node_name]

        target_nodes = [node_name for node_name in room_node_name_list if target_category == self.graph.nodes[node_name]['scene_category']]
        target_nodes += [node_name for node_name in object_node_name_list if target_category == self.graph.nodes[node_name]['class_']]
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
                # print('target_shortest_path_pair: ', target_shortest_path_pair)
                print('shortest path length: ', target_shortest_path_pair[0])
                print('shortest path trajectory: ', target_shortest_path_pair[1])
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
        
        if self.debug:
            print('trajectory length: ', trajectory_length)
            print('trajectory_list: ', trajectory_list)

        return trajectory_length, trajectory_list
    
    def llm_category_finding(self, source_node, target_category, save_dir=None):
        if self.debug:
            print('source_node: ', source_node)
            print('target_category: ', target_category)
        
        travel_steps = 0
        category_found = False
        current_node = source_node
        trajectory_list = [current_node]
        trajectory_length = 0

        if save_dir is not None:
            save_list = []

        while not category_found and travel_steps < 10:                
            neighbor_nodes = list(self.graph.successors(current_node))
            prompt = "You are travel in a new unknown environment."
            prompt += "The environment is represented as a graph."
            prompt += self.graph_description
            prompt += "Your task is to find an object in the category '{}' with shortest path possible\n.".format(target_category)
            prompt += 'You have visted places {}: \n'.format(trajectory_list)
            prompt += 'The current place is {} with information {}\n'.format(current_node, self.graph.nodes[current_node])
            prompt += 'It has {} number of neighbors: \n'.format(len(neighbor_nodes))
            for i, neighbor_node in enumerate(neighbor_nodes):
                prompt += 'The number {} neighbor place is {} with information {}\n'.format(i+1, neighbor_node, self.graph.nodes[neighbor_node])
            prompt += "Please answer your desired place to go next from the neghbor list of {}. Reason about it step by step. At the end of your reasoning, output the neighbor name with the format of a python dictionary with key 'choice' and value the name of chosen neighbor.".format(neighbor_nodes)

            # import pdb; pdb.set_trace()

            # response_text, llm_response = CompletionCall(prompt=prompt)
            # response_text, llm_response = ChatCompletionCall(prompt=prompt, model='gpt-4')
            response_text, llm_response = ChatCompletionCall(prompt=prompt, model='gpt-3.5-turbo')

            if save_dir is not None:
                save_list.append({'role':'user', 'content': prompt})
                save_list.append({'role': 'assistant', 'content': response_text})

            if self.debug:
                print("==============================================================")
                print('prompt: ', prompt)
                print('llm_response: ', llm_response)
            
            # try getting answer from llm response
            try:
                next_node = eval('{' + response_text.split('{')[1].split('}')[0] + '}')['choice']
                if next_node.startswith('object'):
                    category_found = target_category == self.graph.nodes[next_node]['class_']
                else:
                    category_found = target_category == self.graph.nodes[next_node]['scene_category']
                trajectory_length += self.graph.edges[(current_node, next_node)]['weight']
                trajectory_list.append(next_node)

            except Exception as e:
                if self.debug:
                    print('llm running error: ', e)
                return np.inf, trajectory_list

            travel_steps += 1
            current_node = next_node

        if self.debug:        
            print('trajectory length: ', trajectory_length)
            print('trajectory_list: ', trajectory_list)

        if save_dir is not None:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            timestamp = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            save_name = 'llm_responses_scene_name_{}_source_node_{}_target_category_{}_{}.json'.format(self.scene_name, source_node, target_category, timestamp)
            json_object = json.dumps(save_list, indent=4)
            with open(os.path.join(save_dir, save_name), 'w', encoding ='utf8') as json_file: 
                # json.dumps(save_list, json_file)
                json_file.write(json_object)

        return trajectory_length, trajectory_list
    
    def run_one_sample(self, source_node, target_category, save_dir=None):

        if self.debug:
            print('source node: ', source_node)
            print('target category: ', target_category)

        gt_shortest_path_length, gt_shortest_path_trajectory = self.calc_shortest_path_between_one_node_and_category(source_node=source_node, target_category=target_category)
        llm_shortest_path_length, llm_shortest_path_trajectory = self.llm_category_finding(source_node=source_node, target_category=target_category)

        # calculate metrics
        log_dict = {}
        log_dict['gt_shortest_path_length'] = gt_shortest_path_length
        log_dict['gt_shortest_path_trajectory'] = gt_shortest_path_trajectory
        log_dict['llm_shortest_path_length'] = llm_shortest_path_length
        log_dict['llm_shortest_path_trajectory'] = llm_shortest_path_trajectory

        # SPL(Success weighted by (normalized inverse) Path Length), https://arxiv.org/pdf/1807.06757.pdf
        spl_by_distance = gt_shortest_path_length / llm_shortest_path_length
        spl_by_steps = len(gt_shortest_path_trajectory) / len(llm_shortest_path_trajectory) if not np.isinf(llm_shortest_path_length) else 0.0
        log_dict['spl_by_distance'] = spl_by_distance
        log_dict['spl_by_steps'] = spl_by_steps

        if save_dir is not None:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            timestamp = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            save_name = 'run_log_scene_name_{}_source_node_{}_target_category_{}_{}.json'.format(self.scene_name, source_node, target_category, timestamp)
            json_object = json.dumps(log_dict, indent=4)
            with open(os.path.join(save_dir, save_name), 'w', encoding ='utf8') as json_file: 
                # json.dumps(save_list, json_file)
                json_file.write(json_object)


if __name__=='__main__':
    split = 'tiny_automated'
    scene_name = 'Allensville'
    scene_text_path = 'scene_text/{}/{}.scn'.format(split, scene_name)
    graph_sim = GraphSim(scene_text_path=scene_text_path, n_neighbors=3, scene_name=scene_name, debug=True)
    # gt_shortest_path_pair = graph_sim.calc_shortest_path_between_one_node_and_category(source_node='room_11', target_category='chair')
    # graph_sim.interactive_category_finding(source_node='room_11', target_category='chair')
    # llm_shortest_path_pair = graph_sim.llm_category_finding(source_node='room_11', target_category='chair', save_dir='llm_responses')
    # print('gt shortest path length: ', gt_shortest_path_pair[0])
    # print('gt shortest path trajectory: ', gt_shortest_path_pair[1])
    # print('llm shortest path length: ', llm_shortest_path_pair[0])
    # print('llm shortest path trajectory: ', llm_shortest_path_pair[1])
    graph_sim.run_one_sample(source_node='room_11', target_category='chair', save_dir='runs')