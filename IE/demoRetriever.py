import os
import random
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from nltk.corpus import stopwords
import re
import numpy as np
from scipy.spatial.distance import cosine

class DemoRetriever:
        def __init__(self, LLMAnnotator) -> None:
                self.inFile = LLMAnnotator.inFile
                self.config = LLMAnnotator.config
                self.inFileJSON = LLMAnnotator.inFileJSON
                self.CTI_Source = LLMAnnotator.CTI_Source

        def retrieveRandomDemo(self, k):
                documents = []
                with open(os.path.join(self.config.inSet, self.CTI_Source, self.inFile), "r") as f:
                        js = json.load(f)
                        documents.append((js["CTI"], self.inFile))
                for CTI_folder in os.listdir(self.config.demo_set):
                        if CTI_folder.endswith(".json"):
                                continue
                        if CTI_folder == "prompt_store":
                                continue
                        CTIfolderPath = os.path.join(self.config.demo_set, CTI_folder)
                        for JSONfile in os.listdir(CTIfolderPath):
                                if JSONfile == self.inFile:
                                        print("")
                                        continue
                                with open(os.path.join(CTIfolderPath, JSONfile), "r") as f:
                                        js = json.load(f)
                                        documents.append((((js["CTI"]["text"], js["IE"]["triplets"]), (JSONfile, "random"))))
                random.shuffle(documents)
                top_k = documents[:k]
                return [(demo[0][0], demo[0][1]) for demo in top_k], [(demo[1][0], demo[1][1]) for demo in top_k]


        def retrievekNNDemo(self, permutation, k): 
                documents = []
                with open(os.path.join(self.config.inSet, self.CTI_Source, self.inFile), "r") as f:
                        js = json.load(f)
                        documents.append((js["CTI"], self.inFile))
                for CTI_folder in os.listdir(self.config.demo_set):
                        if CTI_folder.endswith(".json"):
                                continue
                        if CTI_folder == "prompt_store":
                                continue
                        CTIfolderPath = os.path.join(self.config.demo_set, CTI_folder)
                        for JSONfile in os.listdir(CTIfolderPath):
                                if JSONfile == self.inFile:
                                        print("")
                                        continue
                                with open(os.path.join(CTIfolderPath, JSONfile), "r") as f:
                                        js = json.load(f)
                                        documents.append((js["CTI"]["text"], JSONfile))
                                
                documents_df = pd.DataFrame([doc[0] for doc in documents], columns=['documents'])

                # removing special characters and stop words from the text
                stop_words_l=stopwords.words('english')
                documents_df['documents_cleaned']=documents_df.documents.apply(lambda x: " ".join(re.sub(r'[^a-zA-Z]',' ',w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]',' ',w).lower() not in stop_words_l) )

                tfidfvectoriser=TfidfVectorizer()
                tfidfvectoriser.fit(documents_df.documents_cleaned)
                tfidf_vectors=tfidfvectoriser.transform(documents_df.documents_cleaned)

                pairwise_similarities=np.dot(tfidf_vectors,tfidf_vectors.T).toarray()
                pairwise_differences=euclidean_distances(tfidf_vectors)

                def most_similar(doc_id,similarity_matrix,matrix):
                        docs = []
                        if matrix=='Cosine Similarity':
                                similar_ix=np.argsort(similarity_matrix[doc_id])[::-1]
                        elif matrix=='Euclidean Distance':
                                similar_ix=np.argsort(similarity_matrix[doc_id])
                        for ix in similar_ix:
                                if ix==doc_id:
                                        continue
                                for doc in documents:
                                        if doc[0] == documents_df.iloc[ix]["documents"]:
                                                docs.append((doc, similarity_matrix[doc_id][ix]))
                        return docs

                top_k = most_similar(0,pairwise_similarities,'Cosine Similarity')[:k]
                if permutation == "desc":
                        return top_k
                elif permutation == "asc":
                        return top_k[::-1]
        
        def retriveDemo(self):
                if self.config.retriever["type"] == "kNN":
                        demos = self.retrievekNNDemo(self.config.retriever["permutation"], self.config.shot)
                        ConsturctedDemos = []
                        for demo in demos:
                                demoFileName = demo[0][1]
                                demoSimilarity = demo[1]
                                for CTI_folder in os.listdir(self.config.demo_set):
                                        if CTI_folder.endswith(".json"):
                                                continue
                                        if CTI_folder == "prompt_store":
                                                continue
                                        CTIfolderPath = os.path.join(self.config.demo_set, CTI_folder)
                                        for JSONfile in os.listdir(CTIfolderPath):
                                                if JSONfile == demoFileName:
                                                        demoFileName = f"{CTI_folder}: {demoFileName}"
                                                        with open(os.path.join(CTIfolderPath, JSONfile), "r") as f:
                                                                js = json.load(f)
                                                                ConsturctedDemos.append(((js["CTI"]["text"], js["IE"]["triplets"]), (demoFileName, demoSimilarity)))
                        return [(demo[0][0], demo[0][1]) for demo in ConsturctedDemos], [(demo[1][0], demo[1][1]) for demo in ConsturctedDemos]
                
                elif self.config.retriever["type"] == "rand":
                        return self.retrieveRandomDemo(self.config.shot)
                
                else:
                        print('Invalid retriever type. Please choose between "kNN", "random", and "fixed".')