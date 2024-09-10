import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="config", version_base="1.2")
def run(config: DictConfig):
    #merge the jsonFile in the outSet into the inSet
    #traverse the outSet, replace the corresponding file in the inSet with the file in the outSet  
    for CTI_source in os.listdir(config.outSet):
        if CTI_source == "prompt_store":
            continue
        inFolder = os.path.join(config.inSet, CTI_source)
        outFolder = os.path.join(config.outSet, CTI_source)
        for file in os.listdir(outFolder):
            inFile = os.path.join(inFolder, file)
            outFile = os.path.join(outFolder, file)
            with open(outFile, 'r') as f:
                data = json.load(f)
                with open(inFile, 'w') as f:
                    json.dump(data, f, indent=4)
        print(f"Finished merging {CTI_source}")
    

if __name__ == "__main__":
    run()