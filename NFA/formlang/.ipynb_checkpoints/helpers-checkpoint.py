class Stack:
    def __init__(self):
        self.lst = []

    def empty(self):
        return len(self.lst) == 0

    def push(self, item):
        self.lst.append(item)

    def pop(self):
        return self.lst.pop()

    def size(self):
        return len(self.lst)

    def top(self):
        return self.lst[-1]

    def __str__(self):
        print(self.lst)
        return 'Stack(' + ','.join([str(v) for v in self.lst]) + ')'


class GraphCondenser:
    def __init__(self, G):
        N = len(G)
        self._G = G
        self._R = [[] for i in range(N)]
        for i in range(N):
            for node in G[i]:
                self._R[node].append(i)

    def dfs1(self, v):
        self._used[v] = True
        for u in self._G[v]:
            if not self._used[u]:
                self.dfs1(u)
        self._order.append(v)

    def dfs2(self, v):
        self._used[v] = True
        self._component.append(v)
        for u in self._R[v]:
            if not self._used[u]:
                self.dfs2(u)

    def condensate(self):
        N = len(self._G)
        self._used = [False] * N
        self._order = []
        for v in range(N):
            if not self._used[v]:
                self.dfs1(v)
        result = []
        self._component = []
        self._used = [False] * N
        for v in self._order[::-1]:
            if not self._used[v]:
                self.dfs2(v)
                result.append(self._component)
                self._component = []
        return result


def replaceInSet(s, old, new):
    if old in s:
        s.remove(old)
        s.add(new)


def shiftedSet(s, shift):
    return set(map(lambda x: x + shift, s))
