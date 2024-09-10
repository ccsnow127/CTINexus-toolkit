import json
import os 
from omegaconf import DictConfig, OmegaConf
from LLMCaller import LLMCaller
from jinja2 import Template, Environment, FileSystemLoader, meta
import time
from usageCalculator import UsageCalculator


class LLMTagger:
    def __init__(self, config: DictConfig):
        self.config = config

    def tag(self, CTI_Source, file):
        inFile_path = os.path.join(self.config.inSet, CTI_Source, file)
        with open(inFile_path, 'r') as f:
            js = json.load(f)
            triples = js["IE"]["triplets"]
             
        self.prompt = self.generate_prompt(triples)
        folderPath = os.path.join(self.config.tag_prompt_store, CTI_Source)
        os.makedirs(folderPath, exist_ok=True)
        # FolderName = time.strftime("%Y-%m-%d-%H-%M")
        # subFolderPath = os.path.join(folderPath, FolderName)
        # os.makedirs(subFolderPath, exist_ok=True)
        self.promptPath = os.path.join(folderPath, file.split('.')[0] + ".txt")
        with open(self.promptPath, 'w') as f:
            f.write(json.dumps(self.prompt[0]["content"], indent=4).replace("\\n", "\n").replace('\\"', '\"'))
             
        self.response, self.response_time = LLMCaller(self.config, self.prompt).call()
        self.usage = UsageCalculator(self.response).calculate()
        
        self.response_content = json.loads(self.response.choices[0].message.content)
    
        outfolder = os.path.join(self.config.outSet, CTI_Source)
        os.makedirs(outfolder, exist_ok=True)
        outfile_path = os.path.join(outfolder, file)

        with open(outfile_path, 'w') as f:
            js["ET"] = {}
            js["ET"]["typed_triplets"] = self.response_content["tagged_triples"]
            js["ET"]["response_time"] = self.response_time
            js["ET"]["Demo_num"] = self.config.shot
            # js["ET"]["tag_prompt_template"] = self.config.tag_prompt_file
            js["ET"]["tag_prompt"] = self.promptPath
            js["ET"]["model_usage"] = self.usage
            json.dump(js, f, indent=4)
        

    def generate_prompt(self, triples):
            # Set up the environment and file loader
            env = Environment(loader=FileSystemLoader(self.config.tag_prompt_folder))
            template_file = env.loader.get_source(env, self.config.tag_prompt_file)[0]
            template = env.get_template(self.config.tag_prompt_file)

            # Find the undeclared variables in the template
            vars = meta.find_undeclared_variables(env.parse(template_file))
            
            if vars is not {}: # if template has variables
                UserPrompt = template.render(triples=triples)
            else:
                UserPrompt = template.render()
            
            prompt = [{"role": "user", "content": UserPrompt}]
            
            return prompt
