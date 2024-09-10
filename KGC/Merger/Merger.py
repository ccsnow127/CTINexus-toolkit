import json
import os 
from omegaconf import DictConfig, OmegaConf
from jinja2 import Template, Environment, FileSystemLoader, meta
from LLMMerger import LLMMerger
import time


class Merger:
    def __init__(self, config: DictConfig):
        self.config = config
        self.tag_dict = {}
        self.entity_id = 0

    def merge(self, CTI_source, inFile):
        self.CTI_source = CTI_source
        self.inFile = inFile
        self.inFile_path = os.path.join(self.config.inSet, self.CTI_source, self.inFile)
        self.build_tag_dict(self.inFile_path)
        start_time = time.time()
        for mention_class, node_list in self.tag_dict.items():
            if len(node_list) == 1:
                print("haha")
            LLMMerger(self).merge(node_list)
        end_time = time.time()
        response_time = end_time - start_time
        self.js['EA']['response_time'] = response_time
        self.js['EA']["embedding_model"] = self.config.embedding_model
        self.js['EA']["entity_num"] = self.entity_id

        outfolder = os.path.join(self.config.outSet, self.CTI_source)
        os.makedirs(outfolder, exist_ok=True)
        outfile_path = os.path.join(outfolder, self.inFile)
        with open(outfile_path, 'w') as f:
            json.dump(self.js, f, indent=4)

    def build_tag_dict(self, inFile_path):
        with open(inFile_path, 'r') as f:
            self.js = json.load(f)
        for triple in self.js["EA"]["aligned_triplets"]:
            for key, node in triple.items():
                if key in ["subject", "object"]:
                    self.update_tag_dict(node) 
        

    def update_tag_dict(self, node):
        if node["mention_class"] in self.tag_dict:
            self.tag_dict[node["mention_class"]].append((node["mention_id"], node["mention_text"]))
        else:
            self.tag_dict[node["mention_class"]] = [(node["mention_id"], node["mention_text"])]
                
