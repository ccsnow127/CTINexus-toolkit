import openai

class LLMCaller:
    def __init__(self, config):
        self.config = config

    def call(self, relation):
        openai.api_key = self.config.api_key
        #call the LLM model to predict the links
        embedding_model = self.config.embedding_model
        #embed the relation
        #use the openAI embedding model
        response = openai.Embedding.create(
                input=relation,
                engine=self.config.embedding_model
        )
        return response['data'][0]['embedding']