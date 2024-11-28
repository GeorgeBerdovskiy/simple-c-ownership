from pycparser.c_ast import FileAST, FuncDef, Compound, Decl, FuncCall, ID, ExprList
from typing import Any
import z3

class Visitor:
    def __init__(self):
        # We will collect our Z3 constraints here
        self.constraints = True

    def visit_file(self, ast: FileAST):
        for _, child in ast.children():
            if isinstance(child, FuncDef):
                self.visit_func_def(child)
    
    def visit_func_def(self, ast: FuncDef):
        self.visit_compound(ast.body)
    
    def visit_compound(self, ast: Compound):
        for item in ast.block_items:
            self.visit_block_item(item)
    
    def visit_block_item(self, ast: Any):
        if isinstance(ast, Decl):
            self.visit_decl(ast)
        elif isinstance(ast, FuncCall):
            self.visit_func_call(ast)
    
    def visit_decl(self, ast: Decl):
        print("Visiting a variable declaration")
        name = ast.name
        
        init = ast.init
        if isinstance(init, FuncCall):
            func_id = ast.init.name
            if isinstance(func_id, ID):
                func_name = func_id.name
                if func_name == 'malloc':
                    # This variable must be owning here
                    self.constraints = z3.And(self.constraints, z3.Bool(name) == True)
    
    def visit_func_call(self, ast: FuncCall):
        func_id = ast.name
        if isinstance(func_id, ID):
            func_name = func_id.name
            if func_name == 'free':
                # What are we freeing?
                variable = ast.args.exprs[0].name
                self.constraints = z3.And(self.constraints, z3.Bool(variable) == True)

