import os
import yaml
from pathlib import Path

# log_dir = 'logs/split_tiny_automated-model_gpt-4-neighbors_4'
# log_dir = 'logs/split_tiny_automated-model_ft:gpt-3.5-turbo-0613:ripl::8Bl2tnqc-neighbors_4'
log_dir = 'test_logs/split_tiny_verified-model_gpt-4-0613-neighbors_4'
split_name = log_dir.split('split_')[1].split('-model')[0]
sample_source_target_dict = {split_name: {}}

for scene_name in sorted(os.listdir(log_dir)):
    scene_dir = Path(log_dir) / scene_name

    source_target_list = []
    for sample_task_name in sorted(os.listdir(scene_dir)):
        source_room_idx = sample_task_name.split('room_')[1].split('_target')[0]
        target_category = sample_task_name.split('target_category-')[1]

        source_target_list.append({'source_room':source_room_idx, 'target_category':target_category})
    
    sample_source_target_dict[split_name][scene_name] = source_target_list

# save sample_source_target_dict to a yaml file
save_path = 'sample_source_target_dict_tiny_verified_gpt-4.yaml'
with open(save_path, 'w') as f:
    yaml.dump(sample_source_target_dict, f)

# load sample_source_target_dict from a yaml file
with open(save_path, 'r') as f:
    sample_source_target_dict = yaml.load(f, Loader=yaml.FullLoader)
    print(sample_source_target_dict)
