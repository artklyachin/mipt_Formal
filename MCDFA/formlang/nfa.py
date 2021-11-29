from formlang.helpers import *
from formlang.dfa import *

class NFA:

    def __init__(self, letter):
        self._rpn = letter
        self._regexPrecedence = 0
        # _G     : list[src] = dict{letter:{set of dst nodes}}]
        # _G[0]  : start node
        # _G[-1] : terminal node
        if letter == "1":
            self._regex = ""
            self._G = [{"ε":{1}}, {}]
        else:
            self._regex = letter
            self._G = [{"ε":{1}}, {letter:{2}}, {"ε":{3}}, {}]


    def addEdges(self, letter, src, setOfDst):
        if letter not in self._G[src]:
            self._G[src][letter] = set()
        self._G[src][letter] |= setOfDst


    def addEdge(self, letter, src, dst):
        self.addEdges(letter, src, {dst})


    def merge(self, dst, src):
        ''' merge src node to dst node, src node become empty '''
        if src != dst:
            for letter in self._G[src]:
                self.addEdges(letter, dst, self._G[src][letter])
            self._G[src] = {}
            for i in range(len(self._G)):
                for it in self._G[i].values():
                    replaceInSet(it, src, dst)


    def compact(self):
        ''' compact the graph excluding empty nodes and renumbering the others '''
        dst = 0
        for src in range(len(self._G)):
            if len(self._G[src]) != 0 or src == self.finish():
                self.merge(dst, src)
                dst += 1
        while len(self._G) > dst:
            self._G.pop()


    def extend(self, other):
        ''' extend the graph with another one '''
        shift = len(self._G)
        for nodeDict in other._G:
            self._G.append({letter: shiftedSet(dstNodes, shift) for (letter, dstNodes) in nodeDict.items()})


    def iterate(self):
        ''' apply Kleene star (operation *) to the graph '''
        self._rpn = f'{self._rpn}*'
        self._regex = f'{self._regex}*' if self._regexPrecedence <= 1 else f'({self._regex})*'
        self._regexPrecedence = 1
        #
        self.merge(self.finish(), 0)
        self.addEdge("ε", 0, self.finish())
        self._G.append({})
        self.addEdge("ε", self.finish() - 1, self.finish())


    def concatenate(self, other):
        ''' concatenate (operation .) another graph to self '''
        self._rpn = f'{self._rpn}{other._rpn}.'
        self._regex = self._regex if self._regexPrecedence <= 2 else f'({self._regex})'
        self._regex += other._regex if other._regexPrecedence <= 2 else f'({other._regex})'
        self._regexPrecedence = 2
        #
        shift = len(self._G)
        self.extend(other)
        self.merge(shift - 1, shift)


    def unite(self, other):
        ''' unite (operation +) another graph to self '''
        self._rpn = f'{self._rpn}{other._rpn}+'
        self._regex = f'{self._regex}|{other._regex}'
        self._regexPrecedence = 3
        #
        shift = len(self._G)
        self.extend(other)
        self.merge(0, shift)
        self.merge(self.finish(), shift - 1)


    def condensate(self):
        ''' condensate the graph merging cycles of epsilon edges '''
        graph = []
        for nodeDict in self._G:
            graph.append(nodeDict["ε"] if "ε" in nodeDict else [])
        components = GraphCondenser(graph).condensate()
        for comp in components:
            for i in range(1, len(comp)):
                self.merge(comp[0], comp[i])
        for i in range(len(self._G)):
            if "ε" in self._G[i]:
                self._G[i]["ε"].discard(i)
                if len(self._G[i]["ε"]) == 0:
                    del self._G[i]["ε"]


    def removeEpsilonEdges(self):
        ''' remove epsilon edges, the graph should be condensated before '''
        ''' after the operation all terminal nodes are connected to the finishing node with symbol $ '''
        for i in range(len(self._G) - 1):
            while "ε" in self._G[i]:
                nodes = list(self._G[i]["ε"])
                self._G[i]["ε"] = set()
                for j in nodes:
                    if j == self.finish():
                        self._G[i]["$"] = {j}
                    else:
                        for (letter, dst) in self._G[j].items():
                            if letter not in self._G[i]:
                                self._G[i][letter] = set()
                            self._G[i][letter] |= dst
                if len(self._G[i]["ε"]) == 0:
                    del self._G[i]["ε"]


    def removeUnreachableEdges(self):
        ''' remove the parts of graph unreachable from the start node '''
        # count incoming edges for each node
        cnt = [0] * self.size()
        for nodeDict in self._G:
            for (letter, dst) in nodeDict.items():
                for i in dst:
                    cnt[i] += 1
        # candidates are non-empty nodes with zero incoming edges
        candidates = [i for i in range(1, self.size()) if cnt[i] == 0 and len(self._G[i]) != 0]
        while len(candidates) != 0:
            nextCandidates = []
            for src in candidates:
                for (letter, dst) in self._G[src].items():
                    for i in dst:
                        cnt[i] -= 1
                        if cnt[i] == 0:
                            nextCandidates.append[i]
                self._G[src] = {}
            candidates = nextCandidates


    def size(self):
        ''' return the current number of nodes '''
        return len(self._G)

    def nodeDict(self, src):
        ''' return the dictionary of edges originating from src node '''
        return self._G[src]

    def start(self):
        ''' return the starting node of graph (always 0) '''
        return 0

    def finish(self):
        ''' return the finishing node of the graph (always the last node) '''
        return len(self._G) - 1

    def numTerminals(self):
        ''' return the number of terminal nodes (leading to the finishing node with epsilon edge) '''
        return sum(1 for nodeDict in self._G if ("ε" in nodeDict and self.finish() in nodeDict["ε"]) or ("$" in nodeDict and self.finish() in nodeDict["$"]))

    def rpn(self):
        ''' return the parsed expression in reverse polish notation '''
        return self._rpn

    def regex(self):
        ''' return the parsed expression in POSIX notaion '''
        return self._regex

    def __str__(self):
        return f'NFA(rpn:{self._rpn} regex:{self._regex} rp:{self._regexPrecedence} start:{self.start()} finish:{self.finish()}, G:{self._G})'

    def createDFA(self):
        Q = [i for i in range(0, self.size() - 1)]
        A = set()
        for i in range(len(self._G) - 1):
            A |= self._G[i].keys()
        if "$" in A:
            A.remove("$")
        A = sorted(A)
        T = [[self._G[q].get(a, set()) for a in A] for q in Q]
        S = {0}
        F = {i for i in range(len(self._G)) if "$" in self._G[i]}
        return DFA(Q, A, T, S, F)
    
def parseRPN(regex):
    ''' build NFA by regex in "reverse polish notantion". '''
    if len(regex) == 0:
        raise ValueError('empty language')

    st = Stack()

    for letter in regex:
        if letter in '1abc':
            st.push(NFA(letter))

        elif letter == '.':
            if st.size() < 2:
                raise ValueError(f'two arguments required for concatenation')
            arg = st.top()
            st.pop()
            st.top().concatenate(arg)

        elif letter == '+':
            if st.size() < 2:
                raise ValueError(f'two arguments required for union')
            arg = st.top()
            st.pop()
            st.top().unite(arg)

        elif letter == '*':
            if st.empty():
                raise ValueError('an argument required for iteration')
            st.top().iterate()

        else:
            raise ValueError(f'letter "{letter}" is not from language alphabet')

    if st.size() != 1:
        raise ValueError(f'stack contains more that one element: {st.size()}')

    return st.top()
