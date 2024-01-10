import os
from collections import defaultdict

import numpy as np


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


def get_best_and_avg_spl(dict_list):
    curr_dict = dict_list[0]
    scene = curr_dict['scene_name']
    source_node = curr_dict['source_node']
    target_category = curr_dict['target_category']
    gt_shortest_path_length = curr_dict['gt_shortest_path_length']
    gt_shortest_steps = len(curr_dict['gt_shortest_path_trajectory'])

    user_length = []
    user_success = []
    user_steps = []
    user_spl_by_steps = []
    user_spl_by_distance = []
    for curr_dict in dict_list:
        user_length.append(curr_dict['user_path_length'])
        user_success.append(curr_dict['user_success'])
        user_steps.append(curr_dict['user_steps'])
        user_spl_by_steps.append(curr_dict['spl_by_steps'])
        user_spl_by_distance.append(curr_dict['spl_by_distance'])

    user_length = np.array(user_length).mean()
    user_steps = np.array(user_steps).mean()
    user_success = np.array(user_success).mean()
    user_spl_by_distance = np.array(user_spl_by_distance).mean()
    user_spl_by_steps = np.array(user_spl_by_steps).mean()

    print(f"Scene: {scene}  from  {source_node}  to {target_category}\n"
          f"Ground Truth: Length: {gt_shortest_path_length} Steps: {gt_shortest_steps}\n"
          f"User Average Result: Length {user_length} Steps: {user_steps} Success Rate: {user_success}\n"
          f"SPL: Length SPL: {user_spl_by_distance}, Step SPL: {user_spl_by_steps}")
    print('\n')


if __name__ == '__main__':
    file_name = "results"
    dict_list = read_text_files_get_dict_list(file_name)
    # Show I can get all information successfully
    print(dict_list[0])
    print('\n\n\n')

    # Show I can group all dict by selected key
    grouped_dict = group_list_by_key(dict_list, 'scene_name')
    Allen_list = grouped_dict['Allensville']
    for dic in Allen_list:
        print(dic)

    print()

    # Show user performance
    for key, curr_dict_list in grouped_dict.items():
        get_best_and_avg_spl(curr_dict_list)