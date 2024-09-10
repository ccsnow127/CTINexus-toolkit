import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
from Preprocessor import Preprocessor

@hydra.main(config_path="config", config_name="config", version_base="1.2")
def run(config: DictConfig):
    if hasattr(config, 'inFile'):
        Preprocessor(config).preprocess(config.CTI_Source, config.inFile)
    
    elif hasattr(config, 'CTI_Source'):
        FolderPath = os.path.join(config.inSet, config.CTI_Source)
        for JSONFile in os.listdir(FolderPath):
            Preprocessor(config).preprocess(config.CTI_Source, JSONFile)

    else:
        for CTI_Source in os.listdir(config.inSet):
            if CTI_Source == 'prompt_store':
                continue
            FolderPath = os.path.join(config.inSet, CTI_Source)
            for JSONFile in os.listdir(FolderPath):
                Preprocessor(config).preprocess(CTI_Source, JSONFile)

if __name__ == "__main__":
    run()
