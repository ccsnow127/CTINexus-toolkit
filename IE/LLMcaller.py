from openai import OpenAI
import time
import json
import logging
LOG = logging.getLogger(__name__)
import requests

class LLMCaller:
    def __init__(self, config, prompt):
        self.config = config  
        self.prompt = prompt

    def query_llama(self, payload):
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
        headers = {"Authorization": "Bearer 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"}
        response = requests.post(API_URL, headers=headers, json=payload)
        # return response.json()
        print("")
        return response.json()


    def call(self):
        startTime = time.time()
        if self.config.model == "LLaMA":
            # input = {"role": "user", "content": "Write me a paragraph about the history of the United States."}
            input = {"role": "user", "content": self.prompt}
            input_str = json.dumps(input)
            payload = {
                'inputs': input_str,
            }
            
            response = self.query_llama(payload)
        else:
            attempts = 0
            max_attempts = 5
            success = False
            while attempts < max_attempts and not success:
                client = OpenAI(api_key=self.config.api_key)
                response = client.chat.completions.create(
                    model = self.config.model,
                    response_format = { "type": "json_object" },
                    messages = self.prompt,
                    max_tokens= 4096,
                )
                try:
                    JSONResp = json.loads(response.choices[0].message.content)
                    JSONResp["triplets"]
                    success = True
                except (json.decoder.JSONDecodeError, KeyError) as e:
                    attempts += 1
                    LOG.error(f"Attempt {attempts}: {str(e)}")
                    if attempts < max_attempts:
                        LOG.info("Retrying...")
                    else:
                        LOG.error("Maximum attempts reached. Failing...")
                        raise e 
                    
        endTime = time.time()
        generation_time = endTime - startTime

        return response, generation_time, JSONResp