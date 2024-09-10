import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
from Merger import Merger

@hydra.main(config_path="config", config_name="model-SecureBert", version_base="1.2")
def run(config: DictConfig):
    if hasattr(config, 'inFile'): # If specifiy a input file
        Merger(config).merge(config.CTI_Source, config.inFile)

    elif hasattr(config, 'CTI_Source'): # If specify a CTI_Source
        FolderPath = os.path.join(config.inSet, config.CTI_Source)
        annotated_files = os.listdir(os.path.join(config.outSet, config.CTI_Source))
        for JSONFile in os.listdir(FolderPath):
            if JSONFile in annotated_files:
                continue
            Merger(config).merge(config.CTI_Source, JSONFile)

    else: # If not specify any input file or CTI_Source
        for CTI_Source in os.listdir(config.inSet):
            if CTI_Source == 'prompt_store':
                continue
            annotated_CTI_Source = os.listdir(config.outSet)
            if CTI_Source in annotated_CTI_Source:
                continue
            FolderPath = os.path.join(config.inSet, CTI_Source)
            for JSONFile in os.listdir(FolderPath):
                Merger(config).merge(CTI_Source, JSONFile)


if __name__ == "__main__":
    run()