import numpy as np
import pygraphviz as pgv
from generate_floor_plan_diagram.graph_info_helper import *

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

test_nodes = [('object_25', {'class_': 'clock', 'location': np.array([-0.86, 10.09, 1.51])}),
              ('object_26', {'class_': 'bench', 'location': np.array([-3.33, 10.48, -1.89])}),
              ('room_5', {'scene_category': 'bedroom', 'floor_number': 'B', 'location': np.array([3.1, 9.11, 1.1])}),
              ('object_4', {'class_': 'sink', 'location': np.array([4.42, 6.52, -1.63])}),
              ('object_10', {'class_': 'refrigerator', 'location': np.array([0.82, 6.18, -1.69])}),
              ('room_7',{'scene_category': 'corridor', 'floor_number': 'A', 'location': np.array([-1.18, 6.02, -1.36])}),
              ('object_19', {'class_': 'cup', 'location': np.array([1.03, 10.05, 0.93])}),
              ('room_2', {'scene_category': 'bathroom', 'floor_number': 'B', 'location': np.array([0.11, 9.61, 1.19])}),
              ('room_15',{'scene_category': 'staircase', 'floor_number': 'A', 'location': np.array([-1.89, 6.8, -0.01])}),
              ('object_7', {'class_': 'sink', 'location': np.array([-0.49, 10.11, 0.2])}),
              ('object_6', {'class_': 'sink', 'location': np.array([0.87, 9.81, 0.72])}),
              ('object_30', {'class_': 'toilet', 'location': np.array([0.41, 10.44, 0.47])}),
              ('object_31', {'class_': 'toilet', 'location': np.array([0.36, 10.44, 0.14])}),
              ('object_8', {'class_': 'refrigerator', 'location': np.array([4.49, 7.32, -1.87])}),
              ('room_4', {'scene_category': 'bedroom', 'floor_number': 'B', 'location': np.array([-3., 9.14, 1.21])}),
              ('room_8', {'scene_category': 'corridor', 'floor_number': 'B', 'location': np.array([0.15, 5.52, 1.2])}),
              ('object_12', {'class_': 'refrigerator', 'location': np.array([3.77, 8.35, -1.22])}),
              ('room_16', {'scene_category': 'storage', 'floor_number': 'A', 'location': np.array([-0.1, 8., -1.2])}),
              ('object_13', {'class_': 'refrigerator', 'location': np.array([3.9, 5.39, -1.2])})]

test_edges = [('room_2', 'room_16', 2.89), ('room_2', 'room_5', 3.03), ('room_2', 'room_4', 3.15),
              ('room_2', 'room_15', 3.65), ('room_2', 'object_6', 0.92), ('room_2', 'object_7', 1.26),
              ('room_2', 'object_19', 1.05), ('room_2', 'object_25', 1.13), ('room_2', 'object_30', 1.14),
              ('room_2', 'object_31', 1.36), ('room_16', 'room_7', 2.26), ('room_16', 'room_15', 2.46),
              ('room_16', 'room_2', 2.89), ('room_16', 'room_8', 3.46), ('room_16', 'object_4', 4.78),
              ('room_16', 'object_8', 4.69), ('room_16', 'object_10', 2.1), ('room_16', 'object_12', 3.89),
              ('room_16', 'object_13', 4.78), ('room_16', 'object_26', 4.13)]


def generate_diagram_from_text_output(text: str, test=False):
    node_list, node_attr_dict = graph_info_helper(text)
    # Create a new graph
    floor_plan_graph = pgv.AGraph(strict=False, directed=False)
    center_node = get_node_name_and_attr(node_list[0], node_attr_dict)

    for node in node_list:
        node_name_and_attr = get_node_name_and_attr(node, node_attr_dict)
        node_position = get_node_pos(node, node_attr_dict)
        if node_is_room(node, node_attr_dict):
            x = np.clip(float((node_position[0] ** 1) * 10), -500, 500)
            y = np.clip(float((node_position[1] ** 1) * 10), -300, 300)
            floor_plan_graph.add_node(node_name_and_attr,
                                      pos=f'{x},{y}',
                                      # pos=f'{float(node_position[0] * 10)},{float(node_position[1] * 10)}',
                                      shape='box', style='filled', fillcolor='lightgreen')
        else:
            w, h = get_node_size(node, node_attr_dict)
            x = np.clip(float((node_position[0] ** 1) * 15), -500, 500)
            y = np.clip(float((node_position[1] ** 1) * 15), -300, 300)
            floor_plan_graph.add_node(node_name_and_attr,
                                      pos=f'{x},{y}',
                                      # pos=f'{float((node_position[0] ** 1) * 15)},{float((node_position[1] ** 1) * 15)}',
                                      width=np.clip(w, 1, 10),
                                      height=np.clip(h, 1, 10),
                                      shape='box', style='filled', fillcolor='lightblue')

    g_node = floor_plan_graph.get_node(center_node)
    g_node.attr['root'] = True
    g_node.attr['fillcolor'] = 'pink'

    for index, node in enumerate(node_list):
        if index != 0:
            leaf = get_node_name_and_attr(node, node_attr_dict)
            floor_plan_graph.add_edge(center_node, leaf)

    # floor_plan_graph.layout(layout="sfdp",beautify=true)

    # Apply beautification options
    # floor_plan_graph.graph_attr.update(beautify=True)

    # Set graph attributes
    floor_plan_graph.graph_attr['layout'] = 'neato'
    floor_plan_graph.graph_attr['splines'] = 'true'
    floor_plan_graph.graph_attr['overlap'] = 'false'
    floor_plan_graph.graph_attr['constraint'] = 'false'

    # Render the UML diagram
    # output_file = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.png"
    # floor_plan_graph.draw(output_file, prog="neato", args='-n2', format="png")
    # floor_plan_graph.draw(output_file, prog="neato", args='-n1', format="png")
    if test:
        output_file = "generated_images/floor_plan_diagram.pdf"
    else:
        output_file = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.pdf"
    # floor_plan_graph.draw(output_file, prog="neato", args='-n2', format="png")
    floor_plan_graph.draw(output_file, prog="neato", args='-n1', format="pdf")

    print(f"UML Class diagram generated: {output_file}")


def generate_fog_of_war_explored_diagram(nodes: list, edges: list, center_node=None, test=False):
    fow_graph = pgv.AGraph(strict=True, directed=False)
    node_name_dict = {}
    for node in nodes:
        # if it is an object node, we ignore
        if 'obj' in node[0]:
            continue
        else:
            node_name = node[0] + '\n scene category: ' + node[1]['scene_category'] + '\n floor number: ' + node[1][
                'floor_number']
            node_name_dict[node[0]] = node_name
            loc = node[1]['location']
            fow_graph.add_node(node_name,
                               pos=f'{loc[0]},{loc[1]}',
                               shape='box', style='filled', fillcolor='lightgreen')

    for edge in edges:
        if 'obj' in edge[0] or 'obj' in edge[1]:
            continue
        else:
            node_name1 = node_name_dict[edge[0]]
            node_name2 = node_name_dict[edge[1]]
            fow_graph.add_edge(node_name1, node_name2)

    if center_node is not None:
        center_node_name = node_name_dict[center_node]
        g_node = fow_graph.get_node(center_node_name)
        g_node.attr['fillcolor'] = 'pink'


    # Set graph attributes
    fow_graph.graph_attr['layout'] = 'neato'
    fow_graph.graph_attr['splines'] = 'true'
    fow_graph.graph_attr['overlap'] = 'false'
    fow_graph.graph_attr['constraint'] = 'false'

    if test:
        output_file = "generated_images/explored_area_diagram.pdf"
    else:
        output_file = "generate_floor_plan_diagram/generated_images/explored_area_diagram.pdf"
    fow_graph.draw(output_file, prog="neato", args='-n1', format="pdf")

    print(f"Explored area diagram generated: {output_file}")


if __name__ == '__main__':
    generate_diagram_from_text_output(test_text, test=True)
    generate_fog_of_war_explored_diagram(test_nodes, test_edges, center_node='room_2', test=True)
