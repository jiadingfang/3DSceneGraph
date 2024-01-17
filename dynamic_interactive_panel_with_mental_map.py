import tkinter as tk
from PIL import Image, ImageTk
from graph_sim import GraphSim
from generate_floor_plan_diagram.generate_diagram import generate_diagram_from_text_output, generate_fog_of_war_explored_diagram
from generate_floor_plan_diagram.graph_info_helper import *
import fitz  # PyMuPDF
import functools
import _pickle as pickle
import os


class GraphSimPanel(GraphSim):
    def get_step_length(self, current_node, next_node):
        return self.graph.edges[(current_node, next_node)]['weight']

    def category_found(self, current_node, target_category):
        if current_node.startswith('object'):
            category_found = target_category == self.graph.nodes[current_node]['class_']
        else:
            category_found = target_category == self.graph.nodes[current_node]['scene_category']

        return category_found

    def panel_scene_text(self, current_node):
        neighbor_nodes = list(self.graph.successors(current_node))
        diagram_text = "=============================================================================\n"
        diagram_text += 'The current place is {} with information {}\n'.format(current_node,
                                                                               self.graph.nodes[current_node])
        diagram_text += 'It has {} number of neighbors: \n'.format(len(neighbor_nodes))
        for i, neighbor_node in enumerate(neighbor_nodes):
            diagram_text += 'The number {} neighbor place is {} with information {}\n'.format(i + 1, neighbor_node,
                                                                                              self.graph.nodes[
                                                                                                  neighbor_node])

        diagram_text += "Please input your desired place to do next from {}: ".format(
            list(range(1, 1 + len(neighbor_nodes))))

        return diagram_text

    def get_explored_place_text(self, trajectory_history, node_info_type='compressed'):
        '''
        Args:
            trajectory_history: string list
            node_info_type: choices=['full', 'compressed', 'compressed_nonmetric']
        Returns:
        '''
        aggregated_graph_edges = self.graph.edges(trajectory_history)
        aggregated_graph_weighted_edges = [(edge[0], edge[1], round(self.graph.edges[edge]['weight'], 2)) for edge in
                                           aggregated_graph_edges]
        aggregated_graph_nodes = functools.reduce(lambda a, b: a | b,
                                                  [set(self.graph.successors(node_name)) for node_name in
                                                   trajectory_history])

        for node_name in trajectory_history:
            aggregated_graph_nodes.add(node_name)

        aggregated_graph_annotated_nodes = [
            (node_name, self.graph_meta.compress_node_info(self.graph.nodes[node_name], node_info_type=node_info_type))
            for node_name in aggregated_graph_nodes]
        return aggregated_graph_annotated_nodes, aggregated_graph_weighted_edges


class InteractivePanel:
    def __init__(self, graph_sim: GraphSimPanel, MAX_STEP: int = 10, source_node: str = 'room_11',
                 target_category: str = 'chair'):
        self.graph_sim = graph_sim
        # Initialize success status
        self.success = False
        # Initialize global variables
        self.buttons_manager = []
        self.trajectory_history = []
        self.trajectory_length = 0
        self.MAX_STEP = MAX_STEP
        self.travel_step = 0
        self.source_node = source_node
        self.target_category = target_category
        self.record = True

        # Creating the main window
        self.root = tk.Tk()
        self.root.title("Floor Plan Detection")

        # For the second PDF
        self.current_zoom_level_left = 1.0
        self.current_zoom_level_pdf_right = 1.0

        # Desired width and height for the displayed image
        self.desired_width = 1000
        self.desired_height = 700

        # Create the main canvas and scrollbars
        self.main_canvas = tk.Canvas(self.root)
        self.v_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.main_canvas.xview)
        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Pack the scrollbars and canvas
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Create a frame inside the main canvas
        self.main_frame = tk.Frame(self.main_canvas)
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor='nw')

        # Set up frames
        self.frame_up = tk.Frame(self.main_frame, width=self.desired_width, height=1000)
        self.frame_mid = tk.Frame(self.main_frame, width=self.desired_width, height=500)
        self.frame_low = tk.Frame(self.main_frame, width=self.desired_width, height=700)

        # Grid configuration for main_frame
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.frame_up.grid(row=0, column=0, sticky='ew')
        self.frame_mid.grid(row=1, column=0, sticky='ew')
        self.frame_low.grid(row=2, column=0, sticky='ew')

        # Place zoom buttons for PDF1
        zoom_in_button_left = tk.Button(self.frame_up, text="Zoom In Left", command=self.zoom_in_pdf_left)
        zoom_in_button_left.grid(row=0, column=0)
        zoom_out_button_left = tk.Button(self.frame_up, text="Zoom Out Left", command=self.zoom_out_pdf_left)
        zoom_out_button_left.grid(row=1, column=0)

        # Place zoom buttons for pdf_right
        zoom_in_button_right = tk.Button(self.frame_up, text="Zoom In Right", command=self.zoom_in_pdf_right)
        zoom_in_button_right.grid(row=0, column=1)
        zoom_out_button_right = tk.Button(self.frame_up, text="Zoom Out Right", command=self.zoom_out_pdf_right)
        zoom_out_button_right.grid(row=1, column=1)

        # Configure the grid columns in frame_up
        self.frame_up.grid_columnconfigure(0, weight=1)  # Column for PDF1
        self.frame_up.grid_columnconfigure(1, weight=1)  # Column for Zoom Buttons of PDF1
        self.frame_up.grid_rowconfigure(0, weight=1)  # Row for Zoom Buttons
        self.frame_up.grid_rowconfigure(1, weight=1)  # Row for PDFs
        self.frame_up.grid_rowconfigure(2, weight=0)  # Row for PDFs

        # Initialization
        self.initialization()

    def onFrameConfigure(self, event=None):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def load_pdf_page(self, pdf_path, page_number=0, zoom_level=1.0):
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        # Select the page
        pdf_page = pdf_document.load_page(page_number)
        # Define the zoom factor and get the pixmap
        zoom_matrix = fitz.Matrix(zoom_level, zoom_level)
        pix = pdf_page.get_pixmap(matrix=zoom_matrix)
        # Convert to a PIL image
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pdf_document.close()
        return image

    def display_pdf_left(self, pdf_path):
        # Load the first page of the PDF
        self.current_pdf_image_left = self.load_pdf_page(pdf_path, zoom_level=self.current_zoom_level_left)
        self.current_pdf_photo_left = ImageTk.PhotoImage(self.current_pdf_image_left)
        self.pdf_image_label_left = tk.Label(self.frame_up, image=self.current_pdf_photo_left)
        self.pdf_image_label_left.grid(row=2, column=0, sticky='nsew')
        # Maintain reference
        self.pdf_image_label_left.photo = self.current_pdf_photo_left

    def display_pdf_right(self, pdf_path):
        # Load the first page of the second PDF
        self.current_pdf_image_right = self.load_pdf_page(pdf_path, zoom_level=self.current_zoom_level_pdf_right)
        self.current_pdf_photo_right = ImageTk.PhotoImage(self.current_pdf_image_right)
        self.pdf_image_label_right = tk.Label(self.frame_up, image=self.current_pdf_photo_right)
        self.pdf_image_label_right.grid(row=2, column=1, sticky='nsew')
        # Maintain reference
        self.pdf_image_label_right.photo = self.current_pdf_photo_right

    def zoom_in_pdf_left(self):
        self.current_zoom_level_left *= 1.25
        self.update_pdf_display()

    def zoom_out_pdf_left(self):
        self.current_zoom_level_left *= 0.8
        self.update_pdf_display()

    def zoom_in_pdf_right(self):
        self.current_zoom_level_pdf_right *= 1.25
        self.update_pdf_display_pdf_right()

    def zoom_out_pdf_right(self):
        self.current_zoom_level_pdf_right *= 0.8
        self.update_pdf_display_pdf_right()

    def update_pdf_display(self):
        # Update the PDF display
        self.current_pdf_image_left = self.load_pdf_page(self.current_pdf_path_left, zoom_level=self.current_zoom_level_left)
        self.current_pdf_photo_left = ImageTk.PhotoImage(self.current_pdf_image_left)
        self.pdf_image_label_left.configure(image=self.current_pdf_photo_left)
        self.pdf_image_label_left.image = self.current_pdf_photo_left  # update the reference

        # Update the scrollable region
        self.onFrameConfigure()

    def update_pdf_display_pdf_right(self):
        self.current_pdf_image_right = self.load_pdf_page(self.current_pdf_path_right,
                                                         zoom_level=self.current_zoom_level_pdf_right)
        self.current_pdf_photo_right = ImageTk.PhotoImage(self.current_pdf_image_right)
        self.pdf_image_label_right.configure(image=self.current_pdf_photo_right)
        self.pdf_image_label_right.image = self.current_pdf_photo_right  # Update the reference

        # Update the scrollable region
        self.onFrameConfigure()

    def record_result(self):
        global result_dir
        result_dir['user_success'] = self.success
        result_dir['user_path_length'] = self.trajectory_length
        result_dir['user_path_trajectory'] = self.trajectory_history
        result_dir['user_steps'] = self.travel_step

        spl_by_distance = int(self.success) * float(result_dir['gt_shortest_path_length']) / self.trajectory_length
        spl_by_steps = int(self.success) * float(len(result_dir['gt_shortest_path_trajectory'])) / self.travel_step

        result_dir['spl_by_distance'] = spl_by_distance
        result_dir['spl_by_steps'] = spl_by_steps

        path = 'generate_floor_plan_diagram/results/' + f'{result_dir["scene_name"]}'
        # Check whether the specified path exists or not
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)

        file_name = 'generate_floor_plan_diagram/results/' + f'{result_dir["scene_name"]}/{result_dir["source_node"]}_to_{result_dir["target_category"]}' + '.txt'
        with open(file_name, 'a') as file:
            file.write(str(result_dir))
            file.write('\n')

        file.close()

    def initialization(self):
        self.trajectory_history.append(self.source_node)
        self.travel_step = 1
        self.trajectory_length = 0

        # generate the first diagram
        scene_output_text = self.graph_sim.panel_scene_text(current_node=self.source_node)
        generate_diagram_from_text_output(text=scene_output_text)

        aggregated_graph_annotated_nodes, aggregated_graph_weighted_edges = self.graph_sim.get_explored_place_text(self.trajectory_history)
        generate_fog_of_war_explored_diagram(nodes=aggregated_graph_annotated_nodes, edges=aggregated_graph_weighted_edges, center_node=self.trajectory_history[-1])

        self.current_zoom_level_left = 1.0
        self.current_zoom_level_pdf_right = 1.0
        self.current_pdf_path_left = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.pdf"  # Change to your PDF path
        self.display_pdf_left(self.current_pdf_path_left)

        self.current_pdf_path_right = "generate_floor_plan_diagram/generated_images/explored_area_diagram.pdf"  # Set this to your second PDF path
        self.display_pdf_right(self.current_pdf_path_right)


        # fill mid frame
        self.greeting = tk.Label(self.frame_mid, text=f"Hello user, let's find ")
        self.greeting.grid(row=0)

        self.target_name = tk.Label(self.frame_mid, text=f"{self.target_category}", bg='white', fg='red', font=14)
        self.target_name.grid(row=1)

        self.traj = tk.Label(self.frame_mid, text=f"Your current path is:{self.trajectory_history}")
        self.traj.grid(row=2)

        self.len_stp = tk.Label(self.frame_mid,
                                text=f"Total length: {round(self.trajectory_length, 4)}, Total steps: {self.travel_step}")
        self.len_stp.grid(row=3)

        self.hint = tk.Label(self.frame_mid, text=f"Choose next place/item you want to visit/select")
        self.hint.grid(row=4)

        # fill the end frame
        node_list, node_attr_dict = graph_info_helper(text=scene_output_text)
        self.create_buttons(node_list[1:])

    def create_buttons(self, neighbor_list: list):
        for button in self.buttons_manager:
            button.destroy()
        self.buttons_manager = []
        # for widget in self.frame_low.winfo_children():
        #     widget.destroy()
        for index, neig in enumerate(neighbor_list):
            button = tk.Button(self.frame_low, text=neig,
                               command=lambda button_text=neig: self.update_interface(button_text))
            c = int(index % 5)
            r = int(index / 5)
            button.grid(row=r, column=c)
            self.buttons_manager.append(button)

    def update_interface(self, button_text):
        previous_node = self.trajectory_history[-1]
        self.trajectory_length += self.graph_sim.get_step_length(previous_node, button_text)
        self.trajectory_history.append(button_text)
        self.travel_step += 1

        if self.travel_step > self.MAX_STEP:
            self.trajectory_length -= self.graph_sim.get_step_length(previous_node, button_text)
            self.trajectory_history = self.trajectory_history[:-1]
            self.travel_step -= 1

            # update image
            self.current_zoom_level_left = 0.5
            self.current_pdf_path_left = "generate_floor_plan_diagram/generated_images/fail.pdf"
            self.display_pdf_left(self.current_pdf_path_left)
            self.current_zoom_level_pdf_right = 0.5
            self.current_pdf_path_right = "generate_floor_plan_diagram/generated_images/fail.pdf"  # Set this to your second PDF path
            self.display_pdf_right(self.current_pdf_path_right)

            for button in self.buttons_manager:
                button.destroy()

            self.greeting.configure(text=f"Sorry, you didn't find {self.target_category} in time!", fg='red', font=20)
            self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
            self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")
            if self.record:
                self.record_result()

            return self.success, self.trajectory_length, self.trajectory_history, self.travel_step

        if 'object' in button_text:
            self.success = (self.graph_sim.graph.nodes[button_text]['class_'] == self.target_category)
            if self.success:
                # generate the first diagram
                self.current_zoom_level_left = 0.5
                self.current_pdf_path_left = "generate_floor_plan_diagram/generated_images/success.pdf"  # Change to your PDF path
                self.display_pdf_left(self.current_pdf_path_left)

                self.current_zoom_level_pdf_right = 0.5
                self.current_pdf_path_right = "generate_floor_plan_diagram/generated_images/success.pdf"  # Set this to your second PDF path
                self.display_pdf_right(self.current_pdf_path_right)
                for button in self.buttons_manager:
                    button.destroy()

                self.greeting.configure(text=f"You've found {self.target_category} successfully!", fg='red', font=20)
                self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
                self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")

                if self.record:
                    self.record_result()
                return self.success, self.trajectory_length, self.trajectory_history, self.travel_step

            else:
                self.current_zoom_level_left = 0.5
                self.current_zoom_level_pdf_right = 0.5
                self.current_pdf_path_left = "generate_floor_plan_diagram/generated_images/fail.pdf"  # Change to your PDF path
                self.display_pdf_left(self.current_pdf_path_left)

                self.current_pdf_path_right = "generate_floor_plan_diagram/generated_images/fail.pdf"  # Set this to your second PDF path
                self.display_pdf_right(self.current_pdf_path_right)
                for button in self.buttons_manager:
                    button.destroy()

                self.greeting.configure(text=f"Sorry, you found the wrong item, we need {self.target_category}!",
                                        fg='red',
                                        font=20)
                self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
                self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")

                if self.record:
                    self.record_result()
                return self.success, self.trajectory_length, self.trajectory_history, self.travel_step

        # generate the first diagram
        scene_output_text = self.graph_sim.panel_scene_text(current_node=button_text)
        generate_diagram_from_text_output(text=scene_output_text)
        self.current_pdf_path_left = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.pdf"  # Change to your PDF path
        self.display_pdf_left(self.current_pdf_path_left)

        aggregated_graph_annotated_nodes, aggregated_graph_weighted_edges = self.graph_sim.get_explored_place_text(
            self.trajectory_history)
        generate_fog_of_war_explored_diagram(nodes=aggregated_graph_annotated_nodes,
                                             edges=aggregated_graph_weighted_edges,
                                             center_node=self.trajectory_history[-1])
        self.current_pdf_path_right = "generate_floor_plan_diagram/generated_images/explored_area_diagram.pdf"  # Set this to your second PDF path
        self.display_pdf_right(self.current_pdf_path_right)

        # update mid frame
        # self.greeting.configure(text=f"Hello user, let's find {self.target_category} step by step")
        self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
        self.len_stp.configure(
            text=f"Total length: {round(self.trajectory_length, 4)}, Total steps: {self.travel_step}")

        # update the end frame
        node_list, node_attr_dict = graph_info_helper(text=scene_output_text)
        self.create_buttons(node_list[1:])

    def run(self, record=True):
        self.record = record
        self.main_frame.bind("<Configure>", self.onFrameConfigure)
        self.root.mainloop()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--user_name', type=str, default='test')
    parser.add_argument('--split_name', type=str, default='medium_automated')
    parser.add_argument('--n_samples_per_scene', type=int, default=5)
    parser.add_argument('--n_neighbors', type=int, default=4)
    parser.add_argument('--llm_model', type=str, default='gpt-4-0613')
    parser.add_argument('--llm_steps_max_adaptive', type=bool, default=True)
    parser.add_argument('--node_info_type', type=str, default='full',
                        choices=['full', 'compressed', 'compressed_nonmetric'])
    parser.add_argument('--debug', type=bool, default=False)
    parser.add_argument('--scene_name', type=str, default='Annona')  # only useful for interactive mode
    parser.add_argument('--source_node', type=str, default='room_4')  # only useful for interactive mode
    parser.add_argument('--target_category', type=str, default='couch')  # only useful for interactive mode
    parser.add_argument('--save_dir', type=str, default='temp')  # only useful for interactive mode
    args = parser.parse_args()

    result_dir = {'user_name': args.user_name,
                  'scene_name': args.scene_name,
                  'source_node': args.source_node,
                  'target_category': args.target_category}

    graph_sim = GraphSimPanel(scene_text_path='scene_text/{}/{}.scn'.format(args.split_name, args.scene_name),
                              n_neighbors=args.n_neighbors, scene_name=args.scene_name, debug=args.debug)

    gt_shortest_path_pair = graph_sim.calc_shortest_path_between_one_node_and_category(source_node=args.source_node,
                                                                                       target_category=args.target_category)

    # traj_list = ['room_2', 'room_16']
    # Nodes, Edges = graph_sim.get_explored_place_text(traj_list, node_info_type='compressed')
    # print(type(Nodes[0][1]))
    # print(Nodes)
    # print(type(Edges))
    # print(Edges)

    result_dir['gt_shortest_path_length'] = gt_shortest_path_pair[0]
    result_dir['gt_shortest_path_trajectory'] = gt_shortest_path_pair[1]

    panel = InteractivePanel(graph_sim=graph_sim,
                             MAX_STEP=10,
                             source_node=args.source_node,
                             target_category=args.target_category)

    panel.run(record=False)
