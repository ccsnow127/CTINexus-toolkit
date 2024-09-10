import os 
import json


def addFP():
    # Load all the metrics files
    metrics_files = []
    eval_set = "/home/yutong/CTINexus/Eval/RQ2/DemoNum/2"
    for dirs in os.listdir(eval_set):
        if dirs == "prompt_store":
                continue
        for file in os.listdir(os.path.join(eval_set, dirs)):
            if file.endswith('.json'):
                metrics_files.append(os.path.join(eval_set, dirs, file))
    # Calculate the false negative through the not_recall_list
    fn = 0
    for file in metrics_files:
        with open(file, 'r') as f:
            data = json.load(f)
            fn += len(data['IE']['Eval']['not_recall_list'])
        # return fp
        with open(file, 'w') as f:
            data['IE']['Eval']['metrics']['fn'] = fn
            json.dump(data, f, indent=4)
            fn = 0

    # ###
    # fp = 0
    # for file in metrics_files:
    #     with open(file, 'r') as f:
    #         data = json.load(f)
    #         fp += len(data['IE']['Eval']['not_matched_list'])
    #     # return fp
    #     with open(file, 'w') as f:
    #         data['IE']['Eval']['metrics']['fp'] = fp
    #         json.dump(data, f, indent=4)
    #         fp = 0
    # ###
    

if __name__ == "__main__":
    addFP()