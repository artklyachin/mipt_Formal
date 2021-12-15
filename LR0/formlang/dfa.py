from formlang.helpers import *

# построения МДКА алгоритмом Бржозовского
class DFA:

    def __init__(self, Q, A, T, S, F):
        self.Q = list(Q)  # список id состояний
        self.A = list(A)  # строка букв алфавита
        self.T = list(T)  # матрица переходов QxA: [q1][a]->{q2}
        self.S = set(S)  # множество начальных состояний из Q (хранятся индексы из Q, а не сами id)
        self.F = set(F)  # множество конечных состояний из Q (хранятся индексы из Q, а не сами id)

    # Обращение КА
    def reverse(self):
        revT = [[set() for j in range(0, len(self.A))] for i in range(0, len(self.Q))]
        for t1 in range(0, len(self.Q)):
            for a in range(0, len(self.A)):
                for t2 in self.T[t1][a]:
                    revT[t2][a].add(t1)
        return DFA(self.Q, self.A, revT, self.F, self.S)

    def reachableSets(self, q, d, ql):
        t = []
        for a in range(0, len(self.A)):
            ts = set()
            for i in ql:
                # объединение множеств (достижимых из ql) состояний для символа a
                ts |= self.T[i][a]
            if len(ts) == 0:
                t.append(set())
                continue
            fs = frozenset(ts)
            i = d.get(fs, len(q))
            if i == len(q):
                d[fs] = i
                q.append(ts)
            t.append({i})
        return t

    # Детерминизация КА
    def determinate(self):
        dfaT = []
        d = {frozenset(self.S): 0}
        q = [self.S]
        while len(dfaT) < len(q):
            dfaT.append(self.reachableSets(q, d, q[len(dfaT)]))
        dfaF = {i for s, i in d.items() if self.F & s}
        return DFA(range(0, len(q)), self.A, dfaT, {0}, dfaF)

    # Алгоритм Бржозовского
    def minimize(self):
        return self.reverse().determinate().reverse().determinate()

    def __str__(self):
        return f'DFA(Q:{self.Q} A:{self.A} T:{self.T} S:{self.S} F:{self.F})'
