# File for finetuning
import os
import json

debug = False
log_dir = 'logs/split_medium_automated-model_gpt-4-neighbors_4'
scene_name_list = os.listdir(log_dir)

raw_messages_list = [] # messages for (correct) llm_responses only
messages_list = [] # messages for llm_responses and llm_correct

for scene_name in scene_name_list:
    print('scene_name: ', scene_name)
    scene_dir = os.path.join(log_dir, scene_name)
    task_configs = os.listdir(scene_dir)
    for task_config in task_configs:
        if debug:
            print('=============================')
            print('task_config: ', task_config)
        task_log_path = os.path.join(scene_dir, task_config)
        log_files = os.listdir(task_log_path)

        time_stamps = list(set([log_fn.split('.')[0].split('_')[-1] for log_fn in log_files]))
        # valid time stamps are the ones that have llm_responses and metrics
        valid_time_stamps = [time_stamp for time_stamp in time_stamps if os.path.exists(os.path.join(task_log_path, 'llm_responses_' + time_stamp + '.json')) and os.path.exists(os.path.join(task_log_path, 'metrics_' + time_stamp + '.json'))]
        if debug: print('valid_time_stamps: ', valid_time_stamps)
        if len(valid_time_stamps) == 0:
            continue
        chosen_time_stamp = valid_time_stamps[-1]
        if debug: print('chosen_time_stamp: ', chosen_time_stamp)
        # chosen_llm_correct_path = os.path.join(task_log_path, 'llm_correct_' + chosen_time_stamp + '.json')
        chosen_llm_response_path = os.path.join(task_log_path, 'llm_responses_' + chosen_time_stamp + '.json')
        chosen_metrics_path = os.path.join(task_log_path, 'metrics_' + chosen_time_stamp + '.json')
        if debug:
            # print('chosen_llm_correct_path: ', chosen_llm_correct_path)
            print('chosen_llm_response_path: ', chosen_llm_response_path)
            print('chosen_metrics_path: ', chosen_metrics_path)

        # Read metrics
        with open(chosen_metrics_path, 'r') as f:
            metrics_dict = json.load(f)
        if metrics_dict['spl_by_steps'] < 0.99:
            gt_shortest_path_trajectory = metrics_dict['gt_shortest_path_trajectory']
            llm_shortest_path_trajectory = metrics_dict['llm_shortest_path_trajectory']
            # find the first different items in two lists
            first_different_index = 0
            for i in range(len(gt_shortest_path_trajectory)):
                if gt_shortest_path_trajectory[i] != llm_shortest_path_trajectory[i]:
                    first_different_index = i
                    if debug: print('first_different_index: ', first_different_index)
                    break

            # Read LLM responses
            with open(chosen_llm_response_path, 'r') as f:
                llm_responses = json.load(f)

            llm_responses_compatible = llm_responses[:first_different_index * 2 - 2]

            # Read LLM correct
            chosen_llm_correct_path = os.path.join(task_log_path, 'llm_correct_' + chosen_time_stamp + '.json')
            with open(chosen_llm_correct_path, 'r') as f:
                llm_correct = json.load(f)

            llm_responses_all = llm_responses_compatible + llm_correct

            # save messages for correct llm_responses only
            for i in range(int(len(llm_responses_compatible) / 2)):
                messages = {'messages': [llm_responses_compatible[i * 2], llm_responses_compatible[i * 2 + 1]]}
                raw_messages_list.append(messages)

            # save messages for messages list that contain both llm_responses and llm_correct
            for i in range(int(len(llm_responses_all) / 2)):
                messages = {'messages': [llm_responses_all[i * 2], llm_responses_all[i * 2 + 1]]}
                messages_list.append(messages)

        # no need for llm_correct
        else:
            with open(chosen_llm_response_path, 'r') as f:
                llm_responses_all = json.load(f)

            # save messages for llm_responses only
            for i in range(int(len(llm_responses_all) / 2)):
                messages = {'messages': [llm_responses_all[i * 2], llm_responses_all[i * 2 + 1]]}
                raw_messages_list.append(messages)

            # save messages for messages list that contain both llm_responses and llm_correct
            for i in range(int(len(llm_responses_all) / 2)):
                messages = {'messages': [llm_responses_all[i * 2], llm_responses_all[i * 2 + 1]]}
                messages_list.append(messages)

    # break

train_messages_length = int(len(messages_list) * 0.9)
train_messages_list = messages_list[:train_messages_length]
val_messages_list = messages_list[train_messages_length:]
print('train_messages_length: ', len(train_messages_list))
print('val_messages_length: ', len(val_messages_list))
with open('finetune_files/finetune_llm_correct_train.jsonl', "w") as out:
    for messages in train_messages_list:
        jout = json.dumps(messages) + "\n"
        out.write(jout)

with open('finetune_files/finetune_llm_correct_val.jsonl', "w") as out:
    for messages in val_messages_list:
        jout = json.dumps(messages) + "\n"
        out.write(jout)

train_raw_messages_length = int(len(raw_messages_list) * 0.9)
train_raw_messages_list = raw_messages_list[:train_raw_messages_length]
val_raw_messages_list = raw_messages_list[train_raw_messages_length:]
print('train_raw_messages_length: ', len(train_raw_messages_list))
print('val_raw_messages_length: ', len(val_raw_messages_list))
with open('finetune_files/finetune_llm_responses_train.jsonl', "w") as out:
    for messages in train_raw_messages_list:
        jout = json.dumps(messages) + "\n"
        out.write(jout)

with open('finetune_files/finetune_llm_responses_val.jsonl', "w") as out:
    for messages in val_raw_messages_list:
        jout = json.dumps(messages) + "\n"
        out.write(jout)