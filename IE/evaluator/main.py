import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
from LLMEvaluator import LLMEvaluator

@hydra.main(config_path="config", config_name="DemoNum=4", version_base="1.2")
def run(config: DictConfig):
        if hasattr(config, 'inFile'):
             LLMEvaluator(config, config.CTI_Source, config.inFile).evaluate()
             
        elif hasattr(config, 'CTI_Source'):
            annotated_files = []
            outFolder = os.path.join(config.outSet, config.CTI_Source)
            for JSONFile in os.listdir(outFolder):
                annotated_files.append(JSONFile)
            
            inFolder = os.path.join(config.inSet, config.CTI_Source)
            for JSONFile in os.listdir(inFolder):
                if JSONFile in annotated_files:
                    continue
                LLMEvaluator(config, config.CTI_Source, JSONFile).evaluate()

        else:
            annotated_folders = []
            for CTI_Source in os.listdir(config.outSet):
                annotated_folders.append(CTI_Source)
            for CTI_Source in os.listdir(config.inSet):
                if CTI_Source in annotated_folders:
                    continue
                if CTI_Source == "prompt_store":
                    continue
                FolderPath = os.path.join(config.inSet, CTI_Source)
                for JSONFile in os.listdir(FolderPath):
                     LLMEvaluator(config, CTI_Source, JSONFile).evaluate()

if __name__ == "__main__":
    run()
    
