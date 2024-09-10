import json
import os 
from scipy.spatial.distance import cosine
import openai
import time

class LLMEvaluator:
    def __init__(self, config, CTI_Source, inFile):
        self.config = config
        self.CTI_Source = CTI_Source
        self.inFile = inFile
        self.GTSet = self.config.ground_truth_set
        openai.api_key = self.config.openai_key
        self.matched_list = []
        self.not_matched_list = []
        self.not_recall_list = []
    
    def evaluate(self):
        GT_file = os.path.join(self.GTSet, self.CTI_Source, self.inFile)
        with open(GT_file, 'r') as f:
            GT = json.load(f)
            GT_triplets = GT['IE']['triplets']
        
        Eval_file = os.path.join(self.config.inSet, self.CTI_Source, self.inFile)
        with open(Eval_file, 'r') as f:
            Eval = json.load(f)
            Eval_triplets = Eval['IE']['triplets']
            
        tp, fp, fn = self.evaluate_similarity(GT_triplets, Eval_triplets)
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0        
        # print(f'Precision: {precision}, Recall: {recall}, F1: {f1}')
        outFolder = os.path.join(self.config.outSet, self.CTI_Source)
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)
        # with open(os.path.join(outFolder, self.inFile), 'w') as f:
        #     json.dump(Eval, f, indent=4)

        outFile = os.path.join(outFolder, self.inFile)
        with open(outFile, 'w') as f:
            Eval['IE']['Eval'] = {}
            Eval['IE']['Eval']['metrics'] = {
                'tp': tp,
                'fp': fp,
                'fn': fn,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
            Eval['IE']['Eval']['matched_list'] = self.matched_list
            Eval['IE']['Eval']['not_matched_list'] = self.not_matched_list
            Eval['IE']['Eval']['not_recall_list'] = self.not_recall_list
            Eval["IE"]["Eval"]["thresh"] = self.config.thresh
            json.dump(Eval, f, indent=4)

    
    def get_embedding(self, text):
        #remove stop words and stemming
        # from nltk.corpus import stopwords
        # from nltk.stem import PorterStemmer
        # from nltk.tokenize import word_tokenize
        # import nltk
        # nltk.download('punkt')
        # nltk.download('stopwords')

        # Tokenize the text
        # words = word_tokenize(text)

        # # Remove stop words
        # stop_words = set(stopwords.words('english'))
        # filtered_words = [word for word in words if word not in stop_words]

        # # Stemming
        # stemmer = PorterStemmer()
        # stemmed_words = [stemmer.stem(word) for word in filtered_words]

        # Reconstruct the text
        # processed_text = " ".join(stemmed_words)
        # Specify the engine you want to use for embeddings
        engine = self.config.embedding_model  # Example engine, choose based on your needs
        attempts = 0
        while attempts < 5:  # Retry up to 3 times
            try:
                response = openai.Embedding.create(
                    input=text,
                    engine=engine
                )
                # Extract the embedding vector; adjust as needed based on response structure
                embedding = response['data'][0]['embedding']
                return embedding
            except Exception as e:
                print(f"Error obtaining embedding for text '{text}': {e}")
                attempts += 1
                time.sleep(3)  # Wait for 3 seconds before retrying
        return None  # Return None if all attempts fail
        
    def evaluate_similarity(self, gt_triplets, eval_triplets):
        threshold = self.config.thresh
        tp, fp, fn = 0, 0, 0
        matched_gt = set()
        # embedding_cache = {}  # Initialize the cache
        str_embedding_cache = {}

        for eval_triplet in eval_triplets:
            try:
                eval_triplet['subject']
            except:
                eval_triplet['subject'] = ""
            try:
                eval_triplet['object']
            except:
                eval_triplet['object'] = ""
            try:
                eval_triplet['relation']
            except:
                eval_triplet['relation'] = ""

            eval_subject, eval_object, eval_rel = eval_triplet['subject'], eval_triplet['object'], eval_triplet['relation']
            
            
            if isinstance(eval_subject, list):
                eval_subject = " ".join(eval_subject)
            if isinstance(eval_object, list):
                eval_object = " ".join(eval_object)
            if eval_subject is None:
                eval_subject = ""
            if eval_object is None:
                eval_object = ""
            
            
            eval_str = " ".join([eval_subject, eval_rel, eval_object])
            reverse_eval_str = " ".join([eval_object, eval_rel, eval_subject])

          
            
            if eval_str not in str_embedding_cache:
                str_embedding_cache[eval_str] = self.get_embedding(eval_str)
            eval_str_embedding = str_embedding_cache[eval_str]
            if reverse_eval_str not in str_embedding_cache:
                str_embedding_cache[reverse_eval_str] = self.get_embedding(reverse_eval_str)
            reverse_eval_str_embedding = str_embedding_cache[reverse_eval_str]

            str_match_found = False

            matched_gt_list = []
            for gt_triplet in gt_triplets:
                gt_subject, gt_object, gt_rel = gt_triplet['subject'], gt_triplet['object'], gt_triplet['relation']
                gt_str = " ".join([gt_subject, gt_rel, gt_object])

                if gt_str not in str_embedding_cache:
                    str_embedding_cache[gt_str] = self.get_embedding(gt_str)
                gt_str_embedding = str_embedding_cache[gt_str]

                str_similarity = 1 - cosine(eval_str_embedding, gt_str_embedding)
                reverse_str_similarity = 1 - cosine(reverse_eval_str_embedding, gt_str_embedding)

                if str_similarity >= threshold or reverse_str_similarity >= threshold:
                    matched_gt_list.append([gt_str, gt_triplet, max(str_similarity, reverse_str_similarity)])
                    str_match_found = True
                    matched_gt.add(tuple(gt_triplet.values()))


            if matched_gt_list:
                matched_gt_list.sort(key=lambda x: x[2], reverse=True)
                #get the gt_str wuth the highest similarity
                gt_str, gt_triplet = matched_gt_list[0][0], matched_gt_list[0][1]
                # if matched_gt_list[0][2]>threshold:
                # str_match_found = True
                tp += 1
                self.matched_list.append([[eval_subject, eval_rel, eval_object], [gt_triplet['subject'], gt_triplet['relation'], gt_triplet['object']]])
                # matched_gt.add(tuple(gt_triplet.values()))

                # tp += 1
                # self.matched_list.append([[eval_subject, eval_rel, eval_object], [gt_triplet['subject'], gt_triplet['relation'], gt_triplet['object']]])
                # matched_gt.add(tuple(gt_triplet.values()))

            # if not match_found:
            if not str_match_found:
                fp += 1
                self.not_matched_list.append([eval_subject, eval_rel, eval_object])

        # Calculate FN by checking which GT triplets weren't matched
        for gt_triplet in gt_triplets:
            if tuple(gt_triplet.values()) not in matched_gt:
                fn += 1
                self.not_recall_list.append([gt_triplet['subject'], gt_triplet['relation'], gt_triplet['object']])

        return tp, fp, fn


