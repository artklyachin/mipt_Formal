import itertools

# Класс, описывающий ситуацию (правило с точкой Эрли
class State:
    def __init__(self, name, expr, dot_index, start_column, end_column=None):
        self.name = name
        self.expr = expr
        self.dot_index = dot_index
        self.start_column = start_column
        self.end_column = None

    # Точка в конце выражения?
    def is_finished(self):
        return self.dot_index >= len(self.expr)

    # Прочитать токен за точкой
    def next_token(self):
        return self.expr[self.dot_index] if self.dot_index < len(self.expr) else None

    def advance(self):
        return State(self.name, self.expr, self.dot_index + 1, self.start_column)

    def __repr__(self):
        terms = [str(p) for p in self.expr]
        terms.insert(self.dot_index, "•")
        return f"{self.name} -> {' '.join(terms)} ({self.start_column.index}, {-1 if self.end_column is None else self.end_column.index})"

    # Вспомогательный картеж для __hash__ и __eq__
    def _tuple(self):
        return (self.name, self.expr, self.dot_index, self.start_column.index)

    def __hash__(self):
        return hash(self._tuple())

    def __eq__(self, other):
        return self._tuple() == other._tuple()


# Класс, описывающий список ситуаций
class Column:
    def __init__(self, index, token):
        self.index =  index
        self.token = token
        self.states = []
        self._unique = {}

    def add(self, state):
        if state in self._unique:
            return self._unique[state]
        self._unique[state] = state
        self.states.append(state)
        state.end_column = self
        return self._unique[state]
    
    def __repr__(self):
        return f"\n  {repr(self.token)}: chart[{self.index}]\n" + "\n".join("    " + str(state) for state in self.states)


# Функция проверки на нетерминал
def is_nt(k, grammar):
    return k in grammar


# Функция поиска ε-порождающих етерминалов
def nullable(g):
    nullable_keys = {k for k in g if [] in g[k]}

    unprocessed = list(nullable_keys)

    g_cur = {}
    for k in g:
        alts = []
        for alt in g[k]:
            ts = [t for t in alt if not is_nt(t, g)]
            if not ts:
                alts.append(alt)
        if alts:
            g_cur[k] = alts
            
    while unprocessed:
        nxt, *unprocessed = unprocessed
        g_nxt = {}
        for k in g_cur:
            g_alts = []
            for alt in g_cur[k]:
                alt_ = [t for t in alt if t != nxt]
                if not alt_:
                    nullable_keys.add(k)
                    unprocessed.append(k)
                    break
                else:
                    g_alts.append(alt_)
            if g_alts:
                g_nxt[k] = g_alts
        g_cur = g_nxt

    return nullable_keys


# Собственно сам парсер
class EarleyParser:
    def __init__(self, grammar):
        self._grammar = grammar
        self.epsilon = nullable(grammar)
        
    def chart_parse(self, tokens, start, alts):
        chart = [Column(i, tok) for i, tok in enumerate([None, *tokens])]
        for alt in alts:
            chart[0].add(State(start, tuple(alt), 0, chart[0]))
        return self.fill_chart(chart)

    def predict(self, col, sym, state):
        for alt in self._grammar[sym]:
            col.add(State(sym, tuple(alt), 0, col))
        if sym in self.epsilon:
            col.add(state.advance())

    def scan(self, col, state, token):
        if token == col.token:
            col.add(state.advance())

    def complete(self, col, state):
        parent_states = [st for st in state.start_column.states if st.next_token() == state.name]
        for st in parent_states:
            col.add(st.advance())

    def fill_chart(self, chart):
        for i, col in enumerate(chart):
            for state in col.states:
                if state.is_finished():
                    self.complete(col, state)
                else:
                    sym = state.next_token()
                    if sym in self._grammar:
                        self.predict(col, sym, state)
                    elif i + 1 < len(chart):
                        self.scan(chart[i + 1], state, sym)
        return chart

    def parse_prefix(self, text, start_symbol):
        alts = [tuple(alt) for alt in self._grammar[start_symbol]]
        self.table = self.chart_parse(text, start_symbol, alts)
        for col in reversed(self.table):
            states = [st for st in col.states
                      if st.name == start_symbol and st.expr in alts and st.start_column.index == 0
                      ]
            if states:
                return col.index, states
        return -1, []
    
    def recognize(self, text, start_symbol = None):
        if start_symbol is None:
            start_symbol = next(iter(self._grammar))
        cursor, states = self.parse_prefix(text, start_symbol)
        starts = [s for s in states if s.is_finished()]

        if cursor < len(text) or not starts:
            raise SyntaxError("at " + repr(text[cursor:]))
        return starts
    
    def get_table(self):
        return self.table

    def one_parse_tree(self, text, start_symbol = None):
        starts = self.recognize(text, start_symbol)
        forest = self.parse_forest(self.table, starts)
        for tree in self.extract_trees(forest):
            yield tree

    def all_parse_trees(self, text, start_symbol = None):
        starts = self.recognize(text, start_symbol)
        forest = self.parse_forest(self.table, starts)
        for tree in self.extract_all_trees(forest):
            yield tree

    def parse_paths(self, named_expr, chart, frm, til):
        def paths(state, start, k, e):
            if not e:
                return [[(state, k)]] if start == frm else []
            else:
                return [[(state, k)] + r
                        for r in self.parse_paths(e, chart, frm, start)]

        *expr, var = named_expr
        starts = None
        if var not in self._grammar:
            starts = ([(var, til - len(var),
                        't')] if til > 0 and chart[til].token == var else [])
        else:
            starts = [(s, s.start_column.index, 'n') for s in chart[til].states
                      if s.is_finished() and s.name == var]

        return [p for s, start, k in starts for p in paths(s, start, k, expr)]

    def forest(self, s, kind, chart):
        return self.parse_forest(chart, [s]) if kind == 'n' else (s, [])

    def _parse_forest(self, chart, state):
        pathexprs = self.parse_paths(state.expr, chart, state.start_column.index,
                                     state.end_column.index) if state.expr else []
        return (state.name, [[(v, k, chart) for v, k in reversed(pathexpr)]
                             for pathexpr in pathexprs])

    def parse_forest(self, chart, states):
        names = list({s.name for s in states})
        assert len(names) == 1
        forest = [self._parse_forest(chart, state) for state in states]
        return (names[0], [e for name, expr in forest for e in expr])

    def extract_a_tree(self, forest_node):
        name, paths = forest_node
        if not paths:
            return (name, [])
        return (name, [self.extract_a_tree(self.forest(*p)) for p in paths[0]])

    def extract_trees(self, forest):
        yield self.extract_a_tree(forest)
        
    def extract_all_trees(self, forest_node):
        name, paths = forest_node
        if not paths:
            yield (name, [])
        results = []
        for path in paths:
            ptrees = [self.extract_all_trees(self.forest(*p)) for p in path]
            for p in itertools.product(*ptrees):
                yield (name, p)


# функции для красивого вывода деревьев
def display_tree(node):
    print(format_node(node))
    for line in format_tree(node):
        print(line)

# терминальные токены выводим в кавычках
def format_node(node):
    return node[0] if node[1] else repr(node[0])

def format_tree(node, prefix=''):
    children = node[1]
    if not node[1]:
        return
    #*children, last_child = children
    for child in node[1][:-1]:
        yield from format_child(child, prefix + '│   ', prefix, False)
    yield from format_child(node[1][-1], prefix + '    ', prefix, True)

def format_child(child, next_prefix, prefix, last):
    yield prefix + ('└─ ' if last else '├─ ') + format_node(child)
    yield from format_tree(child, next_prefix)