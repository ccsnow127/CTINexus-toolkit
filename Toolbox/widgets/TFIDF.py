import pandas as pd
import numpy as np
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
import re
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import os 
import json
import hydra
from omegaconf import DictConfig, OmegaConf
import openai
import time

@hydra.main(config_path="config", config_name="config6", version_base="1.2")
def run(config: DictConfig):

    documents = []
    for CTI_folder in os.listdir(config.demo_set):
        if CTI_folder.endswith(".json"):
            continue
        CTIfolderPath = os.path.join(config.demo_set, CTI_folder)
        for JSONfile in os.listdir(CTIfolderPath):
            with open(os.path.join(CTIfolderPath, JSONfile), "r") as f:
                js = json.load(f)
                documents.append(js["CTI"])
                
    documents_df=pd.DataFrame(documents,columns=['documents'])

    # removing special characters and stop words from the text
    stop_words_l=stopwords.words('english')
    documents_df['documents_cleaned']=documents_df.documents.apply(lambda x: " ".join(re.sub(r'[^a-zA-Z]',' ',w).lower() for w in x.split() if re.sub(r'[^a-zA-Z]',' ',w).lower() not in stop_words_l) )

    tfidfvectoriser=TfidfVectorizer()
    tfidfvectoriser.fit(documents_df.documents_cleaned)
    tfidf_vectors=tfidfvectoriser.transform(documents_df.documents_cleaned)

    pairwise_similarities=np.dot(tfidf_vectors,tfidf_vectors.T).toarray()
    pairwise_differences=euclidean_distances(tfidf_vectors)

    def most_similar(doc_id,similarity_matrix,matrix):
        print (f'Document: {documents_df.iloc[doc_id]["documents"]}')
        print ('\n')
        print ('Similar Documents:')
        if matrix=='Cosine Similarity':
            similar_ix=np.argsort(similarity_matrix[doc_id])[::-1]
        elif matrix=='Euclidean Distance':
            similar_ix=np.argsort(similarity_matrix[doc_id])
        for ix in similar_ix:
            if ix==doc_id:
                continue
            print('\n')
            print (f'Document: {documents_df.iloc[ix]["documents"]}')
            print (f'{matrix} : {similarity_matrix[doc_id][ix]}')

    most_similar(0,pairwise_similarities,'Cosine Similarity')
    most_similar(0,pairwise_differences,'Euclidean Distance')               

if __name__ == "__main__":
    run()