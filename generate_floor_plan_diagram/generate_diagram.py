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


def generate_diagram_from_text_output(text: str):
    node_list, node_attr_dict = graph_info_helper(text)
    # Create a new graph
    floor_plan_graph = pgv.AGraph(strict=False, directed=False)
    center_node = get_node_name_and_attr(node_list[0], node_attr_dict)

    for node in node_list:
        node_name_and_attr = get_node_name_and_attr(node, node_attr_dict)
        node_position = get_node_pos(node, node_attr_dict)
        if node_is_room(node, node_attr_dict):
            floor_plan_graph.add_node(node_name_and_attr,
                                      pos=f'{float(node_position[0] * 150)},{float(node_position[1] * 150)}',
                                      shape='box', style='filled', fillcolor='lightgreen')
        else:
            floor_plan_graph.add_node(node_name_and_attr,
                                      pos=f'{float((node_position[0] ** 1) * 200)},{float((node_position[1] ** 1) * 200)}',
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
    output_file = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.png"
    # floor_plan_graph.draw(output_file, prog="neato", args='-n2', format="png")
    floor_plan_graph.draw(output_file, prog="neato", args='-n1', format="png")


    print(f"UML Class diagram generated: {output_file}")


if __name__ == '__main__':
    generate_diagram_from_text_output(test_text)
