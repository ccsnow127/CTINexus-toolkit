import json
import os 
from omegaconf import DictConfig, OmegaConf
from jinja2 import Template, Environment, FileSystemLoader, meta
from LLMCaller import LLMCaller
from UsageCalculator import UsageCalculator


class LLMLinker:
    def __init__(self, linker):
        self.config = linker.config
        self.predicted_triples = []
        self.response_times = []
        self.usages = []
        self.main_nodes = linker.main_nodes
        self.linker = linker
        self.js = linker.js
        self.inFile = linker.inFile
        self.CTI_Source = linker.CTI_Source
        self.topic_node = linker.topic_node

    def link(self):
        for main_node in self.main_nodes:
            prompt = self.generate_prompt(main_node)
            llmCaller = LLMCaller(self.config, prompt)
            max_regenerate_times = 3
            # for regenerate_times in range(max_regenerate_times):
            self.llm_response, self.response_time = llmCaller.call()
            self.usage = UsageCalculator(self.llm_response).calculate()
            self.response_content = json.loads(self.llm_response.choices[0].message.content)
            try:
                pred_sub = self.response_content["predicted_triple"]['subject']
                pred_obj = self.response_content["predicted_triple"]['object']
                pred_rel = self.response_content["predicted_triple"]['relation']
                # break
            except:
                values = list(self.response_content.values())
                pred_sub, pred_rel, pred_obj = values[0], values[1], values[2]
                # try:
                #     pred_rel = self.response_content['relation']
                #     pred_sub = self.response_content['subject']
                #     pred_obj = self.response_content['object']
                #     # break
                # except:
                #     try:
                #         pred_sub = self.response_content['predicted_subject']
                #         pred_obj = self.response_content['predicted_object']
                #         pred_rel = self.response_content['predicted_relation']
                #     except:
                #         print("Error: The LLM model does not return the predicted triple!")
                #         print(f"Error file name: {self.inFile}")
                #         pred_sub = "hallucination"
                #         pred_obj = "hallucination"
                #         pred_rel = "hallucination"

            if pred_sub == main_node["entity_text"] and pred_obj == self.topic_node["entity_text"]:
                new_sub = {
                    "entity_id": main_node["entity_id"],
                    "mention_text": main_node["entity_text"]
                }
                new_obj = self.topic_node

            elif pred_obj == main_node["entity_text"] and pred_sub == self.topic_node["entity_text"]:
                new_sub = self.topic_node
                new_obj = {
                    "entity_id": main_node["entity_id"],
                    "mention_text": main_node["entity_text"]
                }

            else:
                print("Error: The predicted subject and object do not match the unvisited subject and topic entity, the LLM produce hallucination!")
                print(f"Hallucinated file name: {self.inFile}")
                new_sub = {
                    "entity_id": "hallucination",
                    "mention_text": "hallucination"
                }
                new_obj = {
                    "entity_id": "hallucination",
                    "mention_text": "hallucination"
                }

            self.predicted_triple = {
                "subject": new_sub,
                "relation": pred_rel,
                "object": new_obj
            }
            self.predicted_triples.append(self.predicted_triple)
            self.response_times.append(self.response_time)
            self.usages.append(self.usage)

        LP = {
            "predicted_links": self.predicted_triples,
            #response time equals to the sum of all response times
            "response_time": sum(self.response_times),
            "model": self.config.model,
            #usage equals to the sum of all usages
            "usage": {
                "input": {
                    "tokens": sum([usage["input"]["tokens"] for usage in self.usages]),
                    "cost": sum([usage["input"]["cost"] for usage in self.usages])
                },
                "output": {
                    "tokens": sum([usage["output"]["tokens"] for usage in self.usages]),
                    "cost": sum([usage["output"]["cost"] for usage in self.usages])
                },
                "total": {
                    "tokens": sum([usage["total"]["tokens"] for usage in self.usages]),
                    "cost": sum([usage["total"]["cost"] for usage in self.usages])
                }
            }
        }
        return LP

    def generate_prompt(self, main_node):
            env = Environment(loader=FileSystemLoader(self.config.link_prompt_folder))
            parsed_template = env.parse(env.loader.get_source(env, self.config.link_prompt_file)[0])
            template = env.get_template(self.config.link_prompt_file)
            variables = meta.find_undeclared_variables(parsed_template)

            if variables is not {}: # if template has variables
                    User_prompt = template.render(main_node=main_node["entity_text"], CTI=self.js["CTI"]["text"], topic_node=self.topic_node["entity_text"])
            else:
                User_prompt = template.render()
            prompt = [{"role": "user", "content": User_prompt}]

            subFolderPath = os.path.join(self.config.link_prompt_set, self.CTI_Source)
            os.makedirs(subFolderPath, exist_ok=True)
            with open(os.path.join(subFolderPath, self.inFile.split('.')[0] + ".txt"), 'w') as f:
                f.write(json.dumps(User_prompt, indent=4).replace("\\n", "\n").replace('\\"', '\"'))
            return prompt

        
    # def find_topic_entity(self):
    #     attack_malware_dict = {}
    #     for triple in self.js["EA"]["aligned_triplets"]:
    #          for key, node in triple.items():
    #              if key in ["subject", "object"]:
    #                  if node["mention_class"] == "Attacker" or node["mention_class"] == "Malware":
    #                     #check if the entity is in the attack_malware_dict
    #                     if node["entity_id"] in attack_malware_dict:
    #                         continue
    #                     else:
    #                         attack_malware_dict[node["entity_id"]] = {
    #                             "entity_text": node["mention_text"],
    #                             "mentions_time": len(node["mentions_merged"])
    #                         }
    #     #return the entity_id with the most mentions
    #     max_entity_id = max(attack_malware_dict, key=lambda x: attack_malware_dict[x]["mentions_time"])
    #     max_entity_text = attack_malware_dict[max_entity_id]["entity_text"]
    #     return {
    #         "entity_id": max_entity_id,
    #         "entity_text": max_entity_text
    #     }
    