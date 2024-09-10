import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
from LLMTagger import LLMTagger

@hydra.main(config_path="config", config_name="GPT3.5+12shot", version_base="1.2")
def run(config: DictConfig):
    if hasattr(config, "inFile"): # tag a single file
        LLMTagger(config).tag(config.CTI_source, config.inFile)

    elif hasattr(config, "CTI_Source"): # tag all files in a single CTI_source
        inFolder = os.path.join(config.inSet, config.CTI_Source)
        for file in os.listdir(inFolder):
            LLMTagger(config).tag(config.CTI_source, file)

    else: # tag all files in all CTI_sources
        for CTI_source in os.listdir(config.inSet):
            if CTI_source == "prompt_store":
                continue
            annotatedCTICource = [dir for dir in os.listdir(config.outSet)]
            if CTI_source in annotatedCTICource:
                continue
            inFolder = os.path.join(config.inSet, CTI_source)
            for file in os.listdir(inFolder):
                LLMTagger(config).tag(CTI_source, file)

if __name__ == "__main__":
    run()