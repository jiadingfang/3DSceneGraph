import tkinter as tk
from PIL import Image, ImageTk
from graph_sim import GraphSim
from generate_floor_plan_diagram.generate_diagram import generate_diagram_from_text_output
from generate_floor_plan_diagram.graph_info_helper import *
import _pickle as pickle


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

        # Creating the main window
        self.root = tk.Tk()
        self.root.title("Floor Plan Detection")

        # Desired width and height for the displayed image
        self.desired_width = 1000
        self.desired_height = 800

        self.frame_up = tk.Frame(self.root, width=self.desired_width, height=1000)
        self.frame_up.pack()
        self.frame_mid = tk.Frame(self.root, width=self.desired_width, height=500)
        self.frame_mid.pack()
        self.frame_low = tk.Frame(self.root, width=self.desired_width, height=700)
        self.frame_low.pack()

        # Initialization
        self.initialization()

    def resize_image(self, image: Image):
        original_width, original_height = image.size
        according_width= int((self.desired_height/original_height) * original_width)
        image = image.resize((according_width, self.desired_height))
        return image

    def record_result(self):
        global result_dir
        result_dir['user_success'] = self.success
        result_dir['user_path_length'] = self.trajectory_length
        result_dir['user_path_trajectory'] = self.trajectory_history
        result_dir['user_steps'] = self.travel_step

        file_name = 'generate_floor_plan_diagram/results/'+result_dir['user_name']+'_result.txt'
        with open(file_name, 'a') as file:
            file.write(str(result_dir))
            file.write('\n')

        file.close()


    def initialization(self):
        self.trajectory_history.append(self.source_node)
        self.travel_step = 0
        self.trajectory_length = 0

        # generate the first diagram
        scene_output_text = self.graph_sim.panel_scene_text(current_node=self.source_node)

        # init image
        generate_diagram_from_text_output(text=scene_output_text)

        floorplan_image_path = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.png"  # Change this to your initial PNG file path
        floorplan_image = Image.open(floorplan_image_path)
        # Calculate the new height based on the specified width
        floorplan_image = self.resize_image(floorplan_image)
        floorplan_image = ImageTk.PhotoImage(floorplan_image)
        self.floorplan_image_label = tk.Label(self.frame_up, image=floorplan_image)
        self.floorplan_image_label.image = floorplan_image
        self.floorplan_image_label.pack()

        # fill mid frame
        self.greeting = tk.Label(self.frame_mid, text=f"Hello user, let's find {self.target_category} step by step")
        self.greeting.grid(row=0)

        self.traj = tk.Label(self.frame_mid, text=f"Your current path is:{self.trajectory_history}")
        self.traj.grid(row=1)

        self.len_stp = tk.Label(self.frame_mid,
                                text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")
        self.len_stp.grid(row=2)

        self.hint = tk.Label(self.frame_mid, text=f"Choose next place/item you want to visit/select")
        self.hint.grid(row=3)

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
            c = int(index % 4)
            r = int(index / 4)
            button.grid(row=r, column=c)
            self.buttons_manager.append(button)

    def update_interface(self, button_text):
        previous_node = self.trajectory_history[-1]
        self.trajectory_length += self.graph_sim.get_step_length(previous_node, button_text)
        self.trajectory_history.append(button_text)
        self.travel_step += 1
        if self.travel_step > self.MAX_STEP:
            # generate the first diagram
            scene_output_text = self.graph_sim.panel_scene_text(current_node=self.source_node)

            # update image
            generate_diagram_from_text_output(text=scene_output_text)

            floorplan_image_path = "generate_floor_plan_diagram/generated_images/fail.png"  # Change this to your initial PNG file path
            floorplan_image = Image.open(floorplan_image_path)
            # Calculate the new height based on the specified width
            floorplan_image = self.resize_image(floorplan_image)
            floorplan_image = ImageTk.PhotoImage(floorplan_image)
            self.floorplan_image_label.configure(image=floorplan_image)
            self.floorplan_image_label.image = floorplan_image
            for button in self.buttons_manager:
                button.destroy()

            self.greeting.configure(text=f"Sorry, you didn't find {self.target_category} in time!", fg='red', font=20)
            self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
            self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")
            self.record_result()

            return self.success, self.trajectory_length, self.trajectory_history, self.travel_step

        if 'object' in button_text:
            self.success = (self.graph_sim.graph.nodes[button_text]['class_'] == self.target_category)
            if self.success:
                # generate the first diagram
                scene_output_text = self.graph_sim.panel_scene_text(current_node=self.source_node)

                # update image
                generate_diagram_from_text_output(text=scene_output_text)

                floorplan_image_path = "generate_floor_plan_diagram/generated_images/success.png"  # Change this to your initial PNG file path
                floorplan_image = Image.open(floorplan_image_path)
                floorplan_image = self.resize_image(floorplan_image)
                floorplan_image = ImageTk.PhotoImage(floorplan_image)
                self.floorplan_image_label.configure(image=floorplan_image)
                self.floorplan_image_label.image = floorplan_image
                for button in self.buttons_manager:
                    button.destroy()

                self.greeting.configure(text=f"You've found {self.target_category} successfully!", fg='red', font=20)
                self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
                self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")

                self.record_result()
                return self.success, self.trajectory_length, self.trajectory_history, self.travel_step

            else:
                floorplan_image_path = "generate_floor_plan_diagram/generated_images/fail.png"  # Change this to your initial PNG file path
                floorplan_image = Image.open(floorplan_image_path)
                floorplan_image = self.resize_image(floorplan_image)
                floorplan_image = ImageTk.PhotoImage(floorplan_image)
                self.floorplan_image_label.configure(image=floorplan_image)
                self.floorplan_image_label.image = floorplan_image
                for button in self.buttons_manager:
                    button.destroy()

                self.greeting.configure(text=f"Sorry, you found the wrong item, we need {self.target_category}!", fg='red',
                                        font=20)
                self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
                self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")

                self.record_result()
                return self.success, self.trajectory_length, self.trajectory_history, self.travel_step


        # generate the first diagram
        scene_output_text = self.graph_sim.panel_scene_text(current_node=button_text)

        # update image
        generate_diagram_from_text_output(text=scene_output_text)

        floorplan_image_path = "generate_floor_plan_diagram/generated_images/floor_plan_diagram.png"  # Change this to your initial PNG file path
        floorplan_image = Image.open(floorplan_image_path)
        # Calculate the new height based on the specified width
        floorplan_image = self.resize_image(floorplan_image)
        floorplan_image = ImageTk.PhotoImage(floorplan_image)
        self.floorplan_image_label.configure(image=floorplan_image)
        self.floorplan_image_label.image = floorplan_image

        # update mid frame
        self.greeting.configure(text=f"Hello user, let's find {self.target_category} step by step")
        self.traj.configure(text=f"Your current path is:{self.trajectory_history}")
        self.len_stp.configure(text=f"Total Length: {self.trajectory_length}, Total steps: {self.travel_step}")

        # update the end frame
        node_list, node_attr_dict = graph_info_helper(text=scene_output_text)
        self.create_buttons(node_list[1:])

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--user_name', type=str, default='luzhe')
    parser.add_argument('--split_name', type=str, default='tiny_automated')
    parser.add_argument('--n_samples_per_scene', type=int, default=5)
    parser.add_argument('--n_neighbors', type=int, default=4)
    parser.add_argument('--llm_model', type=str, default='gpt-4-0613')
    parser.add_argument('--llm_steps_max_adaptive', type=bool, default=True)
    parser.add_argument('--debug', type=bool, default=False)
    parser.add_argument('--scene_name', type=str, default='Allensville')  # only useful for interactive mode
    parser.add_argument('--source_node', type=str, default='room_11')  # only useful for interactive mode
    parser.add_argument('--target_category', type=str, default='chair')  # only useful for interactive mode
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

    result_dir['gt_shortest_path_length'] = gt_shortest_path_pair[0]
    result_dir['gt_shortest_path_trajectory'] = gt_shortest_path_pair[1]

    panel = InteractivePanel(graph_sim=graph_sim,
                             MAX_STEP=10,
                             source_node=args.source_node,
                             target_category=args.target_category)

    panel.run()


