import pygraphviz as pgv

# Create a new graph
uml_graph = pgv.AGraph(strict=False, directed=True)

classA = "ClassA\nattribute1: int\nmethod1()"
# Add classes to the graph
uml_graph.add_node(classA, shape="rectangle")
uml_graph.add_node("ClassB", shape="rectangle")

# Add inheritance relationship
uml_graph.add_edge("ClassB", classA, arrowhead="onormal")

# Add attributes and methods
uml_graph.add_node("attribute1: int", shape="oval", style="dashed")
uml_graph.add_node("method1()", shape="oval", style="dashed")
uml_graph.add_edge("ClassA", "attribute1: int", arrowhead="none")
uml_graph.add_edge("ClassA", "method1()", arrowhead="none")

# Render the UML diagram
output_file = "uml_class_diagram.png"
uml_graph.draw(output_file, prog="dot", format="png")

print(f"UML Class diagram generated: {output_file}")