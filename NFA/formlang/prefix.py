from formlang import nfa


class PrefixChecker:
    
    def __init__(self, rpn):
        self._nfa = nfa.parseRPN(rpn)
        self._nfa.condensate()
        self._nfa.removeEpsilonEdges()
        self._nfa.removeUnreachableEdges()
        self._nfa.compact()
        
    def check(self, word):
        top = self._nfa.start()
        prefix = self.dfs(word, top) 
        return "YES" if prefix == len(word) else "NO"
        
    def dfs(self, word, top):
        if len(word) == 0:
            return 0
        
        maxprefix = 0
        letter = word[0]
        if letter in self._nfa.nodeDict(top):
            for nexttop in self._nfa.nodeDict(top)[letter]:
                prefix = 1 + self.dfs(word[1:], nexttop)
                maxprefix = max(maxprefix, prefix)
        return maxprefix