import sys
from typing import List, Tuple

from lamtools import interpret_term, LamTerm

def run_kirvine(term):
    curterm = term
    curenviron = None
    stack = []
    steps = 0
    while True:
        steps += 1
        if curterm.op == '@':
            stack.append((curterm.right, curenviron))
            curterm = curterm.left
        elif curterm.op == 'mlam':
            if len(stack) < len(curterm.left):
                break
            curenviron = (curenviron, stack[-len(curterm.left)::-1])
            stack = stack[:-len(curterm.left)]
            curterm = curterm.right
        elif curterm.op == 'lam':
            if len(stack) == 0:
                break
            curenviron = (curenviron, [stack.pop()])
            curterm = curterm.right
        else: # is var
            if curterm.op[0] != 0:
                for _ in range(curterm.op[0]):
                    if curenviron is not None:
                        curenviron = curenviron[0]
                    else:
                        break
            if curenviron is not None:
                curterm, curenviron = curenviron[1][curterm.op[1]-1] # closure k at environ e
            else:
                break
    return (curterm, curenviron), steps 

def simplify_closure(closure: Tuple[LamTerm, List[Tuple]], level: int = 0) -> LamTerm:
    """Convert a closure to a simple term (no computation)"""
    term, environment = closure
    if term.op == 'mlam':
        term.right = simplify_closure((term.right, environment), level+1)
    elif term.op == 'lam':
        term.right = simplify_closure((term.right, environment), level+1)
    elif term.op == '@':
        term.left = simplify_closure((term.left, environment), level)
        term.right = simplify_closure((term.right, environment), level)
    else:
        if term.op[0] >= level:
            for _ in range(term.op[0]-level):
                environment = environment[0]
            closure = environment[1][term.op[1]-1]
            term = simplify_closure(closure, 0)
    return term

if __name__ == '__main__':
    t = interpret_term(sys.argv[1])
    #t.collapse_lams()
    t.encode_vars()
    print(t)
    rc, steps = run_kirvine(t)
    print(rc)
    st = simplify_closure(rc)
    print(st)
    print(steps)