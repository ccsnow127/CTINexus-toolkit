import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="config", version_base="1.2")
def run(config: DictConfig):
    in_folder_dir = os.path.join(config.inSet, config.CTI_Source)
    for file in os.listdir(in_folder_dir):
        in_filepath = os.path.join(in_folder_dir, file)
        with open(in_filepath, 'r') as f:
            data = json.load(f)
            triples = data["annotator"]["triplets"]["tagged_triples"]
            id = 0
            for triple in triples:
                triple["subject"]["id"] = id
                id += 1
                triple["object"]["id"] = id
                id += 1
            
    out_folder_dir = os.path.join(config.outSet, config.CTI_Source)
    os.makedirs(out_folder_dir, exist_ok=True)
    for file in os.listdir(in_folder_dir):
        out_filepath = os.path.join(out_folder_dir, file)
        with open(out_filepath, 'w') as f:
            json.dump(data, f, indent=4)


run()