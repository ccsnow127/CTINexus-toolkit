import os
import json
from LLMCaller import LLMCaller
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

class Evaluator:
    def __init__(self, config, CTI_Source, inFile):
        self.config = config
        self.CTI_Source = CTI_Source
        self.inFile = inFile
        self.tfidf_vectorizer = TfidfVectorizer()
        with open(os.path.join(self.config.inSet, self.CTI_Source, self.inFile)) as f:
            self.inFileJSON = json.load(f)
            self.CTI = self.inFileJSON["CTI"]["text"]
        # self.relation_cache = {}
        
    def evaluate(self):
        self.Eval = {
            "correct": 0,
            "incorrect": 0
        }
        #check if the predicted triples' relations and the ground truth triples' relations have similarity score higher than or equal to 0.5
        #if yes, then the predicted triple is correct

        #load the predicted triples
        with open(os.path.join(self.config.inSet, self.CTI_Source, self.inFile)) as f:
            eval_js = json.load(f)
            predicted_triples = eval_js["LP"]["predicted_links"]

        #load the ground truth triples
        with open(os.path.join(self.config.GTSet, self.CTI_Source, self.inFile)) as f:
            GT_js = json.load(f)
            ground_truth_triples = GT_js["LP"]["predicted_links"]
        
        #calculate the similarity score between the predicted triples' relations and the ground truth triples' relations

        #use the self.config.thresh to determine the threshold for the similarity score
        #use the self.config.embedding_model to embed the predicted triples' relations and the ground truth triples' relations
        #use the entity_id to identify the relations
        for predicted_triple in predicted_triples:
            if predicted_triple["subject"]["mention_text"] == "hallucination" or predicted_triple["object"]["mention_text"] == "hallucination":
                continue
            # nodes = set()
            nodes = []
            for key, val in predicted_triple.items():
                if key == "relation":
                    continue
                # nodes.add(val["entity_id"])
                nodes.append(val["mention_text"])
            for ground_truth_triple in ground_truth_triples:
                # gt_nodes = set()
                gt_nodes = []
                for key, val in ground_truth_triple.items():
                    if key == "relation":
                        continue
                    # gt_nodes.add(val["entity_id"])
                    gt_nodes.append(val["mention_text"])
                if nodes == gt_nodes:
                    eval_relation = predicted_triple["relation"]
                    gt_relation = ground_truth_triple["relation"]
                elif nodes[0] == gt_nodes[1] and nodes[1] == gt_nodes[0]:
                    eval_relation = predicted_triple["relation"]
                    gt_relation = ground_truth_triple["relation"]
                    # eval_relation = " ".join([predicted_triple["object"]["mention_text"], predicted_triple["relation"], predicted_triple["subject"]["mention_text"]])
                    # gt_relation = " ".join([ground_truth_triple["subject"]["mention_text"], ground_truth_triple["relation"], ground_truth_triple["object"]["mention_text"]])
                    # eval_relation = " ".join([predicted_triple["subject"]["mention_text"], predicted_triple["relation"], predicted_triple["object"]["mention_text"]])
                    # gt_relation = " ".join([ground_truth_triple["subject"]["mention_text"], ground_truth_triple["relation"], ground_truth_triple["object"]["mention_text"]])
                    
                    # eval_relation_emb = self.get_embedding(eval_relation)
                    # gt_relation_emb = self.get_embedding(gt_relation)
                else:
                    continue
                eval_relation_emb, gt_relation_emb = self.get_embedding(eval_relation, gt_relation)
                similarity_score = 1 - cosine(eval_relation_emb, gt_relation_emb)
                similarity_score = round(similarity_score, 2)
                if similarity_score >= self.config.thresh:
                    self.Eval["correct"] += 1
                else:
                    self.Eval["incorrect"] += 1
                break
            
                    
                    # eval_relation_emb = self.get_embedding(eval_relation)
                    # gt_relation_emb = self.get_embedding(gt_relation)
                    
        eval_js["LP"]["Eval"] = self.Eval
            

        #output the evaluation results
        with open(os.path.join(self.config.outSet, self.CTI_Source, self.inFile), 'w') as f:
            json.dump(eval_js, f, indent=4)
                


    def get_embedding(self, eval_relation, gt_relation):
        # documents_df = pd.DataFrame([eval_relation, gt_relation], columns=['documents'])
        # self.tfidf_vectorizer.fit(documents_df['documents'])
        # tfidf_vectors = self.tfidf_vectorizer.transform(documents_df['documents'])
        # return tfidf_vectors.toarray()[0], tfidf_vectors.toarray()[1]
        caller = LLMCaller(self.config)
        eval_relation_emb = caller.call(eval_relation)
        gt_relation_emb = caller.call(gt_relation)
        return eval_relation_emb, gt_relation_emb
