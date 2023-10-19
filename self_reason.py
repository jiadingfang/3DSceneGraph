# File for self-reasoning about navigation mistakes using LLM
import os

log_dir = 'logs/split_medium_automated-model_gpt-4-neighbors_4'
scene_name_list = os.listdir(log_dir)

for scene_name in scene_name_list:
    scene_dir = os.path.join(log_dir, scene_name)
    task_configs = os.listdir(scene_dir)
    for task_config in task_configs:
        task_log_path = os.path.join(scene_dir, task_config)
        log_files = os.listdir(task_log_path)
        time_stamps = list(set([log_fn.split('.')[0].split('_')[-1] for log_fn in log_files]))