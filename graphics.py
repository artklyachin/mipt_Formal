import pygraphviz as pgv
import pydotplus as pdp
from formlang import nfa

def nfaGraphVizString(_nfa, withFinish=True):
    G = pgv.AGraph(strict=False, directed=True)
    G.graph_attr['label'] = _nfa.rpn()
    G.node_attr['shape'] = 'circle'
    G.edge_attr['color'] = 'red'
    for i in range(_nfa.size()):
        if len(_nfa.nodeDict(i)) != 0:
            G.add_node(i)
    if withFinish:
        G.add_node(_nfa.finish(), style = 'filled')
    G.get_node(_nfa.start()).attr['shape'] = 'doublecircle'
    for i in range(_nfa.size()):
        for (letter, dst) in _nfa.nodeDict(i).items():
            for j in dst:
                if j == _nfa.finish() and not withFinish:
                    G.get_node(i).attr['style'] = 'filled'
                else:
                    G.add_edge(i, j, label = letter)

    return G.string()

def nfaCreateImage(_nfa, withFinish=True):
    return pdp.graph_from_dot_data(nfaGraphVizString(_nfa, withFinish)).create_png()
