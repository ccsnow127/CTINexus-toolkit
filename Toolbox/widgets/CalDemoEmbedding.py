import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
import openai
import time

@hydra.main(config_path="config", config_name="config6", version_base="1.2")
def run(config: DictConfig):
    demoSetPath, CTI_folders, _ = next(os.walk(config.demo_set))
    openai.api_key = config.openai_key
    embedding_model = config.embedding_model

    for CTI_folder in CTI_folders:
        CTIfolderPath = os.path.join(demoSetPath, CTI_folder)
        for JSONfile in os.listdir(CTIfolderPath):
            with open(os.path.join(CTIfolderPath, JSONfile), "r") as f:
                js = json.load(f)
            if embedding_model == "text-embedding-3-large":
                print(f"start embedding {JSONfile.split('.')[0]}")
                start_time = time.time()
                response = openai.Embedding.create(
                    input=js["CTI"],
                    engine=embedding_model
                )
                end_time = time.time()
                response_time = end_time - start_time
                print(f"finish embedding {JSONfile.split('.')[0]}, took {response_time} seconds")
                if "vector" not in js:
                    js["vector"] = {}
                if "text-embedding-3-large" not in js["vector"]:
                    js["vector"]["text-embedding-3-large"] = {}
                js["vector"]["text-embedding-3-large"]["embedding"] = response['data'][0]['embedding']
                js["vector"]["text-embedding-3-large"]["time"] = response_time
                js["vector"]["text-embedding-3-large"]["token"] = response['usage']['total_tokens']
            

            with open(os.path.join(CTIfolderPath, JSONfile), "w") as f:
                json.dump(js, f, indent=4)

if __name__ == "__main__":
    run()