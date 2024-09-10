import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
from Linker import Linker

@hydra.main(config_path="config", config_name="3shot-GPT4", version_base="1.2")
def run(config: DictConfig):
    # linker = Linker(config)
    if hasattr(config, 'addition'):
        for CTI_Source in config.addition:
            for file in config.addition[CTI_Source]:
                Linker(config, CTI_Source, file)

    elif hasattr(config, 'inFile'): # If specifiy a input file
        Linker(config, config.CTI_Source, config.inFile)

    elif hasattr(config, 'CTI_Source'): # If specify a CTI_Source
        FolderPath = os.path.join(config.inSet, config.CTI_Source)
        annotated_files = os.listdir(os.path.join(config.outSet, config.CTI_Source))
        for JSONFile in os.listdir(FolderPath):
            if JSONFile in annotated_files:
                continue
            Linker(config, config.CTI_Source, JSONFile)

    else: # If not specify any input file or CTI_Source
        annotated_CTI_Sources = os.listdir(config.outSet)
        for CTI_Source in os.listdir(config.inSet):
            if CTI_Source in annotated_CTI_Sources:
                continue
            FolderPath = os.path.join(config.inSet, CTI_Source)
            for JSONFile in os.listdir(FolderPath):
                Linker(config, CTI_Source, JSONFile)

if __name__ == "__main__":
    run()