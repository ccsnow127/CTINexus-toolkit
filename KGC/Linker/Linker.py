import json
import os 
from omegaconf import DictConfig, OmegaConf
from LLMLinker import LLMLinker
from collections import defaultdict

class Linker:
    def __init__(self, config: DictConfig, CTI_Source, inFile):
        self.config = config
        self.CTI_Source = CTI_Source
        self.inFile = inFile


        infile_path = os.path.join(self.config.inSet, self.CTI_Source, self.inFile)
        with open(infile_path, 'r') as f:
            self.js = json.load(f)
            self.aligned_triplets = self.js["EA"]["aligned_triplets"]

        self.graph = {}
        
        # 构建一个图的邻接列表来表示这些三元组的连接
        

        # 填充图
        for triplet in self.aligned_triplets:
            subject_entity_id = triplet["subject"]["entity_id"]
            object_entity_id = triplet["object"]["entity_id"]
            
            if subject_entity_id not in self.graph:
                self.graph[subject_entity_id] = []
            if object_entity_id not in self.graph:
                self.graph[object_entity_id] = []
            
            # 添加无向边
            self.graph[subject_entity_id].append(object_entity_id)
            self.graph[object_entity_id].append(subject_entity_id)

        self.subgraphs = self.find_disconnected_subgraphs()
        self.main_nodes = []
        # # 使用DFS来检查连通性
        # self.visited = set()

        # 对于每个子图，找到主节点
        for i, subgraph in enumerate(self.subgraphs):
            main_node_entity_id = self.get_main_node(subgraph)
            main_node = self.get_node(main_node_entity_id)
            print(f"subgraph {i}: main node: {main_node['entity_text']}")
            self.main_nodes.append(main_node)

        # # 从第一个节点开始DFS
        # self.dfs(next(iter(self.graph)))

        # # 检查是否访问了所有节点
        # is_connected = len(self.visited) == len(self.graph)
        # print(f"Is the graph connected? {is_connected}")

        # # 如果图不是连通的，对于未访问的子图，再使用dfs
        # if not is_connected:
        #     for node in self.graph.keys():
        #         if node not in self.visited:
        #             self.dfs(node)

        # unvisited_nodes = set(self.graph.keys()) - self.visited
        # print(f"Unvisited nodes: {unvisited_nodes}")

        # unvisted_subjects = {}
        # for triplet in aligned_triplets:
        #     if triplet["subject"]["entity_id"] in unvisited_nodes:
        #         unvisted_subjects[triplet["subject"]["entity_id"]] = triplet["subject"]

        self.topic_node = self.get_topic_node(self.subgraphs)
        #exclude the topic node from the main nodes
        self.main_nodes = [node for node in self.main_nodes if node["entity_id"] != self.topic_node["entity_id"]]
        self.js["LP"] = LLMLinker(self).link()
        self.js["LP"]["topic_node"] = self.topic_node
        self.js["LP"]["main_nodes"] = self.main_nodes
        self.js["LP"]["subgraphs"] = [list(subgraph) for subgraph in self.subgraphs]
        self.js["LP"]["subgraph_num"] = len(self.subgraphs)
        
        outfolder = os.path.join(self.config.outSet, self.CTI_Source)
        os.makedirs(outfolder, exist_ok=True)
        outfile_path = os.path.join(outfolder, self.inFile)

        with open(outfile_path, 'w') as f:
            json.dump(self.js, f, indent=4)


    # def dfs(self, node):
    #     if node in self.visited:
    #         return
    #     self.visited.add(node)
    #     for neighbour in self.graph[node]:
    #         self.dfs(neighbour)

    def find_disconnected_subgraphs(self):
        self.visited = set()
        subgraphs = []

        for start_node in self.graph.keys():
            if start_node not in self.visited:
                # 每次找到一个新的子图时，清空当前的访问记录，但只记录这个子图的访问
                current_subgraph = set()
                self.dfs_collect(start_node, current_subgraph)
                subgraphs.append(current_subgraph)

        return subgraphs

    def dfs_collect(self, node, current_subgraph):
        if node in self.visited:
            return
        self.visited.add(node)
        current_subgraph.add(node)  # 添加节点到当前子图
        for neighbour in self.graph[node]:
            self.dfs_collect(neighbour, current_subgraph)

    def get_main_node(self, subgraph):
        # 统计每个节点的出度
        outdegrees = defaultdict(int)
        self.directed_graph = {}
        #build directed graph
        for triplet in self.aligned_triplets:
            subject_entity_id = triplet["subject"]["entity_id"]
            object_entity_id = triplet["object"]["entity_id"]
            if subject_entity_id not in self.directed_graph:
                self.directed_graph[subject_entity_id] = []
            self.directed_graph[subject_entity_id].append(object_entity_id)
            outdegrees[subject_entity_id] += 1
            outdegrees[object_entity_id] += 1
        #找到出度最大的节点
        max_outdegree = 0
        main_node = None
        for node in subgraph:
            if outdegrees[node] > max_outdegree:
                max_outdegree = outdegrees[node]
                main_node = node
        return main_node
    
    def get_node(self, entity_id):
        for triplet in self.aligned_triplets:
            for key, node in triplet.items():
                if key in ["subject", "object"]:
                    if node["entity_id"] == entity_id:
                        return node
                    

    def get_topic_node(self, subgraphs):
        #节点数最多的子图为主节点所在图
        max_node_num = 0
        for subgraph in subgraphs:
            if len(subgraph) > max_node_num:
                max_node_num = len(subgraph)
                main_subgraph = subgraph
        #找到最大图的主节点
        return self.get_node(self.get_main_node(main_subgraph))