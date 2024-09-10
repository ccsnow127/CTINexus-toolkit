from promptConstructor import PromptConstructor
from demoRetriever import DemoRetriever
from instructionLoader import InstructionLoader
from LLMcaller import LLMCaller
from responseParser import ResponseParser
import json
import os 

class LLMAnnotator:
    def __init__(self, config, CTI_Source, inFile):
        self.config = config
        self.CTI_Source = CTI_Source
        self.inFile = inFile
    
    def annotate(self):
        inFolder = os.path.join(self.config.inSet, self.CTI_Source)
        with open(os.path.join(inFolder, self.inFile), 'r') as f:
            self.inFileJSON = json.load(f)

        if self.config.retriever == "fixed":
            self.demos = ""
        else:
            self.demos, self.demosInfo = DemoRetriever(self).retriveDemo()

        self.inFilename = os.path.splitext(self.inFile)[0]

        self.prompt = PromptConstructor(self).generate_prompt()

        self.llm_response, self.response_time, self.JSONResp = LLMCaller(self.config, self.prompt).call()
        
        self.output = ResponseParser(self).parse()

        self.promptID = self.llm_response.id[-3:]
        templ = self.config.templ.split('.')[0]

        self.outPromptFolder = os.path.join(self.config.ie_prompt_store, self.CTI_Source)
        os.makedirs(self.outPromptFolder, exist_ok=True)

        self.outPromptFile = os.path.join(self.outPromptFolder, f'{self.inFilename}-{templ}-{self.promptID}.jinja')

        with open(self.outPromptFile, 'w') as f:
            json_str = json.dumps(self.output["prompt"])
            json_str = json_str.replace("\\n", "\n")
            f.write(json_str)
        
        self.outFolder = os.path.join(self.config.outSet, self.CTI_Source)
        os.makedirs(self.outFolder, exist_ok=True)
        
        self.outFile = os.path.join(self.outFolder, f'{self.inFilename}.json')

        with open(self.outFile, 'w') as f:
            outJSON = {}
            ###CTI
            outJSON["CTI"] = {}
            outJSON["CTI"]["text"] = self.output["CTI"]
            outJSON["CTI"]["link"] = self.output["link"]
            ###IE results
            outJSON["IE"] = {}
            outJSON["IE"]["triplets"] = self.output["annotator"]["triplets"]
            outJSON["IE"]["triples_count"] = self.output["annotator"]["triples_count"]
            outJSON["IE"]["cost"] = self.output["usage"]
            outJSON["IE"]["time"] = self.response_time
            ###Prompt
            outJSON["IE"]["Prompt"] = {}
            outJSON["IE"]["Prompt"]["constructed_prompt"] = self.outPromptFile
            outJSON["IE"]["Prompt"]["prompt_template"] = self.config.templ
            outJSON["IE"]["Prompt"]["demo_retriever"]= self.config.retriever.type
            outJSON["IE"]["Prompt"]["demo_number"] = self.config.shot
            outJSON["IE"]["Prompt"]["demos"] = self.demosInfo
            if self.config.retriever.type == "kNN":
                outJSON["IE"]["Prompt"]["permutation"] = self.config.retriever.permutation
            #write to file
            json.dump(outJSON, f, indent=4)