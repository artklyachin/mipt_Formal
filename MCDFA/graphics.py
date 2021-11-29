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
        G.add_node(_nfa.finish(), shape = 'doublecircle')
    G.get_node(_nfa.start()).attr['style'] = 'filled'
    for i in range(_nfa.size()):
        for (letter, dst) in _nfa.nodeDict(i).items():
            for j in dst:
                if j == _nfa.finish() and not withFinish:
                    G.get_node(i).attr['shape'] = 'doublecircle'
                else:
                    G.add_edge(i, j, label = letter)

    return G.string()

def nfaCreateImage(_nfa, withFinish=True):
    return pdp.graph_from_dot_data(nfaGraphVizString(_nfa, withFinish)).create_png()

def dfaGraphVizString(_dfa, _label):
    G = pgv.AGraph(strict=False, directed=True)
    G.graph_attr['label'] = _label
    G.node_attr['shape'] = 'circle'
    G.edge_attr['color'] = 'red'
    for i in range(len(_dfa.Q)):
        G.add_node(i, label = str(_dfa.Q[i]), shape = ('doublecircle' if i in _dfa.F else 'circle'))
        if i in _dfa.S:
            G.get_node(i).attr['style'] = 'filled'
        if i in _dfa.F:
            G.get_node(i).attr['shape'] = 'doublecircle'
    for q1 in range(len(_dfa.Q)):
        for a in range(len(_dfa.A)):
            for q2 in (_dfa.T[q1][a]):
                G.add_edge(q1, q2, label = _dfa.A[a])
    return G.string()

def dfaCreateImage(_dfa, _label = ''):
    return pdp.graph_from_dot_data(dfaGraphVizString(_dfa, _label)).create_png()
