import os
from collections import defaultdict
import numpy as np
import json


class colors:
    # ANSI color codes for text formatting
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


def read_text_files_get_dict_list(directory):
    dict_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as txt_file:
                    # print(f"Reading contents of {file_path}:")
                    for line in txt_file:
                        dict_list.append(eval(line))  # Process each line here

    return dict_list


def group_list_by_key(ori_dict, key_text):
    """
    # suggested key text:
    'user_name' : check how good single user act
    'scene_name' : compare between user and chatgpt
    'user_success' : check total success rate over all tasks
    """
    grouped_data = defaultdict(list)

    # Group the data by the 'group' attribute
    for item in ori_dict:
        grouped_data[item[key_text]].append(item)

    # Print the grouped data
    # for key, group in grouped_data.items():
    #     print(f"Group {key}:")
    #     for item in group:
    #         print(item)
    #     print()

    return grouped_data


def get_gt_user_llm_result(dict_list, print_result=False):
    curr_dict = dict_list[0]
    scene = curr_dict['scene_name']
    source_node = curr_dict['source_node']
    target_category = curr_dict['target_category']
    gt_shortest_path_length = curr_dict['gt_shortest_path_length']
    gt_shortest_steps = len(curr_dict['gt_shortest_path_trajectory'])

    raw_user_length = []
    user_success = []
    raw_user_steps = []
    raw_user_spl_by_steps = []
    raw_user_spl_by_distance = []
    for curr_dict in dict_list:
        user_success.append(curr_dict['user_success'])
        # if not success, we skip this case, because the path_length is meaningless
        if curr_dict['user_success']:
            raw_user_length.append(curr_dict['user_path_length'])
            raw_user_steps.append(curr_dict['user_steps'])
        raw_user_spl_by_steps.append(curr_dict['spl_by_steps'])
        raw_user_spl_by_distance.append(curr_dict['spl_by_distance'])

    if len(raw_user_length):
        user_length = np.array(raw_user_length).mean()
        user_steps = np.array(raw_user_steps).mean()
        user_length_var = np.array(raw_user_length).std()
        user_steps_var = np.array(raw_user_steps).std()
    else:
        user_length = 0
        user_steps = 0
        user_length_var = 0
        user_steps_var = 0

    user_success = np.array(user_success).mean()
    user_spl_by_distance = np.array(raw_user_spl_by_distance).mean()
    user_spl_by_steps = np.array(raw_user_spl_by_steps).mean()
    user_spl_by_distance_var = np.array(raw_user_spl_by_distance).std()
    user_spl_by_steps_var = np.array(raw_user_spl_by_steps).std()

    for root, dirs, files in os.walk(
            f'logs/split_tiny_automated-model_gpt-4-neighbors_4/{scene}/source_node-{source_node}_target_category-{target_category}'):
        for file in files:
            if file.startswith('metrics'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as json_file:
                    llm_dict_gpt4 = json.load(json_file)

    if llm_dict_gpt4['llm_shortest_path_length'] != np.inf:
        llm_length_gpt4 = float(llm_dict_gpt4['llm_shortest_path_length'])
        llm_steps_gpt4 = len(llm_dict_gpt4['llm_shortest_path_trajectory'])
        llm_success_gpt4 = True
    else:
        llm_length_gpt4 = 0
        llm_steps_gpt4 = int(0)
        llm_success_gpt4 = False

    llm_spl_by_distance_gpt4 = llm_dict_gpt4['spl_by_distance']
    llm_spl_by_steps_gpt4 = llm_dict_gpt4['spl_by_steps']

    if print_result:
        print(
            f"Scene: {colors.RED} {scene} {colors.RESET} from {colors.RED} {source_node} {colors.RESET} to {colors.RED} {target_category} {colors.RESET}\n"
            f"Ground Truth: Length: {colors.BLUE} {gt_shortest_path_length:.3f} {colors.RESET} Steps: {colors.YELLOW} {gt_shortest_steps} {colors.RESET}\n"
            "\n"
            f"User Average Result: Length {colors.BLUE} {user_length:.3f} {colors.RESET}, Steps: {colors.YELLOW} {user_steps:.3f} {colors.RESET} Success Rate: {colors.GREEN} {user_success:.3f} {colors.RESET}\n"
            f"User SPL: Length SPL: {user_spl_by_distance:.3f}, Step SPL: {user_spl_by_steps:.3f}\n"
            "\n"
            f"LLM gpt4 Result: Length: {colors.BLUE} {llm_length_gpt4:.3f} {colors.RESET}, Steps:{colors.YELLOW} {llm_steps_gpt4} {colors.RESET} Success: {colors.GREEN} {llm_success_gpt4} {colors.RESET}\n"
            f"LLM gpt4 SPL: Length SPL: {llm_spl_by_distance_gpt4:.3f}, Step SPL: {llm_spl_by_steps_gpt4:.3f}")
        print('\n')

    result_dict = {'scene': scene,
                   'source_node': source_node,
                   'target_category': target_category,
                   'gt_shortest_path_length': gt_shortest_path_length,
                   'gt_shortest_steps': gt_shortest_steps,
                   'user_length': user_length,
                   'user_steps': user_steps,
                   'user_success': user_success,
                   'user_spl_by_distance': user_spl_by_distance,
                   'user_spl_by_steps': user_spl_by_steps,
                   'llm_length_gpt4': llm_length_gpt4,
                   'llm_steps_gpt4': llm_steps_gpt4,
                   'llm_success_gpt4': llm_success_gpt4,
                   'llm_spl_by_distance_gpt4': llm_spl_by_distance_gpt4,
                   'llm_spl_by_steps_gpt4': llm_spl_by_steps_gpt4,
                   'user_length_var': user_length_var,
                   'user_steps_var': user_steps_var,
                   'user_spl_by_distance_var': user_spl_by_distance_var,
                   'user_spl_by_steps_var': user_spl_by_steps_var}

    return result_dict


if __name__ == '__main__':
    current_directory = os.getcwd()
    print(current_directory)
    folder_name = "results"
    dict_list = read_text_files_get_dict_list(folder_name)
    # Show I can get all information successfully
    # print(dict_list[0])
    # print('\n\n\n')

    grouped_dict = group_list_by_key(dict_list, 'scene_name')
    # Show I can group all dict by selected key
    # Allen_list = grouped_dict['Allensville']
    # for dic in Allen_list:
    #     print(dic)
    #
    # print()

    # Show user performance
    for key, curr_dict_list in grouped_dict.items():
        get_gt_user_llm_result(curr_dict_list, print_result=True)
