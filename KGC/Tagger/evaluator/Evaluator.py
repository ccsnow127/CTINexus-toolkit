import json
import os

class Evaluator:
    def __init__(self, config, CTI_Source, JSONFile):
        self.config = config
        self.CTI_Source = CTI_Source
        self.JSONFile = JSONFile

    def evaluate(self):
        paired_tuples = []
        self.correct = 0
        self.incorrect = 0
        self.TP = 0
        self.TN = 0
        self.FP = 0
        self.FN = 0

        negative_class = "This entity cannot be classified into any of the existing types"

        categories = [
            "Account",
            "Credential",
            "Tool",
            "Attacker",
            "Event",
            "Exploit Target",
            "Indicator",
            "Information",
            "Location",
            "Malware",
            "Malware Characteristic",
            "Organization",
            "Infrastructure",
            "Time",
            "Vulnerability",
            "This entity cannot be classified into any of the existing types"
        ]
        # Initialize counters for each category
        counters = {category: {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0} for category in categories}

        with open(os.path.join(self.config.ground_truth_set, self.CTI_Source, self.JSONFile), 'r') as f:
            self.GT_JSONTriplets = json.load(f)['ET']['typed_triplets']
        with open(os.path.join(self.config.inSet, self.CTI_Source, self.JSONFile), 'r') as f:
            self.eval_JSONFile = json.load(f)
            self.eval_JSONTriplets = self.eval_JSONFile['ET']['typed_triplets']

        for eval_triplet, gt_triplet in zip(self.eval_JSONTriplets, self.GT_JSONTriplets):
            try:
                paired_subject = [eval_triplet['subject'], gt_triplet['subject']]
                paired_tuples.append(paired_subject)
            except:
                pass
            try:
                paired_object = [eval_triplet['object'], gt_triplet['object']]
                paired_tuples.append(paired_object)
            except:
                pass
            
        # paired_tuples are list of json objects with keys 'text' and 'class'
        for paired_tuple in paired_tuples:
            try:
                eval_class = paired_tuple[0]['class']
            except:
                eval_class = negative_class
            gt_class = paired_tuple[1]['class']
            if ":" in eval_class:
                eval_class = eval_class.split(":")[0]
            if ":" in gt_class:
                gt_class = gt_class.split(":")[0]

            if eval_class not in categories:
                eval_class = negative_class
            if gt_class not in categories:
                gt_class = negative_class

            if eval_class == gt_class:
                counters[eval_class]['TP'] += 1
                for category in categories:
                    if category != eval_class:
                        counters[category]['TN'] += 1
                self.correct += 1
                if eval_class != negative_class:
                    self.TP += 1
                else:
                    self.TN += 1
            else:
                counters[eval_class]['FP'] += 1
                counters[gt_class]['FN'] += 1
                for category in categories:
                    if category != eval_class and category != gt_class:
                        counters[category]['TN'] += 1
                self.incorrect += 1
                if eval_class == negative_class:
                    self.FN += 1
                elif gt_class == negative_class:
                    self.TN += 1  # Correcting this to FP as it's a false alarm, not a true negative.
                    self.FP += 1  # This is the correct line for counting false positives.
                else:
                    self.FP += 1 
        
        self.eval_JSONFile['ET']['Eval'] = {}
        self.eval_JSONFile ['ET']['Eval']['correct'] = self.correct
        self.eval_JSONFile ['ET']['Eval']['incorrect'] = self.incorrect
        self.eval_JSONFile ['ET']['Eval']['TP'] = self.TP
        self.eval_JSONFile ['ET']['Eval']['TN'] = self.TN
        self.eval_JSONFile ['ET']['Eval']['FP'] = self.FP
        self.eval_JSONFile ['ET']['Eval']['FN'] = self.FN
        self.eval_JSONFile ['ET']['Eval']['Macro-counters'] = counters
        self.eval_JSONFile ['ET']['Eval']['Num_of_classes'] = self.eval_JSONFile['ET']['Eval']['Num_of_classes'] = len([category for category in categories if counters[category]['TP'] + counters[category]['FP'] > 0])




        with open(os.path.join(self.config.inSet, self.CTI_Source, self.JSONFile), 'w') as f:
            json.dump(self.eval_JSONFile, f, indent=4)
        