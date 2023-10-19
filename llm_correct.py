# File for self-reasoning about navigation mistakes using LLM
import os
import json
import openai
import tqdm

debug = False
log_dir = 'logs/split_medium_automated-model_gpt-4-neighbors_4'
scene_name_list = os.listdir(log_dir)

for scene_name in tqdm.tqdm(scene_name_list):
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
        valid_time_stamps = [time_stamp for time_stamp in time_stamps if os.path.exists(os.path.join(task_log_path, 'llm_responses_' + time_stamp + '.json')) and os.path.exists(os.path.join(task_log_path, 'metrics_' + time_stamp + '.json'))]
        if debug: print('valid_time_stamps: ', valid_time_stamps)
        if len(valid_time_stamps) == 0:
            continue
        chosen_time_stamp = valid_time_stamps[-1]
        if debug: print('chosen_time_stamp: ', chosen_time_stamp)
        chosen_llm_response_path = os.path.join(task_log_path, 'llm_responses_' + chosen_time_stamp + '.json')
        chosen_metrics_path = os.path.join(task_log_path, 'metrics_' + chosen_time_stamp + '.json')
        if debug:
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
                    break

            # Read LLM responses
            with open(chosen_llm_response_path, 'r') as f:
                llm_responses = json.load(f)
            first_different_llm_response_user = llm_responses[first_different_index * 2 - 2 ]
            first_different_llm_response_assistant = llm_responses[first_different_index * 2 - 1]
            if debug:
                print('first_different_llm_response_user: ', first_different_llm_response_user)
                print('first_different_llm_response_assistant: ', first_different_llm_response_assistant)

            gt_choice = gt_shortest_path_trajectory[first_different_index]
            llm_choice = llm_shortest_path_trajectory[first_different_index]
            if debug:
                print('gt_choice: ', gt_choice)
                print('llm_choice: ', llm_choice)

            # Ask LLM to reason about the mistake
            prompt = 'Analysis your current choices, and tell me why the choice should be ' + gt_choice + '.'
            if debug: print('prompt: ', prompt)
            messages = [
                {"role": "system", "content": "You are a helpful assistant. You job is to navigate in a unknown environment to find a certain object with shortest path possible. Be consice with your response."},
                first_different_llm_response_user,
                {"role": "user", "content": prompt}
            ]
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=messages,
                max_tokens=300,
                temperature=0
            )
            repsonse_text = response['choices'][0]['message']["content"]
            if debug: print('response_text: ', repsonse_text)

            llm_correct_message = [
                first_different_llm_response_user,
                {"role": "assistant", "content": repsonse_text}
            ]
            if debug: print('llm_correct_message: ', llm_correct_message)

            save_name = 'llm_correct_{}.json'.format(chosen_time_stamp)
            json_object = json.dumps(llm_correct_message, indent=4)
            with open(os.path.join(task_log_path, save_name), 'w', encoding ='utf8') as json_file: 
                json_file.write(json_object)
        # break
    # break

                
