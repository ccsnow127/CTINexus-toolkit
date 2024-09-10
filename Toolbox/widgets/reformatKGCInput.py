import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
import openai
import time

def reformat(js):
    jsr = {}
    jsr["CTI"] = js["CTI"]
    jsr["IE"] = {}
    jsr["IE"]["triplets"] = js["annotator"]["triplets"]
    jsr["IE"]["triples_count"] = js["annotator"]["triples_count"]
    jsr["IE"]["cost"] = js["usage"]
    jsr["IE"]["time"] = js["response_time"]
    jsr["IE"]["link"] = js["link"]
    jsr["IE"]["prompt_file"] = js["prompt"]
    jsr["IE"]["prompt_template"] = js["template"]

    return jsr


@hydra.main(config_path="config", config_name="config7", version_base="1.2")
def run(config: DictConfig):
    # for CTI_source in os.listdir(config.inSet):
    #     inFolderPath = os.path.join(config.inSet, CTI_source)
    #     outFolderPath = os.path.join(config.outSet, CTI_source)
    #     for JSONfile in os.listdir(inFolderPath):
    #         try:
    #             with open(os.path.join(inFolderPath, JSONfile), "r") as f:
    #                 js = json.load(f)
    #         except:
    #             print("Error in reading the file: ", JSONfile)
    #             continue
    #         jsr = reformat(js)

            # with open(os.path.join(outFolderPath, JSONfile), "w") as f:
            #     json.dump(jsr, f, indent=4)
    with open("dataset/KGC-inputs-test/Unit42/Diplomats-Beware-Q3-f54.json", "r") as f:
        js = json.load(f)
        jsr = reformat(js)

    with open("dataset/KGC-inputs-test/Unit42/Diplomats-Beware-Q3-f54.json", "w") as f:
        json.dump(jsr, f, indent=4)


if __name__ == "__main__":
    run()