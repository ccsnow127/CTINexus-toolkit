import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="config4", version_base="1.2")
def run(config: DictConfig):
    CTI_Source = config.CTI_Source
    GTset = config.GTset
    in_folder_dir = os.path.join(config.GTset, CTI_Source)
    for file in os.listdir(in_folder_dir):
        in_filepath = os.path.join(in_folder_dir, file)
        with open(in_filepath, 'r') as f:
            data = json.load(f)
            del_keys = ["usage", "prompt", "template", "response_time"]
            for key in del_keys:
                del data[key]

        with open(in_filepath, 'w') as f:
            json.dump(data, f, indent=4)
            

run()