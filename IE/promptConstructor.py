import json
from jinja2 import Template, Environment, FileSystemLoader, meta

class PromptConstructor:
    def __init__(self, llmAnnotator):
        self.demos = llmAnnotator.demos
        self.config = llmAnnotator.config
        self.inFileJSON = llmAnnotator.inFileJSON
        self.query =  self.inFileJSON["CTI"]        
        self.templ = self.config.templ
    
    def generate_prompt(self):
                # Set up the environment and file loader
                env = Environment(loader=FileSystemLoader(self.config.ie_prompt_set))
                DymTemplate = self.templ
                template_source = env.loader.get_source(env, DymTemplate)[0]
                parsed_content = env.parse(template_source)
                variables = meta.find_undeclared_variables(parsed_content)

                # Load the template from the file
                template = env.get_template(DymTemplate)
                
                if variables is not {}: # if template has variables
                        Uprompt = template.render(demos=self.demos, query=self.query)
                else:
                    Uprompt = template.render()

                prompt = [{"role": "user", "content": Uprompt}]
                
                return prompt

    def ConstructPromptWithTemplate(self):
        prompt = self.generate_prompt()
        return prompt