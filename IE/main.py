from LLMAnnotator import LLMAnnotator
import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="demoNum=4", version_base="1.2")
def run(config: DictConfig):
        if hasattr(config, 'inFile'):
             LLMAnnotator(config, config.CTI_Source, config.inFile).annotate()
             
        elif hasattr(config, 'CTI_Source'):
            inFolder = os.path.join(config.inSet, config.CTI_Source)
            for JSONFile in os.listdir(inFolder):
                LLMAnnotator(config, config.CTI_Source, JSONFile).annotate()

        else:
            for CTI_Source in os.listdir(config.inSet):
                annotatedCTICource = [dir for dir in os.listdir(config.outSet)]
                if CTI_Source in annotatedCTICource:
                    continue
                if CTI_Source.endswith('.json'):
                    continue

                FolderPath = os.path.join(config.inSet, CTI_Source)
                for JSONFile in os.listdir(FolderPath):
                    LLMAnnotator(config, CTI_Source, JSONFile).annotate()

if __name__ == "__main__":
    run()
    
