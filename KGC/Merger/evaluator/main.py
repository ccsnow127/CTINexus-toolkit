import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="config", config_name="model=SecureBert", version_base="1.2")
def run(config: DictConfig):
    #compare the jsonFile in the evalSet and the GTSet
    #traverse the evalSet, compare the corresponding file in the evalSet and the GTSet
    for CTI_source in os.listdir(config.evalSet):
        if CTI_source == "prompt_store":
            continue
        evalFolder = os.path.join(config.evalSet, CTI_source)
        GTFolder = os.path.join(config.GTSet, CTI_source)
        for file in os.listdir(evalFolder):
            evalFile = os.path.join(evalFolder, file)
            GTFile = os.path.join(GTFolder, file)
            with open(evalFile, 'r') as f:
                eval_data = json.load(f)
            with open(GTFile, 'r') as f:
                GT_data = json.load(f)
            eval = {
                "TP": 0,
                "FP": 0,
                "FN": 0,
                "TN": 0
            }
            #compare the eval_data[]

            #compare the eval_data['EA']['aligned_triplets'] with the GT_data['EA']['aligned_triplets']
            eval_aligned_triplets = eval_data['EA']['aligned_triplets']
            GT_aligned_triplets = GT_data['EA']['aligned_triplets']
            if len(eval_aligned_triplets) != len(GT_aligned_triplets):
                print(f"Error: {CTI_source}/{file} aligned_triplets length not equal")
            else:
                for eval_triplet, GT_triplet in zip(eval_aligned_triplets, GT_aligned_triplets):
                    eval_subject = eval_triplet['subject']
                    GT_subject = GT_triplet['subject']
                    eval_object = eval_triplet['object']
                    GT_object = GT_triplet['object']
                    eval_sub_merged = True if len(eval_subject['mentions_merged']) > 1 else False
                    GT_sub_merged = True if len(GT_subject['mentions_merged']) > 1 else False
                    eval_obj_merged = True if len(eval_object['mentions_merged']) > 1 else False
                    GT_obj_merged = True if len(GT_object['mentions_merged']) > 1 else False
                    if eval_sub_merged == True and GT_sub_merged == True:
                        eval['TP'] += 1
                    elif eval_sub_merged == True and GT_sub_merged == False:
                        eval['FP'] += 1
                    elif eval_sub_merged == False and GT_sub_merged == True:
                        eval['FN'] += 1
                    else:
                        eval['TN'] += 1
                    if eval_obj_merged == True and GT_obj_merged == True:
                        eval['TP'] += 1
                    elif eval_obj_merged == True and GT_obj_merged == False:
                        eval['FP'] += 1
                    elif eval_obj_merged == False and GT_obj_merged == True:
                        eval['FN'] += 1
                    else:
                        eval['TN'] += 1
                    eval_data['EA']['threshold'] = config.similarity_threshold
                    eval_data['EA']['Eval'] = eval
                with open(evalFile, 'w') as f:
                    json.dump(eval_data, f, indent=4)
                    


if __name__ == "__main__":
    run()