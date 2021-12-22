import pytest
from formlang import dfa

def test_nfa_methods():
    g = dfa.DFA([0, 1, 2, 3], ['a', 'b'], [[{1, 2}, {2}], [{2}, {3}], [{1, 2}, {3}], [set(), set()]], {0}, {3})
    assert str(g) == "DFA(Q:[0, 1, 2, 3] A:['a', 'b'] T:[[{1, 2}, {2}], [{2}, {3}], [{1, 2}, {3}], [set(), set()]] S:{0} F:{3})"
    assert str(g.reverse()) == "DFA(Q:[0, 1, 2, 3] A:['a', 'b'] T:[[set(), set()], [{0, 2}, set()], [{0, 1, 2}, {0}], [set(), {1, 2}]] S:{3} F:{0})"
    assert str(g.determinate()) == "DFA(Q:[0, 1, 2, 3] A:['a', 'b'] T:[[{1}, {2}], [{1}, {3}], [{1}, {3}], [set(), set()]] S:{0} F:{3})"
    assert str(g.minimize()) == "DFA(Q:[0, 1, 2] A:['a', 'b'] T:[[{1}, {1}], [{1}, {2}], [set(), set()]] S:{0} F:{2})"
    assert str(g.determinate().complete()) == "DFA(Q:[0, 1, 2, 3, 4] A:['a', 'b'] T:[[{1}, {2}], [{1}, {3}], [{1}, {3}], [{4}, {4}], [{4}, {4}]] S:{0} F:{3})"