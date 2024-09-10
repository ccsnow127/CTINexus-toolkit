import json

class InstructionLoader:
    def __init__(self, InstructionID):
        self.instructionID = InstructionID
        self.instructionfile = "Toolbox/instruction/instruction.json"
        with open(self.instructionfile, "r") as f:
            data = json.load(f)
        self.instruction= data[self.instructionID]
