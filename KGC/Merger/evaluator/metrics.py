import os 
import json


def calculate_overall_metrics():
    # Load all the metrics files
    metrics_files = []
    eval_set = "/home/yutong/CTINexus/Eval/RQ3/Merger/Embedding/Merger-output-0.6-secureBert"
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
        'precision': 0,
        'recall': 0,
        'f1': 0,
        'Num_of_mentions': 0,
        'Num_of_entities': 0,
    }
    fileNum = 0
    f1_scores = []
    for file in metrics_files:
        with open(file, 'r') as f:
            fileNum += 1
            data = json.load(f)
            metrics = data['EA']['Eval']
            overall_metrics['tp'] += metrics['TP']
            overall_metrics['fp'] += metrics['FP']
            overall_metrics['fn'] += metrics['FN']
            # overall_metrics['tn'] += metrics['TN']
            overall_metrics['Num_of_mentions'] += data['EA']['mentions_num']
            overall_metrics['Num_of_entities'] += data['EA']['entity_num']

    overall_metrics['precision'] = overall_metrics['tp'] / (overall_metrics['tp'] + overall_metrics['fp']) if overall_metrics['tp'] + overall_metrics['fp'] > 0 else 0
    overall_metrics['recall'] = overall_metrics['tp'] / (overall_metrics['tp'] + overall_metrics['fn']) if overall_metrics['tp'] + overall_metrics['fn'] > 0 else 0
    overall_metrics['f1'] = 2 * overall_metrics['precision'] * overall_metrics['recall'] / (overall_metrics['precision'] + overall_metrics['recall']) if overall_metrics['precision'] + overall_metrics['recall'] > 0 else 0
    overall_metrics['Num_of_mentions'] = overall_metrics['Num_of_mentions'] / fileNum
    overall_metrics['Num_of_entities'] = overall_metrics['Num_of_entities'] / fileNum


    outMetricSet = "/home/yutong/CTINexus/Eval/RQ3/Merger/Embedding/Merger-output-0.6-secureBert/prompt_store/metrics"
    with open(os.path.join(outMetricSet, 'overall_metrics.json'), 'w') as f:
        json.dump(overall_metrics, f, indent=4)

if __name__ == "__main__":
    overall_metrics = calculate_overall_metrics()
    print(overall_metrics)