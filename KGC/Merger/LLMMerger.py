import json
import os 
from omegaconf import DictConfig, OmegaConf
from jinja2 import Template, Environment, FileSystemLoader, meta
import openai
from scipy.spatial.distance import cosine
import itertools
import time
import torch
from transformers import BertTokenizer, BertModel
from transformers import RobertaTokenizer, RobertaModel



class LLMMerger:
    def __init__(self, merger):
        self.merger = merger
        self.config = merger.config
        self.tokenizer = RobertaTokenizer.from_pretrained("ehsanaghaei/SecureBERT")
        self.model = RobertaModel.from_pretrained("ehsanaghaei/SecureBERT")
        
    def merge(self, node_list):
        self.node_list = node_list
        self.js = self.merger.js

        node_embedding_list = self.get_embeddings(node_list)

        clusters = []

        for (mention_id_1, mention_embedding_1), (mention_id_2, mention_embedding_2) in itertools.combinations(node_embedding_list, 2):
            similarity = 1 - cosine(mention_embedding_1, mention_embedding_2)

            if similarity > self.config.similarity_threshold:
                # Check if either entity is already in a cluster
                if_in_cluster = False
                for cluster in clusters:
                    if mention_id_1 in cluster or mention_id_2 in cluster:
                        cluster.update([mention_id_1, mention_id_2])
                        if_in_cluster = True
                        break

                # If neither entity is in a cluster, create a new cluster
                if not if_in_cluster:
                    clusters.append(set([mention_id_1, mention_id_2]))

        # For entities that are not clustered, create individual clusters
        for (m_id, m_text) in node_list:
            if not any(m_id in cluster for cluster in clusters):
                clusters.append({m_id})

        # Convert sets to lists for output
        clusters = [list(cluster) for cluster in clusters]

        # Output the clusters
        for _, cluster in enumerate(clusters):
                if len(cluster) > 1:
                    for mention_id in cluster:
                        _node = self.retrieve_node(mention_id)
                        _node["entity_id"] = self.merger.entity_id
                        _node["mentions_merged"] = [self.retrieve_mention_text(mention_id) for mention_id in cluster]
                        _node["entity_text"] = self.get_freq_mentions(_node["mentions_merged"])

                else:#len(cluster) == 1
                    for mention_id in cluster:
                        _node = self.retrieve_node(mention_id)
                        _node["entity_id"] = self.merger.entity_id
                        _node["mentions_merged"] = [self.retrieve_mention_text(mention_id)]
                        _node["entity_text"] = _node["mentions_merged"][0]
                self.merger.entity_id += 1

    def get_embeddings(self, node_list):
        if self.config.embedding_model == 'secure-bert':
            return self.get_bert_embeddings(node_list)
        openai.api_key = self.config.api_key
        node_embedding_list = []
        for (mention_id, mention_text) in node_list:
            response = openai.Embedding.create(
                input=mention_text,
                engine=self.config.embedding_model
            )
            node_embedding_list.append((mention_id, response['data'][0]['embedding']))
        return node_embedding_list
    
    def get_bert_embeddings(self, node_list):
        node_embedding_list = []
        for (mention_id, mention_text) in node_list:
            # Tokenize the text
            inputs = self.tokenizer(mention_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
            # The last hidden state is the first element of outputs
            last_hidden_states = outputs.last_hidden_state
            # Pool the outputs into a single mean vector
            mean_embedding = torch.mean(last_hidden_states, dim=1).squeeze().numpy()
            node_embedding_list.append((mention_id, mean_embedding))
        return node_embedding_list
    
    def retrieve_mention_text(self, mention_id):
        for triple in self.js["EA"]["aligned_triplets"]:
            for key, node in triple.items():
                if key in ["subject", "object"]:
                    if node["mention_id"] == mention_id:
                        return node["mention_text"]
                    
    def retrieve_node(self, mention_id):
        for triple in self.js["EA"]["aligned_triplets"]:
            for key, node in triple.items():
                if key in ["subject", "object"]:
                    if node["mention_id"] == mention_id:
                        return node

    def get_max_prefix(self, mention_list):
        max_prefix = ''
        # sort the mention_list by length
        mention_list = sorted(mention_list, key=lambda x: len(x))
        for i in range(1, len(mention_list[0]) + 1):
            if all(mention.startswith(mention_list[0][:i]) for mention in mention_list):
                max_prefix = mention_list[0][:i]
            else:
                break
        return max_prefix
    
    def get_longest_common_string(self, mention_list):
        if len(mention_list) < 2:
            return mention_list
         # Initialize the matrix with zeros
        n = len(mention_list)
        lengths = [[0] * (len(mention_list[0]) + 1) for _ in range(len(mention_list[1]) + 1)]
        longest = 0  # Length of the longest common substring
        lcs_end = 0  # End index of the longest common substring in the first string

        # Build the matrix
        for i in range(1, len(mention_list[0]) + 1):
            for j in range(1, len(mention_list[1]) + 1):
                if mention_list[0][i - 1] == mention_list[1][j - 1]:
                    lengths[j][i] = lengths[j - 1][i - 1] + 1
                    if lengths[j][i] > longest:
                        longest = lengths[j][i]
                        lcs_end = i
                else:
                    lengths[j][i] = 0

        # The longest common substring
        lcs = mention_list[0][lcs_end - longest: lcs_end]

        # Check if the found substring is common in all other strings
        for i in range(2, n):
            if lcs not in mention_list[i]:
                return ''  # If not common in any one of the strings, return empty
        return lcs
    

    def get_freq_common_string(self, mention_list):
        # 创建一个字典来存储所有子字符串及其出现的频率
        substring_freq = {}

        # 遍历每个字符串，为其所有可能的子字符串更新频率
        for s in mention_list:
            n = len(s)
            for i in range(n):
                for j in range(i+1, n+1):
                    # 提取子字符串
                    substr = s[i:j]
                    if substr in substring_freq:
                        substring_freq[substr] += 1
                    else:
                        substring_freq[substr] = 1

        # 筛选出现频率大于等于2的子字符串
        common_substrings = {k: v for k, v in substring_freq.items() if v >= 2}

        # 如果没有找到任何公共子字符串，返回空字符串
        if not common_substrings:
            return ''

        # 返回最长的、频率最高的子字符串
        # 如果有多个这样的子字符串，返回其中任意一个
        return max(common_substrings.keys(), key=lambda x: (len(x), common_substrings[x]))
    
    def get_shortest_string(self, mention_list):
        return min(mention_list, key=len)
    
    def get_freq_mentions(self, mention_list):
        freq = {}
        for mention in mention_list:
            if mention in freq:
                freq[mention] += 1
            else:
                freq[mention] = 1
        fm = max(freq, key=freq.get)
        if freq[fm] > 1:
            return fm
        else:
            return self.get_shortest_string(mention_list)