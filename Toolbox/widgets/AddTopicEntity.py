import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="config3", version_base="1.2")
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
            
            max_len = (0, 0)#(id, length)
            for key, list in MergedDict.items():
                if len(list) > max_len[1]:
                    max_len = (key, len(list))
            print(max_len)
            data["annotator"]["topic_entity"] = {
                "id": max_len[0],
                "text": MergedDict[max_len[0]]
            }
                

    out_folder_dir = os.path.join(config.outSet, config.CTI_Source)
    os.makedirs(out_folder_dir, exist_ok=True)
    for file in os.listdir(in_folder_dir):
        out_filepath = os.path.join(out_folder_dir, file)
        with open(out_filepath, 'w') as f:
            json.dump(data, f, indent=4)

run()