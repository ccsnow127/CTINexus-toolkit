import json
import os 
from omegaconf import DictConfig, OmegaConf
import copy


class Preprocessor:
    def __init__(self, config: DictConfig):
        self.config = config

    def preprocess(self, CTI_source, inFile):
        self.CTI_source = CTI_source
        self.inFile = inFile
        with open(os.path.join(self.config.inSet, self.CTI_source, self.inFile), 'r') as f:
            js = json.load(f)

        jsr = copy.deepcopy(js)
        jsr["EA"] = {}
        jsr["EA"]["aligned_triplets"] = js["ET"]["typed_triplets"]
        ID = 0
        for triple in jsr["EA"]["aligned_triplets"]:
            for key, entity in triple.items():
                if key in ["subject", "object"]:
                    entity["mention_id"] = ID
                    ID += 1
                    entity['mention_text'] = entity.pop('text')
                    entity["mention_class"] = entity.pop('class')
                    if isinstance(entity["mention_class"], dict):
                        entity["mention_class"] = list(entity["mention_class"].keys())[0]

        jsr["EA"]["mentions_num"] = ID
        
        
        outfolder = os.path.join(self.config.outSet, self.CTI_source)
        os.makedirs(outfolder, exist_ok=True)
        outfile_path = os.path.join(outfolder, self.inFile)
        with open(outfile_path, 'w') as f:
            json.dump(jsr, f, indent=4)
