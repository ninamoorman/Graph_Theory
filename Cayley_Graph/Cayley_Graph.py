# import networkx as nx
# import matplotlib.pyplot as plt
import random
from igraph import *

def group_operation(a, b): # make this generalized (input)
    # Z3xZ3
    # ind_0 = (a[0] + b[0]) % 3
    # ind_1 = (a[1] + b[1]) % 3
    # return (ind_0, ind_1)

    # 5Z
    return (a+b)%5

def cayley_condition(u, v, S):
    for s in S:
        if u == group_operation(s, v):
            return True
    return False

def cayley_sum_condition(u, v, S):
    for s in S:
        if s == group_operation(u, v):
            return True
    return False

def Cayley_Graph(V, S, group_name):
    labels = dict()
    E_Cayley = set()
    E_Cayley_Sum = set()
    for u in V:
        for v in V:
            if cayley_condition(u, v, S):
                if (u, v) not in E_Cayley and (v, u) not in E_Cayley:
                    E_Cayley.add((u, v))
            if cayley_sum_condition(u, v, S):
                if (u, v) not in E_Cayley_Sum and (v, u) not in E_Cayley_Sum:
                    E_Cayley_Sum.add((u, v))
        labels[u] = u

    show_graph(V, E_Cayley, "", group_name, S, labels) # C
    show_graph(V, E_Cayley_Sum, "Sum ", group_name, S, labels) # C sum

def Cayley_Sum_Graph(G, S):
    pass

def show_graph_old(V, E, graph_type, group_name, S, labels):
    G = nx.Graph()
    G.add_edges_from(E)
    pos = nx.spring_layout(G)

    # Generate a dict of positions
    # pos = {i: (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) for i in V}

    # nodes
    nx.draw_networkx_nodes(G,pos,
                        nodelist=V,
                        node_color='r',
                        node_size=50,
                    alpha=0.8)

    # edges
    nx.draw_networkx_edges(G,pos,
                        edgelist=E,
                        width=2,alpha=0.5,edge_color='r')

    nx.draw_networkx_labels(G,pos,labels,font_size=16)

    plt.axis('off')
    plt.title("Cayley {2}Graph of {0} given S = {1}".format(group_name, S, graph_type))
    plt.savefig("Plots/Cayley {2}Graph of {0} given S = {1}".format(group_name, S, graph_type))
    plt.show()

def show_graph(V, E, graph_type, group_name, S, labels):
    g = Graph()
    g.add_vertices(V)
    g.add_edges(E)
    layout = g.layout("kk") # random_3d
    plot(g, layout = layout)

    # plt.axis('off')
    # plt.title("Cayley {2}Graph of {0} given S = {1}".format(group_name, S, graph_type))
    # plt.savefig("Plots/Cayley {2}Graph of {0} given S = {1}".format(group_name, S, graph_type))
    # plt.show()

def main(G, S, group_name):
    # print(G)
    # print(S)
    Cayley_Graph(G, S, group_name)
    Cayley_Sum_Graph(G, S)

if __name__ == "__main__":

    # Z3xZ3
    # G = []
    # for i in range(3):
    #     for j in range(3):
    #         G.append((i, j))
    # S = [(0, 1), (1, 0), (0, 2), (2, 0)]

    # 5Z
    G = range(5)
    S = {1, 4}

    main(G, S, "Z3xZ3")