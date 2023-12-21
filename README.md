# LLM Goal-Finding in 3D Scene Graph
This is the code repo for the project that test indoor goal-finding capabilities in 3D scene graphs

## Install
> pip install -r requirements.txt

## Data
For original 3D scene graph data, visit [https://github.com/StanfordVL/3DSceneGraph](https://github.com/StanfordVL/3DSceneGraph)

But I have processed the data including all provided partitions `medium_automated`, `tiny_automated`, `tiny_verified` under the directory `scene_text` so you do not have to download extra data for running this repo.

## Repo Structure
The following are brief discriptions of some important files or directories:
- `graphs.py`: the file responsible for creating affinity graph for each scene.
- `graph_sim.py`: the main file for evaluation. Each graph is treated as a simulator for text navigation.
- `llm_call.py`: utility code for calling LLMs.
- `llm_correct.py`: code for creating self-correction examples for finetuning.
- `finetun.py`: code for running LLM finetune.
- `logs`: log files for each evaluation run. Subdirectory names indicate their split and LLM model name.
- `finetune_files`: prepared data for finetuning LLMs.


## Evaluation
Run
> python graph_sim.py

There are opions like `split_name`, `llm_model`, `n_samples_per_scene`, `n_neighbors` that you can alter. Will make them in argparse later.