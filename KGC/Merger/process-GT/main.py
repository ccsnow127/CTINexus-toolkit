import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

def fix_nodes(inFile, outFile,  entity_text_list, entity_id_beg):
    with open(inFile, 'r') as f:
        fixed_entity_dict = {}
        data = json.load(f)
        aligned_triplets = data['EA']['aligned_triplets']
        for aligned_triplet in aligned_triplets:
            for key, node in aligned_triplet.items():
                if key == "subject" or key == "object":
                    if node['entity_text'] in entity_text_list:
                        node['entity_id'] = entity_id_beg
                        node['mentions_merged'] = [text for text in node['mentions_merged'] if text == node['entity_text'] or text not in entity_text_list]
                        if node['entity_text'] not in fixed_entity_dict:
                            fixed_entity_dict[node['entity_text']] = entity_id_beg
                            entity_id_beg += 1
        data['EA']['entity_num'] = entity_id_beg-1
        with open(outFile, 'w') as f:
            json.dump(data, f, indent=4)
    return entity_id_beg  # 返回修改后的 entity_id_beg
        




@hydra.main(config_path="config", config_name="config", version_base="1.2")
def run(config: DictConfig):
    for CTI_source in os.listdir(config.inSet):
        if CTI_source == "prompt_store":
            continue
        inFolder = os.path.join(config.inSet, CTI_source)
        for file in os.listdir(inFolder):
            entity_id_dict = {}
            # inFolder = "/home/yutong/CTINexus/dataset/Merger-output-large-GT/BleepingComputer"
            # file = "androxgh0st.json"
            with open(os.path.join(inFolder, file), 'r') as f:
                data = json.load(f)
                aligned_triplets = data['EA']['aligned_triplets']
                entity_id_beg = data['EA']['entity_num']
                for aligned_triplet in aligned_triplets:
                    for key, node in aligned_triplet.items():
                        if key == "subject" or key == "object":
                            if len(node['mentions_merged']) > 1:
                                if node['entity_id'] not in entity_id_dict:
                                    entity_id_dict[node['entity_id']] = set()
                                entity_id_dict[node['entity_id']].add(node['entity_text'])

                for key, entity_text_list in entity_id_dict.items():
                    if len(entity_text_list) > 1:
                        inFile = os.path.join(inFolder, file)
                        outFolder = os.path.join(config.outSet, CTI_source)
                        if not os.path.exists(outFolder):
                            os.makedirs(outFolder)
                        outFile = os.path.join(outFolder, file)
                        entity_id_beg = fix_nodes(inFile, outFile, entity_text_list, entity_id_beg)



if __name__ == "__main__":
    run()