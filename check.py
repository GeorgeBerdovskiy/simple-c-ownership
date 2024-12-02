from pycparser import parse_file
from pycparser.c_ast import FileAST

from visitor import Visitor

def parse(source) -> FileAST:
    ast = parse_file(source)
    return ast

if __name__ == "__main__":
    print("Running...")

    ast = parse("examples/valid.c")

    v = Visitor()
    v.visit_file(ast)
    is_valid = v.is_satisfiable()

    print(f"Satisfies ownership rules? {is_valid}")
