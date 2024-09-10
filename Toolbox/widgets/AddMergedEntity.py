import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="config2", version_base="1.2")
def run(config: DictConfig):
    in_folder_dir = os.path.join(config.inSet, config.CTI_Source)
    for file in os.listdir(in_folder_dir):
        in_filepath = os.path.join(in_folder_dir, file)
        with open(in_filepath, 'r') as f:
            data = json.load(f)
            triples = data["annotator"]["triplets"]["tagged_triples"]
            MergedDict = {}
            for triple in triples:
                if triple["subject"]["flag"] == 1:
                    if triple["subject"]["id"] in MergedDict:
                        MergedDict[triple["subject"]["id"]].append(triple["subject"]["text"])
                    else:
                        MergedDict[triple["subject"]["id"]] = [triple["subject"]["text"]]
                if triple["object"]["flag"] == 1:
                    if triple["object"]["id"] in MergedDict:
                        MergedDict[triple["object"]["id"]].append(triple["object"]["text"])
                    else:
                        MergedDict[triple["object"]["id"]] = [triple["object"]["text"]]
            for triple in triples:
                if triple["subject"]["id"] in MergedDict:
                    triple["subject"]["merged_entities"] = MergedDict[triple["subject"]["id"]]
                if triple["object"]["id"] in MergedDict:
                    triple["object"]["merged_entities"] = MergedDict[triple["object"]["id"]]

    out_folder_dir = os.path.join(config.outSet, config.CTI_Source)
    os.makedirs(out_folder_dir, exist_ok=True)
    for file in os.listdir(in_folder_dir):
        out_filepath = os.path.join(out_folder_dir, file)
        with open(out_filepath, 'w') as f:
            json.dump(data, f, indent=4)

run()