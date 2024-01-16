from generate_floor_plan_diagram.result_info_helper import *
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':

    folder_name = "generate_floor_plan_diagram/results"

    # read all user result
    dict_list = read_text_files_get_dict_list(folder_name)
    # group all result by scene name
    grouped_dict = group_list_by_key(dict_list, 'scene_name')

    x_scene_name = []

    y1_gt_path_length = []
    y1_user_path_length_avg = []
    y1_user_path_length_var = []
    y1_gpt4_path_length = []

    y2_gt_steps = []
    y2_user_steps_avg = []
    y2_user_steps_var = []
    y2_gpt4_steps = []

    y3_user_dis_spl_avg = []
    y3_user_dis_spl_var = []
    y3_gpt4_dis_spl = []

    y4_user_steps_spl_avg = []
    y4_user_steps_spl_var = []
    y4_gpt4_steps_spl = []

    for key, curr_dict_list in grouped_dict.items():
        curr_res_dict = get_gt_user_llm_result(curr_dict_list)
        x_scene_name.append(curr_res_dict['scene'])

        y1_gt_path_length.append(curr_res_dict['gt_shortest_path_length'])
        y1_user_path_length_avg.append(curr_res_dict['user_length'])
        y1_user_path_length_var.append(curr_res_dict['user_length_var'])
        y1_gpt4_path_length.append(curr_res_dict['llm_length_gpt4'])

        y2_gt_steps.append(curr_res_dict['gt_shortest_steps'])
        y2_user_steps_avg.append(curr_res_dict['user_steps'])
        y2_user_steps_var.append(curr_res_dict['user_steps_var'])
        y2_gpt4_steps.append(curr_res_dict['llm_steps_gpt4'])

        y3_user_dis_spl_avg.append(curr_res_dict['user_spl_by_distance'])
        y3_user_dis_spl_var.append(curr_res_dict['user_spl_by_distance_var'])
        y3_gpt4_dis_spl.append(curr_res_dict['llm_spl_by_distance_gpt4'])

        y4_user_steps_spl_avg.append(curr_res_dict['user_spl_by_steps'])
        y4_user_steps_spl_var.append(curr_res_dict['user_spl_by_steps_var'])
        y4_gpt4_steps_spl.append(curr_res_dict['llm_spl_by_steps_gpt4'])


    # https://blog.csdn.net/weixin_38920297/article/details/114972832
    # print(y1_user_path_length_avg)
    # print(y1_user_path_length_var)
    default_palette = sns.color_palette()
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(24, 12))
    # plt.figure(figsize=(12,8))
    total_width = 1.2
    x_axis = np.arange(len(x_scene_name))

    width_3 = total_width / (3 + 1)

    axes[0, 0].bar(x_axis - width_3, y1_gt_path_length, width=width_3,  label='Ground Truth')
    axes[0, 0].bar(x_axis, y1_user_path_length_avg, yerr=y1_user_path_length_var, width=width_3,  label='Human')
    axes[0, 0].bar(x_axis + width_3, y1_gpt4_path_length, width=width_3, label='GPT-4')
    axes[0, 0].set_xticks(x_axis)
    # axes[0, 0].set_xticklabels(x_scene_name, rotation=25)
    axes[0, 0].set_xticklabels(x_scene_name)
    axes[0, 0].set_xlabel("Scene")
    axes[0, 0].set_ylabel("Distance")
    axes[0, 0].set_title("Distance Comparison")
    axes[0, 0].legend()
    # plt.tight_layout()

    axes[0, 1].bar(x_axis - width_3, y2_gt_steps, width=width_3, label='Ground Truth')
    axes[0, 1].bar(x_axis, y2_user_steps_avg, yerr=y2_user_steps_var, width=width_3, label='Human')
    axes[0, 1].bar(x_axis + width_3, y2_gpt4_steps, width=width_3, label='GPT-4')
    axes[0, 1].set_xticks(x_axis)
    axes[0, 1].set_xticklabels(x_scene_name)
    axes[0, 1].set_xlabel("Scene")
    axes[0, 1].set_ylabel("Steps")
    axes[0, 1].set_title("Steps Comparison")
    axes[0, 1].legend()

    width_2 = total_width / (2 + 1)
    y3_user_dis_spl_var = [min(a, b) for a, b in zip(y3_user_dis_spl_var, y3_user_dis_spl_avg)]
    axes[1, 0].bar(x_axis - width_2, y3_user_dis_spl_avg, yerr=y3_user_dis_spl_var, width=width_2, label='Human', color=default_palette[1])
    axes[1, 0].bar(x_axis, y3_gpt4_dis_spl, width=width_2, label='GPT-4',color=default_palette[2])
    axes[1, 0].set_xticks(x_axis)
    axes[1, 0].set_xticklabels(x_scene_name)
    axes[1, 0].set_xlabel("Scene")
    axes[1, 0].set_ylabel("Distance SPL")
    axes[1, 0].set_title("Distance SPL Comparison")
    axes[1, 0].legend()

    y4_user_steps_spl_var = [min(a, b) for a, b in zip(y4_user_steps_spl_avg, y4_user_steps_spl_var)]
    axes[1, 1].bar(x_axis - width_2, y4_user_steps_spl_avg, yerr=y4_user_steps_spl_var, width=width_2, label='Human',color=default_palette[1])
    axes[1, 1].bar(x_axis, y4_gpt4_steps_spl, width=width_2, label='GPT-4',color=default_palette[2])
    axes[1, 1].set_xticks(x_axis)
    axes[1, 1].set_xticklabels(x_scene_name)
    axes[1, 1].set_xlabel("Scene")
    axes[1, 1].set_ylabel("Steps SPL")
    axes[1, 1].set_title("Steps SPL Comparison")
    axes[1, 1].legend()

    # plt.tight_layout()
    plt.savefig("current_result.pdf")
    # plt.show()







