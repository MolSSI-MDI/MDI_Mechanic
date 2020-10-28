import os
import pickle
from graphviz import Digraph

def make_graph( base_path ):
    # Read the data required to make the graph
    graph_file = os.path.join( base_path, "MDI_Mechanic", ".temp", "graph.pickle")
    with open(graph_file, 'rb') as handle:
        data = pickle.load(handle)
    nodes = data['nodes']
    edges = data['edges']

    dot = Digraph(comment='Node Report', format='svg')

    node_list = []
    for node in nodes.keys():
        node_list.append( node )
    ordered_nodes = sorted( node_list )
    
    for node in ordered_nodes:
        dot.node( node, nodes[ node ], shape='box', margin='0.1' )

    for edge in edges:
        dot.edge( edge[0], edge[1] )

    graph_path = os.path.join( base_path, "report", "graphs", "node-report.gv" )
    dot.render( graph_path )

if __name__ == "__main__":
    make_graph()
