import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
import openai

@hydra.main(config_path="config", config_name="config5", version_base="1.2")
def run(config: DictConfig):
    api_key = config.openai_key
    validate_api_key(api_key)

def validate_api_key(api_key):
    openai.api_key = api_key

    try:
        response = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
            ]
        )
        print("API key is valid.")
    except Exception as e:
        print(f"API key is not valid. Error: {str(e)}")

run()