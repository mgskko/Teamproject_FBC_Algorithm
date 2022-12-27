#
# team 6
# 고명석, 배재익, 이정연
#
from collections import deque

import matplotlib.pyplot as plt
import numpy as np


class F_SCORE:
    def __init__(self, source_file_list, ground_truth_filename):
        self.file_name = source_file_list
        self.ground_truth_filename = ground_truth_filename
        self.ground_truth = []
        self.avg_f_score = []
        self.cluster = []

    def set_ground_truth(self):
        with open(self.ground_truth_filename, 'r') as ground_truth_file:
            for lines in ground_truth_file:
                self.ground_truth.append([i for i in lines.strip().split(' ')])

    def get_cluster(self, filename):
        self.cluster = []
        with open(filename, 'r') as file:
            for line in file:
                self.cluster.append([i for i in line.strip().split(' ')][2:])
            file.close()

    def append_avg_f_score(self, x):
        result = []
        for X in x:
            set_x = set(X)
            x_size = len(X)
            max_f_score = 0
            for Y in self.ground_truth:
                set_y = set(Y)
                y_size = len(Y)
                x_y_intersection_size = len(set_x.intersection(set_y))
                if x_y_intersection_size == 0:
                    continue
                recall = x_y_intersection_size / y_size
                precision = x_y_intersection_size / x_size
                x_y_f_score = (2 * recall * precision) / (recall + precision)
                if x_y_f_score > max_f_score:
                    max_f_score = x_y_f_score
            result.append(max_f_score)
        self.avg_f_score.append(sum(result) / len(result))

    def print_in_file(self):
        with open('f_score_output.txt', 'w') as fp:
            for i in range(len(self.file_name)):
                fp.write(str(self.file_name[i]) + " : ")
                fp.write(str(self.avg_f_score[i]))
                fp.write("\n")
        fp.close()

    def do(self):
        self.set_ground_truth()
        for file_name in self.file_name:
            self.get_cluster(file_name)
            self.append_avg_f_score(self.cluster)
        self.print_in_file()


class FBC:
    def __init__(self, filename, cutting_value, minimal_size):
        self.filename = filename
        self.raw_data = []
        self.cluster_list = []
        self.node_list = []
        self.nodes_as_integer = []
        self.adjacency_list = []
        self.depth_list = []
        self.cutting_value = cutting_value
        self.minimal_size = minimal_size

    def print_in_file(self):
        res = list(reversed(sorted(self.cluster_list, key=len)))
        with open('project_output_' + str(self.cutting_value) + '_' + str(self.minimal_size) + '.txt', 'w') as fp:
            for i in range(len(res)):
                if len(res[i]) < self.minimal_size:
                    continue
                fp.write(str(len(res[i])) + ' : ' + ' '.join(str(self.node_list[j]) for j in res[i]) + '\n')
        fp.close()

    def set_node_list(self):
        for i in range(len(self.raw_data)):
            for j in range(len(self.raw_data[i])):
                if self.raw_data[i][j] not in self.node_list:
                    self.node_list.append(self.raw_data[i][j])
        self.node_list = sorted(self.node_list)

    def set_adjacency_list(self):
        result = [[] for i in range(len(self.node_list))]
        for i in self.nodes_as_integer:
            result[i[0]].append(i[1])
            result[i[1]].append(i[0])
        self.adjacency_list = result

    def set_nodes_as_integer(self):
        self.nodes_as_integer = [[[] for i in range(len(self.raw_data[0]))] for j in range(len(self.raw_data))]
        for i in range(len(self.raw_data)):
            for j in range(len(self.raw_data[i])):
                self.nodes_as_integer[i][j] = self.node_list.index(self.raw_data[i][j])

    def bfs(self, start):
        visited = []
        q = deque([start])
        while len(q):
            curr = q.popleft()
            visited.append(curr)
            for i in self.adjacency_list[curr]:
                if i not in visited and i not in q:
                    q.append(i)
        return sorted(visited)

    def set_cluster_list(self):
        visited = []
        for i in range(len(self.node_list)):
            if i not in visited:
                cluster = self.bfs(i)
                self.cluster_list.append(cluster)
                visited = visited + cluster

    def calculate_depth(self):
        N = 1
        while 1:
            values = []
            for i in range(len(self.depth_list)):
                values.append(self.get_new_depth(self.adjacency_list[i], N))
            for j in range(len(self.depth_list)):
                self.depth_list[j] = self.depth_list[j] + values[j]
            if max(values) < 0.1:
                break
            N = N + 1

    def get_new_depth(self, adj, iters):
        return sum([self.depth_list[i] for i in adj]) / pow(iters, 2)

    def cut_edge(self):
        value = np.quantile(self.depth_list, self.cutting_value)
        candidate = [[False for i in range(len(self.adjacency_list))] for i in range(len(self.adjacency_list))]
        for i in range(len(self.adjacency_list)):
            for j in range(len(self.adjacency_list[i])):
                if self.depth_list[i] > value > self.depth_list[self.adjacency_list[i][j]]:
                    candidate[i][self.adjacency_list[i][j]] = True
                if self.depth_list[i] < value < self.depth_list[self.adjacency_list[i][j]]:
                    candidate[i][self.adjacency_list[i][j]] = True

        for i in range(len(self.adjacency_list)):
            for j in range(len(self.adjacency_list)):
                if candidate[i][j]:
                    self.adjacency_list[i].remove(j)

    def do(self):
        with open(self.filename, 'r') as file:
            for line in file:
                self.raw_data.append([i for i in line.strip().split('\t')])
        self.set_node_list()
        self.set_nodes_as_integer()
        self.set_adjacency_list()

        self.depth_list = [1 for i in range(len(self.node_list))]
        self.calculate_depth()
        self.cut_edge()

        self.set_cluster_list()
        self.print_in_file()
        self.print_for_cytoscape()

    def print_for_cytoscape(self):
        with open('depth.txt', 'w') as fp:
            fp.write(str(len(self.node_list)) + '\n')
            fp.write(' '.join(str(self.depth_list[i]) for i in range(len(self.depth_list))) + '\n')
            for i in range(len(self.adjacency_list)):
                fp.write(' '.join(str(self.adjacency_list[i][j]) for j in range(len(self.adjacency_list[i]))) + '\n')
        fp.close()


cut = [0.1, 0.25, 0.5, 0.75, 0.9]
for c in cut:
    for minimal in range(1, 2):
        fbc = FBC("assignment5_input.txt", c, minimal)
        fbc.do()

result_to_compare = ["assignment5_output.txt",
                     "assignment6_output.txt",
                     "project_output_0.1_1.txt",
                     "project_output_0.1_2.txt",
                     "project_output_0.25_1.txt",
                     "project_output_0.25_2.txt",
                     "project_output_0.5_1.txt",
                     "project_output_0.5_2.txt",
                     "project_output_0.75_1.txt",
                     "project_output_0.75_2.txt",
                     "project_output_0.9_1.txt",
                     "project_output_0.9_2.txt",
                     ]
f_score = F_SCORE(result_to_compare, "complex_merged.txt")
f_score.do()
