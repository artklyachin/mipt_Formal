import fileinput
from formlang import prefix

def main():
    for line in fileinput.input():
        L, x, k = line.split()
        print(prefix.PrefixChecker(L).check(x * int(k)))

if __name__ == "__main__":
    main()
