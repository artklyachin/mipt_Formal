import pytest
from formlang import nfa

def test_parseRPN():
    tests = [
        ('1', '', 2, 1, 1),
        ('1*', '*', 2, 1, 1),
        ('11.', '', 2, 1, 1),
        ('a', 'a', 3, 1, 1),
        ('a1.', 'a', 3, 1, 1),
        ('a1*.', 'a*', 3, 1, 1),
        ('a*', 'a*', 3, 2, 2),
        ('a*1+', 'a*|', 3, 2, 2),
        ('a*1.', 'a*', 3, 2, 2),
        ('a**', 'a**', 3, 2, 2),
        ('ab+', 'a|b', 4, 2, 2),
        ('ab+a+', 'a|b|a', 5, 2, 3),
        ('abc++', 'a|b|c', 5, 3, 3),
        ('ab+*', '(a|b)*', 4, 3, 3),
        ('a*b*+', 'a*|b*', 4, 3, 3),
        ('aa.', 'aa', 4, 1, 1),
        ('abc..', 'abc', 5, 1, 1),
        ('ab.cb.+', 'ab|cb', 6, 2, 2),
        ('a*b*.', 'a*b*', 4, 3, 3),
        ('a*a*.', 'a*a*', 4, 2, 3),
        ('ab+c.aba.*.bac.+.+*', '((a|b)c|a(ba)*(b|ac))*', 11, 3, 4),
        ('acb..bab.c.*.ab.ba.+.+*a.', '(acb|b(abc)*(ab|ba))*a', 14, 2, 1),        
    ]
    for test in tests:
        g = nfa.parseRPN(test[0])
        assert g.rpn() == test[0], f'Error in {test}'
        assert g.regex() == test[1], f'Error in {test}'
        g.condensate()
        g.removeEpsilonEdges()
        g.removeUnreachableEdges()
        g.compact()
        assert g.size() == test[2], f'Error in {test}'
        assert len(g.nodeDict(g.start()).keys()) == test[3], f'Error in {test}'
        assert g.numTerminals() == test[4], f'Error in {test}'
        
def test_parseRPN_errors():
    tests = [
        ('', ValueError, 'empty language'),
        ('a.', ValueError, 'two arguments required for concatenation'),
        ('a+', ValueError, 'two arguments required for union'),
        ('*a.', ValueError, 'an argument required for iteration'),
        ('ad.', ValueError, 'letter "d" is not from language alphabet'),
        ('aa', ValueError, 'stack contains more that one element: 2'),
    ]
    for test in tests:
        with pytest.raises(test[1], match=test[2]):
            nfa.parseRPN(test[0])

def test_nfa_methods():
    g = nfa.parseRPN("a")
    assert g.size() == 4
    assert g.nodeDict(1) == {"a":{2}}
    assert g.start() == 0
    assert g.finish() == 3
    assert g.numTerminals() == 1
    assert g.rpn() == "a"
    assert g.regex() == "a"
    assert str(g) == "NFA(rpn:a regex:a rp:0 start:0 finish:3, G:[{'ε': {1}}, {'a': {2}}, {'ε': {3}}, {}])"
    assert str(g.createDFA()) == "DFA(Q:[0, 1, 2] A:['a', 'ε'] T:[[set(), {1}], [{2}, set()], [set(), {3}]] S:{0} F:set())"
