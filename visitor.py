from pycparser.c_ast import FileAST, FuncDef, Compound, Decl, FuncCall, ID, ExprList
from typing import Any
import z3

class Visitor:
    def __init__(self):
        # We will collect our Z3 constraints here
        self.constraints = True
        self.variable_map = {}
    
    def get_variable(self, s: str):
        """
        Given the string representation of a variable `s`, returns the
        last instance of the variable to be used as a constraint. For
        example, if variable "x" has never been used before, calling
        `get_variable(x)` will return "x0".
        """
        if s not in self.variable_map:
            self.variable_map[s] = 0

        return f"{s}{self.variable_map[s]}"

    def fresh_variable(self, s: str):
        """
        This function behaves like `get_variable` but if the variable
        has been used before, it will return a fresh instance. For example,
        if variable "x" has been seen before and the last instance we've used
        in the constraints is "x5", calling `fresh_variable(x)` will return "x6".
        """
        if s not in self.variable_map:
            self.variable_map[s] = 0
        else:
            self.variable_map[s] += 1
        
        return f"{s}{self.variable_map[s]}"

    def is_satisfiable(self) -> bool:
        solver = z3.Solver()
        
        # Handle both single constraints and collections of constraints
        if isinstance(self.constraints, list) or isinstance(self.constraints, set):
            solver.add(self.constraints)
        else:
            solver.add(self.constraints)
            
        # Check satisfiability
        result = solver.check()
        
        # return sat/unsat result as boolean
        return result == z3.sat

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
        print(ast)
        name = ast.name
        
        init = ast.init
        if isinstance(init, FuncCall):
            func_id = ast.init.name
            if isinstance(func_id, ID):
                func_name = func_id.name
                if func_name == 'malloc':
                    r_name = name

                    # This variable must be non-owning before assignment, and owning right after
                    c1 = z3.Int(self.get_variable(r_name)) == 0
                    c2 = z3.Int(self.fresh_variable(r_name)) == 1

                    self.constraints = z3.And(self.constraints, c1, c2)

        elif isinstance(init, ID):
            y_name = init.name
            z_name = name

            # We might transfer ownership here (STMT-ASGN)
            c1 = z3.Int(self.get_variable(z_name)) == 0
            c2 = z3.Int(self.get_variable(y_name)) == z3.Int(self.fresh_variable(y_name)) + z3.Int(self.fresh_variable(z_name))

            self.constraints = z3.And(self.constraints, c1, c2)
    
    def visit_func_call(self, ast: FuncCall):
        func_id = ast.name
        if isinstance(func_id, ID):
            func_name = func_id.name
            if func_name == 'free':
                y_name = ast.args.exprs[0].name
                
                # The variable being freed must be owning before, and is non owning after
                c1 = z3.Int(self.get_variable(y_name)) == 1
                c2 = z3.Int(self.fresh_variable(y_name)) == 0

                self.constraints = z3.And(self.constraints, c1, c2)
