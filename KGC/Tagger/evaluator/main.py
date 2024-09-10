import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
from Evaluator import Evaluator

@hydra.main(config_path="config", config_name="GPT3.5+12shot", version_base="1.2")
def run(config: DictConfig):
        if hasattr(config, 'inFile'):
            Evaluator(config, config.CTI_Source, config.inFile).evaluate()
             
        elif hasattr(config, 'CTI_Source'):
            inFolder = os.path.join(config.inSet, config.CTI_Source)
            for JSONFile in os.listdir(inFolder):
                 Evaluator(config, config.CTI_Source, JSONFile).evaluate()

        else:
            # counter = 0
            for CTI_Source in os.listdir(config.inSet):
                if CTI_Source.endswith('.json'):
                    continue
                if CTI_Source == "prompt_store":
                    continue
                FolderPath = os.path.join(config.inSet, CTI_Source)
                for JSONFile in os.listdir(FolderPath):
                    # counter += 1
                    # print(f"Processing {counter} files...")
                    Evaluator(config, CTI_Source, JSONFile).evaluate()

if __name__ == "__main__":
    run()
    
