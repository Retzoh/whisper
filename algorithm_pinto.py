# Algorithms used for rumor source inference in a graph
# - Pinto algorithm

import networkx as nx
from numpy import matrix, array
from numpy import linalg
import math

#####################################################################
# ATRIBUTES OF THE NODE:
#
# name: i = node number i (0 < i < n)
#
# informed: 0 = ignorant
#           1 = informed/infected
#
# observer: 0 = non observer
#           i = observer number i (0 < i < k)
#
# path: i = number of edges between the node and the
# supposed source (SEE IF USEFULL)
#
# time: t = time when the observer receives the information
#
# bfs: auxiliar boolean to construct the bfs tree
#
# children: children nodes for the bfs tree
#
# Example: G.add_node(1,informed=0,observer=0,path=0,time=0)
#####################################################################

class Node(object):
    def __init__(self):
        self.name = ""
        self.informed = 0
        self.observer = 0
        self.path = 0
        self.time = 0
        self.bfs = False
        self.children = []


# O is a vector with the observer nodes
# propagation delays are RVs with Gaussian distribution N(mi,sigma2)
class AlgorithmPinto:
    def __init__(self):
        pass

    def Algorithm(self, G, O, mi, sigma2):
        d = self.observed_delay(G, O)
        first_node = O[0]
        # calculates F for the first node: fulfills max
        MAX = self.main_function(first_node, O, d, nx.bfs_tree(G, source=first_node), mi, sigma2)
        source = first_node  # SEE HOW WE CAN DO IT
        # calculates the maximum F
        for s in G:
            T = nx.bfs_tree(G, source=s)
            F = self.main_function(s, d, T, mi)
            if F > MAX:
                MAX = F
                source = s
        return source

    # MAIN_FUNCTION S to be calculated
    def main_function(self, s, O, d, T, mi, sigma2):
        mi_s = self.deterministic_delay(T, s, O, mi)
        delta = self.delay_covariance(T, O, sigma2)
        return mi_s.T * delta.I * (d - (0.5 * mi_s))

    # calculates array d (observed delay)
    @staticmethod
    def observed_delay(g, O):
        d = {}
        for i in range(0, len(O) - 1):
            d[i] = g.node[O[i + 1]]['time'] - g.node[O[i]]['time']
        return d

    # calculates array mi_s (deterministic delay)
    def deterministic_delay(self, T, s, O, mi):
        constant = self.height_node(T, s, O[0])
        mi_s = array([0 for i in range(len(O)-1)])
        for i in range(len(O)-1):
            mi_s[i] = self.height_node(T, s, O[i + 1]) - constant
        mi_s = mi * mi_s
        return mi_s

    # calculates the height of a node in the tree T (recursive)
    def height_node(self, T, s, node):
        l = list(nx.all_simple_paths(T, s, node))
        if l == []:
            return 0
        else:
            return len(l[0]) - 1

    # calculates the array delta (delay covariance)
    # FIXME here
    def delay_covariance(self, T, O, sigma2):
        n = len(O)
        delta = matrix([[0 for i in range(n)] for j in range(n)])
        for k in range(len(O)-1):
            for i in range(len(O)-1):
                if i == k:
                    delta[k][i] = self.height_node(T, O[0], O[k + 1])
                else:
                    delta[k][i] = math.fabs(self.height_node(T, O[0], O[k + 1]) - self.height_node(T, O[0], O[i + 1]))
        delta = delta * (sigma2 ** 2)
        return delta
