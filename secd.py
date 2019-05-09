import sys
from typing import List, Tuple

from lamtools import interpret_term, LamTerm

def run_secd(term: LamTerm) -> Tuple[Tuple[LamTerm, Tuple], int]:
    stack = []
    curenvironment = None
    curterm = termseq(term)
    dump = []
    steps = 0

    while True:
        steps += 1
        if len(curterm) == 0:
            res = stack.pop()
            if len(dump) == 0:
                return res, steps
            (stack, curenvironment, curterm) = dump.pop()
            stack.append(res)
            continue

        topterm = curterm.pop()

        if topterm == '@':
            left = stack.pop()
            right = stack.pop()
            curenvironment = left[1]
            left = left[0]
            curenvironment = (curenvironment, right)
            if left.right.op == '@':
                dump.append((stack, curenvironment, curterm))
                stack = []
                curterm = termseq(left.right)
            elif left.right.op == 'lam':
                stack.append((left.right, curenvironment))
            else:
                #stack.append(curenvironment[left.right.op])
                curterm.append(left.right)
        elif topterm.op == 'lam':
            closure = (topterm, curenvironment)
            stack.append(closure)
        else:
            for _ in range(topterm.op[0]):
                curenvironment = curenvironment[0]
            stack.append(curenvironment[1])
        

def termseq(term: LamTerm) -> List:
    seq = []
    if term.op == '@':
        seq.append('@')
        seq.extend(termseq(term.left))
        seq.extend(termseq(term.right))
    else:
        seq.append(term)
    return seq

def simplify_closure(closure: Tuple[LamTerm, Tuple], level: int = 0) -> LamTerm:
    """Convert a closure to a simple term (no computation)"""
    term, environment = closure
    if term.op == 'lam':
        term.right = simplify_closure((term.right, environment), level+1)
    elif term.op == '@':
        term.left = simplify_closure((term.left, environment), level)
        term.right = simplify_closure((term.right, environment), level)
    else:
        if term.op[0] >= level:
            for _ in range(term.op[0]-level):
                environment = environment[0]
            closure = environment[1]
            term = simplify_closure(closure, 0)
    return term
    
if __name__ == '__main__':
    t = interpret_term(sys.argv[1])
    t.encode_vars()
    rt, steps = run_secd(t)
    print(rt)
    print(steps)
    print(simplify_closure(rt))
