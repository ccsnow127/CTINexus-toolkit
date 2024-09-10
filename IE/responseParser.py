import json
from usageCalculator import UsageCalculator
import logging
LOG = logging.getLogger(__name__)

class ResponseParser:
    def __init__(self, llmAnnotator) -> None:
        self.llm_response = llmAnnotator.llm_response
        self.prompt = llmAnnotator.prompt
        self.query = llmAnnotator.inFileJSON["CTI"]
        self.link = llmAnnotator.inFileJSON["link"]
        self.config = llmAnnotator.config
        self.JSONResp = llmAnnotator.JSONResp

    def parse(self):
        #construct output
        # try:
        #     responseJSON = json.loads(self.llm_response.choices[0].message.content)
        # except json.decoder.JSONDecodeError:
        #     LOG.error("Error decoding JSON")
        #     LOG.info(f"LLM's output: {self.llm_response.choices[0].message.content}")
        #     raise

        self.output = {
            "CTI": self.query,
            "annotator": self.JSONResp,
            "link": self.link,
            "usage": UsageCalculator(self.llm_response).calculate(),
            "prompt": self.prompt,
        }
        # try:
        #     self.output["annotator"]["triplets"]
        # except KeyError:
        #     LOG.error("No triplets found in LLM's output")
        #     LOG.info(f"LLM's output: {self.llm_response.choices[0].message.content}")
        #     raise
        count = len(self.output["annotator"]["triplets"])
        self.output["annotator"]["triples_count"] = count

        return self.output