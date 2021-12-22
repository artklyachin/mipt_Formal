import pytest
from formlang import helpers

def test_Stack():
    st = helpers.Stack()
    assert st.empty() == True
    assert st.size() == 0
    st.push(1)
    assert st.empty() == False
    assert st.size() == 1
    assert st.top() == 1
    assert str(st) == "Stack(1)"
    st.pop()
    assert st.empty() == True
    assert st.size() == 0

def test_replaceInSet():
    s = {1, 2, 3}
    helpers.replaceInSet(s, 2, 4)
    assert s == {1, 3, 4}
    helpers.replaceInSet(s, 2, 5)
    assert s == {1, 3, 4}

def test_shiftedSet():
    s = {1, 2, 3}
    assert helpers.shiftedSet(s, 10) == {11, 12, 13}
