import pygraphviz as pgv
import pydotplus as pdp

class Grammar:
    def __init__(self, grammar):
        self.grammar = grammar
        self.start = next(iter(grammar))
        self.nonterminals = set(grammar.keys())
        self.terminals = set()

        for head, bodies in grammar.items():
            for body in bodies:
                if '$' in body:
                    raise ValueError(f"{head} -> {body}: Специальный символ '$' не может присутствовать в правиле")

                for symbol in body:
                    if symbol not in self.nonterminals:
                        self.terminals.add(symbol)

        self.symbols = self.terminals | self.nonterminals
        
        
def first_follow(G):
    def union(set_1, set_2):
        set_1_len = len(set_1)
        set_1 |= set_2

        return set_1_len != len(set_1)

    first = {symbol: set() for symbol in G.symbols}
    first.update((terminal, {terminal}) for terminal in G.terminals)
    follow = {symbol: set() for symbol in G.nonterminals}
    follow[G.start].add('$')

    while True:
        updated = False

        for head, bodies in G.grammar.items():
            for body in bodies:
                for symbol in body:
                    if symbol != 'ε':
                        updated |= union(first[head], first[symbol] - set('ε'))

                        if 'ε' not in first[symbol]:
                            break
                    else:
                        updated |= union(first[head], set('ε'))
                else:
                    updated |= union(first[head], set('ε'))

                aux = follow[head]
                for symbol in reversed(body):
                    if symbol == 'ε':
                        continue
                    if symbol in follow:
                        updated |= union(follow[symbol], aux - set('ε'))
                    if 'ε' in first[symbol]:
                        aux = aux | first[symbol]
                    else:
                        aux = first[symbol]

        if not updated:
            return first, follow


class SLRParser:
    def __init__(self, grammar):
        start = next(iter(grammar))
        grammar_prime = {start + "'": {(start,)}}
        grammar_prime.update(grammar)
        self.G_prime = Grammar(grammar_prime)
        self.max_G_prime_len = len(max(self.G_prime.grammar, key=len))
        self.G_indexed = []

        for head, bodies in self.G_prime.grammar.items():
            for body in bodies:
                self.G_indexed.append([head, body])

        self.first, self.follow = first_follow(self.G_prime)
        self.C = self.items(self.G_prime)
        self.action = list(self.G_prime.terminals) + ['$']
        self.goto = list(self.G_prime.nonterminals - {self.G_prime.start})
        self.parse_table_symbols = self.action + self.goto
        self.parse_table = self.construct_table()

    def CLOSURE(self, I):
        J = I

        while True:
            item_len = len(J)

            for head, bodies in J.copy().items():
                for body in bodies.copy():
                    if '•' in body[:-1]:
                        symbol_after_dot = body[body.index('•') + 1]

                        if symbol_after_dot in self.G_prime.nonterminals:
                            for G_body in self.G_prime.grammar[symbol_after_dot]:
                                J.setdefault(symbol_after_dot, set()).add(
                                    ('•',) if G_body == ('ε',) else ('•',) + G_body)

            if item_len == len(J):
                return J

    def GOTO(self, I, X):
        goto = {}

        for head, bodies in I.items():
            for body in bodies:
                if '•' in body[:-1]:
                    dot_pos = body.index('•')

                    if body[dot_pos + 1] == X:
                        replaced_dot_body = body[:dot_pos] + (X, '•') + body[dot_pos + 2:]

                        for C_head, C_bodies in self.CLOSURE({head: {replaced_dot_body}}).items():
                            goto.setdefault(C_head, set()).update(C_bodies)

        return goto

    def items(self, G_prime):
        C = [self.CLOSURE({G_prime.start: {('•', G_prime.start[:-1])}})]

        while True:
            item_len = len(C)

            for I in C.copy():
                for X in G_prime.symbols:
                    goto = self.GOTO(I, X)

                    if goto and goto not in C:
                        C.append(goto)

            if item_len == len(C):
                return C

    def construct_table(self):
        parse_table = {r: {c: '' for c in self.parse_table_symbols} for r in range(len(self.C))}

        for i, I in enumerate(self.C):
            for head, bodies in I.items():
                for body in bodies:
                    if '•' in body[:-1]:  # CASE 2 a
                        symbol_after_dot = body[body.index('•') + 1]

                        if symbol_after_dot in self.G_prime.terminals:
                            s = f's{self.C.index(self.GOTO(I, symbol_after_dot))}'

                            if s not in parse_table[i][symbol_after_dot]:
                                if 'r' in parse_table[i][symbol_after_dot]:
                                    parse_table[i][symbol_after_dot] += '/'

                                parse_table[i][symbol_after_dot] += s

                    elif body[-1] == '•' and head != self.G_prime.start:  # CASE 2 b
                        for j, (G_head, G_body) in enumerate(self.G_indexed):
                            if G_head == head and (G_body == body[:-1] or G_body == ('ε',) and body == ('•',)):
                                for f in self.follow[head]:
                                    if parse_table[i][f]:
                                        parse_table[i][f] += '/'

                                    parse_table[i][f] += f'r{j}'

                                break

                    else:  # CASE 2 c
                        parse_table[i]['$'] = 'acc'

            for A in self.G_prime.nonterminals:  # CASE 3
                j = self.GOTO(I, A)

                if j in self.C:
                    parse_table[i][A] = self.C.index(j)

        return parse_table

    def print_grammar(self):
        for i, (head, body) in enumerate(self.G_indexed):
            print(f'{i:>{len(str(len(self.G_indexed) - 1))}}: {head:>{self.max_G_prime_len}} -> {" ".join(body)}')

    def print_first(self):
        for head in self.G_prime.grammar:
            print(f'{head:>{self.max_G_prime_len}} = {{ {", ".join(self.first[head])} }}')

    def print_follow(self):
        for head in self.G_prime.grammar:
            print(f'{head:>{self.max_G_prime_len}} = {{ {", ".join(self.follow[head])} }}')

    def print_parse_table(self):
        def fprint(text, variable):
            print(f'{text:>12}: {", ".join(variable)}')

        def symbols_width(symbols):
            return (width + 1) * len(symbols) - 1

        width = max(len(c) for c in {'СОСТОЯНИE'} | self.G_prime.symbols) + 2
        for r in range(len(self.C)):
            max_len = max(len(str(c)) for c in self.parse_table[r].values())

            if width < max_len + 2:
                width = max_len + 2

        print(f'┌{"─" * width}┬{"─" * symbols_width(self.action)}┬{"─" * symbols_width(self.goto)}┐')
        print(f'│{"":{width}}│{"ACTION":^{symbols_width(self.action)}}│{"GOTO":^{symbols_width(self.goto)}}│')
        print(f'│{"СОСТОЯНИE":^{width}}├{("─" * width + "┬") * (len(self.parse_table_symbols) - 1) + ("─" * width + "┤")}')
        print(f'│{"":^{width}}│', end=' ')

        for symbol in self.parse_table_symbols:
            print(f'{symbol:^{width - 1}}│', end=' ')

        print()
        print(f'├{("─" * width + "┼") * (len(self.G_prime.symbols)) + ("─" * width + "┤")}')

        for r in range(len(self.C)):
            print(f'│{r:^{width}}│', end=' ')

            for c in self.parse_table_symbols:
                print(f'{self.parse_table[r][c]:^{width - 1}}│', end=' ')

            print()

        print(f'└{("─" * width + "┴") * (len(self.G_prime.symbols)) + ("─" * width + "┘")}')
        print()

    def generate_automaton(self):
        automaton = pgv.AGraph(strict=False, directed=True)
        automaton.graph_attr['label'] = 'LR (0)-автомат для грамматики выражений'
        automaton.node_attr['shape'] = 'record'

        for i, I in enumerate(self.C):
            I_html = f'<<I>I</I><SUB>{i}</SUB><BR/>'

            for head, bodies in I.items():
                for body in bodies:
                    I_html += f'<I>{head:>{self.max_G_prime_len}}</I> &#8594;'

                    for symbol in body:
                        if symbol in self.G_prime.nonterminals:
                            I_html += f' <I>{symbol}</I>'
                        elif symbol in self.G_prime.terminals:
                            I_html += f' <B>{symbol}</B>'
                        else:
                            I_html += f' {symbol}'

                    I_html += '<BR ALIGN="LEFT"/>'

            automaton.add_node(f'I{i}', label=f'{I_html}>')

        for r in range(len(self.C)):
            for c in self.parse_table_symbols:
                if isinstance(self.parse_table[r][c], int):
                    automaton.add_edge(f'I{r}', f'I{self.parse_table[r][c]}', label=f'<<I>{c}</I>>')

                elif 's' in self.parse_table[r][c]:
                    i = self.parse_table[r][c][self.parse_table[r][c].index('s') + 1:]

                    if '/' in i:
                        i = i[:i.index('/')]

                    automaton.add_edge(f'I{r}', f'I{i}', label=f'<<B>{c}</B>>' if c in self.G_prime.terminals else c)

                elif self.parse_table[r][c] == 'acc':
                    automaton.add_node('acc', label='<<B>Принятие</B>>', shape='none')
                    automaton.add_edge(f'I{r}', 'acc', label='$')

        return pdp.graph_from_dot_data(automaton.string()).create_png()

    def LR_parser(self, w):
        buffer = f'{w} $'.split()
        pointer = 0
        a = buffer[pointer]
        stack = ['0']
        symbols = ['']
        results = {'step': [''], 'stack': ['Стек'] + stack, 'symbols': ['Символы'] + symbols, 'input': ['Вход'],
                   'action': ['Действие']}

        step = 0
        while True:
            s = int(stack[-1])
            step += 1
            results['step'].append(f'({step})')
            results['input'].append(' '.join(buffer[pointer:]))

            if a not in self.parse_table[s]:
                results['action'].append(f'Ошибка: нераспознанный символ {a}')
                break
            elif not self.parse_table[s][a]:
                results['action'].append('Ошибка: входная строка не может быть распознана')
                break
            elif '/' in self.parse_table[s][a]:
                action = 'свертка' if self.parse_table[s][a].count('r') > 1 else 'перенос'
                results['action'].append(f'Ошибка: {action}/свертка конфликт в ситуации {s}, на символе {a}')
                break
            elif self.parse_table[s][a].startswith('s'):
                results['action'].append('shift')
                stack.append(self.parse_table[s][a][1:])
                symbols.append(a)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))
                pointer += 1
                a = buffer[pointer]
            elif self.parse_table[s][a].startswith('r'):
                head, body = self.G_indexed[int(self.parse_table[s][a][1:])]
                results['action'].append(f'reduce by {head} -> {" ".join(body)}')

                if body != ('ε',):
                    stack = stack[:-len(body)]
                    symbols = symbols[:-len(body)]

                stack.append(str(self.parse_table[int(stack[-1])][head]))
                symbols.append(head)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))

            elif self.parse_table[s][a] == 'acc':
                results['action'].append('accept')

                break

        return results

    def print_LR_parser(self, results):
        max_lens = {key: max(len(value) for value in results[key]) for key in results}
        justs = {'step': '>', 'stack': '', 'symbols': '', 'input': '>', 'action': ''}

        line = f'┌{"".join([("─" * (max_len + 2) + "┬") for max_len in max_lens.values()])}'
        print(line[:-1]+'┐')
        print(''.join(
            [f'│ {history[0]:^{max_len}} ' for history, max_len in zip(results.values(), max_lens.values())]) + '│')
        line = f'├{"".join([("─" * (max_len + 2) + "┼") for max_len in max_lens.values()])}'
        print(line[:-1]+'┤')
        for i, step in enumerate(results['step'][:-1], 1):
            print(''.join([f'│ {history[i]:{just}{max_len}} ' for history, just, max_len in
                           zip(results.values(), justs.values(), max_lens.values())]) + '│')
        line = f'└{"".join([("─" * (max_len + 2) + "┴") for max_len in max_lens.values()])}'
        print(line[:-1]+'┘')
