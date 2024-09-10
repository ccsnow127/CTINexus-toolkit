
import os 
import json


def calculate_overall_metrics():
    # Load all the metrics files
    metrics_files = []
    eval_set = "/home/yutong/CTINexus/Eval/RQ3/Linker/2-shot-gpt-3.5-RE"
    for dir in os.listdir(eval_set):
        if dir == "prompt_store":
                continue
        for file in os.listdir(os.path.join(eval_set, dir)):
            if file.endswith('.json'):
                metrics_files.append(os.path.join(eval_set, dir, file))
    # Calculate overall metrics
    overall_metrics = {
        "correct": 0,
        "incorrect": 0,
        "accuracy": 0
    }
    fileNum = 0
    f1_scores = []
    for file in metrics_files:
        with open(file, 'r') as f:
            fileNum += 1
            data = json.load(f)
            metrics = data['LP']['Eval']
            overall_metrics['correct'] += metrics['correct']
            overall_metrics['incorrect'] += metrics['incorrect']

    overall_metrics['accuracy'] = overall_metrics['correct'] / (overall_metrics['correct'] + overall_metrics['incorrect']) if overall_metrics['correct'] + overall_metrics['incorrect'] > 0 else 0


    outMetricSet = "/home/yutong/CTINexus/Eval/RQ3/Linker/2-shot-gpt-3.5-RE/prompt_store/metrics"
    with open(os.path.join(outMetricSet, 'overall_metrics.json'), 'w') as f:
        json.dump(overall_metrics, f, indent=4)

if __name__ == "__main__":
    overall_metrics = calculate_overall_metrics()
    print(overall_metrics)