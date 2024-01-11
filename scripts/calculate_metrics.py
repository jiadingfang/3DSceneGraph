import os
import glob
import json
from pathlib import Path

# log_dir = 'logs/split_tiny_automated-model_gpt-4-neighbors_4'
# log_dir = 'logs/split_tiny_automated-model_gpt-3.5-turbo-neighbors_4'
# log_dir = 'logs/split_tiny_automated-model_ft:gpt-3.5-turbo-0613:ripl::8Bl5JCs3-neighbors_4'
log_dir = 'logs/split_tiny_automated-model_ft:gpt-3.5-turbo-0613:ripl::8Bl2tnqc-neighbors_4'
# log_dir = 'test_logs/split_tiny_automated-model_gpt-4-0613-neighbors_4'
# log_dir = 'test_logs/split_tiny_automated-model_gpt-3.5-turbo-0613-neighbors_4'
# log_dir = 'test_logs/split_tiny_automated-model_ft:gpt-3.5-turbo-0613:ripl::8Bl5JCs3-neighbors_4'
# log_dir = 'test_logs/split_tiny_automated-model_ft:gpt-3.5-turbo-0613:ripl::8Bl2tnqc-neighbors_4'
# log_dir = 'test_logs/split_tiny_verified-model_gpt-4-0613-neighbors_4'
# log_dir = 'test_logs/split_tiny_verified-model_gpt-3.5-turbo-0613-neighbors_4'
# log_dir = 'test_logs/split_tiny_verified-model_ft:gpt-3.5-turbo-0613:ripl::8Bl5JCs3-neighbors_4'
# log_dir = 'test_logs/split_tiny_verified-model_ft:gpt-3.5-turbo-0613:ripl::8Bl2tnqc-neighbors_4'
print('log_dir: ', log_dir)
split_name = log_dir.split('split_')[1].split('-model')[0]

total_split_metrics_dict = {'spl_by_distance': {}, 'spl_by_steps': {}}

for scene_name in os.listdir(log_dir):
    # print(scene_name)
    scene_dir = Path(log_dir) / scene_name

    total_split_metrics_dict['spl_by_distance'][scene_name] = []
    total_split_metrics_dict['spl_by_steps'][scene_name] = []

    for sample_task_name in os.listdir(scene_dir):
        task_metrics_path = glob.glob(str(scene_dir / sample_task_name / 'metrics_*.json'))[0]
        with open(task_metrics_path, 'r') as f:
            task_metrics = json.load(f)
            # print(task_metrics)

        total_split_metrics_dict['spl_by_distance'][scene_name].append(task_metrics['spl_by_distance'])
        total_split_metrics_dict['spl_by_steps'][scene_name].append(task_metrics['spl_by_steps'])
        
# calculate statistics
total_split_metrics_dict_mean_per_scene = {'spl_by_distance': {}, 'spl_by_steps': {}}
total_split_metrics_dict_std_per_scene = {'spl_by_distance': {}, 'spl_by_steps': {}}
for metric_name in total_split_metrics_dict.keys():
    for scene_name in total_split_metrics_dict[metric_name].keys():
        total_split_metrics_dict_mean_per_scene[metric_name][scene_name] = sum(total_split_metrics_dict[metric_name][scene_name]) / len(total_split_metrics_dict[metric_name][scene_name])
        total_split_metrics_dict_std_per_scene[metric_name][scene_name] = (sum([(x - total_split_metrics_dict_mean_per_scene[metric_name][scene_name])**2 for x in total_split_metrics_dict[metric_name][scene_name]]) / len(total_split_metrics_dict[metric_name][scene_name])) ** 0.5
# print('total_split_metrics_dict_mean_per_scene: ', total_split_metrics_dict_mean_per_scene)
# print('total_split_metrics_dict_std_per_scene: ', total_split_metrics_dict_std_per_scene)

total_split_metrics_dict_mean = {'spl_by_distance': 0, 'spl_by_steps': 0}
total_split_metrics_dict_std = {'spl_by_distance': 0, 'spl_by_steps': 0}
for metric_name in total_split_metrics_dict.keys():
    total_split_metrics_dict_mean[metric_name] = sum([total_split_metrics_dict_mean_per_scene[metric_name][scene_name] for scene_name in total_split_metrics_dict_mean_per_scene[metric_name].keys()]) / len(total_split_metrics_dict_mean_per_scene[metric_name].keys())
    total_split_metrics_dict_std[metric_name] = (sum([(total_split_metrics_dict_mean_per_scene[metric_name][scene_name] - total_split_metrics_dict_mean[metric_name])**2 for scene_name in total_split_metrics_dict_mean_per_scene[metric_name].keys()]) / len(total_split_metrics_dict_mean_per_scene[metric_name].keys())) ** 0.5

print('total_split_metrics_dict_mean: ', total_split_metrics_dict_mean)
# print('total_split_metrics_dict_std: ', total_split_metrics_dict_std)