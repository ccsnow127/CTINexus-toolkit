import os 
import json


def calculate_overall_metrics():
    # Load all the metrics files
    metrics_files = []
    eval_set = "/home/yutong/CTINexus/Eval/RQ3/Tagger/GPT3.5-12shot"
    for dir in os.listdir(eval_set):
        if dir == "prompt_store":
                continue
        for file in os.listdir(os.path.join(eval_set, dir)):
            if file.endswith('.json'):
                metrics_files.append(os.path.join(eval_set, dir, file))
    # Calculate overall metrics
    overall_metrics = {
        'tp': 0,
        'fp': 0,
        'fn': 0,
        'tn': 0,
        'accuracy': 0,
        'micro-f1': 0,
        'macro-f1': 0,
        'Num_of_classes': 0,
    }
    fileNum = 0
    f1_scores = []
    for file in metrics_files:
        with open(file, 'r') as f:
            fileNum += 1
            data = json.load(f)
            metrics = data['ET']['Eval']
            overall_metrics['tp'] += metrics['TP']
            overall_metrics['fp'] += metrics['FP']
            overall_metrics['fn'] += metrics['FN']
            overall_metrics['tn'] += metrics['TN']
            overall_metrics['Num_of_classes'] += metrics['Num_of_classes']

            class_metrics = metrics['Macro-counters']
            for class_name, metrics in class_metrics.items():
                precision = metrics['TP'] / (metrics['TP'] + metrics['FP']) if metrics['TP'] + metrics['FP'] > 0 else 0
                recall = metrics['TP'] / (metrics['TP'] + metrics['FN']) if metrics['TP'] + metrics['FN'] > 0 else 0
                f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
                f1_scores.append(f1)

    precision = overall_metrics['tp'] / (overall_metrics['tp'] + overall_metrics['fp']) if overall_metrics['tp'] + overall_metrics['fp'] > 0 else 0
    recall = overall_metrics['tp'] / (overall_metrics['tp'] + overall_metrics['fn']) if overall_metrics['tp'] + overall_metrics['fn'] > 0 else 0
    overall_metrics['micro-f1'] = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    overall_metrics['Num_of_classes'] = overall_metrics['Num_of_classes'] / fileNum
    overall_metrics["macro-f1"] = sum(f1_scores) / len([score for score in f1_scores if score != 0]) if len(f1_scores) > 0 else 0
    overall_metrics['accuracy'] = (overall_metrics['tp'] + overall_metrics['tn']) / (overall_metrics['tp'] + overall_metrics['fp'] + overall_metrics['fn'] + overall_metrics['tn']) if overall_metrics['tp'] + overall_metrics['fp'] + overall_metrics['fn'] + overall_metrics['tn'] > 0 else 0


    outMetricSet = "/home/yutong/CTINexus/Eval/RQ3/Tagger/GPT3.5-12shot/prompt_store/metrics"
    with open(os.path.join(outMetricSet, 'overall_metrics.json'), 'w') as f:
        json.dump(overall_metrics, f, indent=4)

if __name__ == "__main__":
    overall_metrics = calculate_overall_metrics()
    print(overall_metrics)