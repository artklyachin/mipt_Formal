import pytest
from formlang import prefix


def test_PrefixChecker():
    tests = [
        ("ab+c.aba.*.bac.+.+*", "a", 2, "YES"),
        ("acb..bab.c.*.ab.ba.+.+*a.", "b", 3, "NO"),
        ("a", "b", "NO"),
        ("a", "", "YES"),
        ("a", "a", "YES"),
        ("a", "aa", "NO"),
        ("aa.", "b", "NO"),
        ("aa.", "", "YES"),
        ("aa.", "a", "YES"),
        ("aa.", "aa", "YES"),
        ("aa.", "aaa", "NO"),
        ("aaa..", "aa", "YES"),
        ("aaa..", "aaa", "YES"),
        ("aaa..", "aaaa", "NO"),
        ("ba.", "ab", "NO"),
        ("ba.", "baa", "NO"),
        ("aa.b*+", "aa", "YES"),
        ("aa.b*+", "aaa", "NO"),
        ("aa.b*+", "ab", "NO"),
        ("aa*.", "", "YES"),
        ("aa*.", "a", "YES"),
        ("aa*.", "aa", "YES"),
        ("aa*.", "aaaaaa", "YES"),
        ("cba++*", "abcaabcbbacccb", "YES"),
        ("a*b*.", "aba", "NO"),
        ("a*b*.", "ba", "NO"),
        ("a*b*.", "aaa", "YES"),
        ("a*b*.", "bbb", "YES"),
        ("a*b*.", "c", "NO")
    ]
    for test in tests:
        if (len(test) == 4):
            assert test[3] == prefix.PrefixChecker(test[0]).check(test[1] * test[2]), test
        else:
            assert test[2] == prefix.PrefixChecker(test[0]).check(test[1]), test
        