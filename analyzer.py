from ast_nodes import *

class SymbolTable:
    def __init__(self):
        # scope_stack will store dictionaries of symbols for each level
        self.scope_stack = [{}] 
        self.all_symbols = [] # For IDE display
        self.functions = {}   # Global function registry: {name: param_count}

    def push_scope(self):
        self.scope_stack.append({})

    def pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def declare(self, name, dtype="var", line=0):
        current_scope = self.scope_stack[-1]
        if name in current_scope:
            raise Exception(f"Semantic Error (line {line}): Variable '{name}' already declared in this scope")
        
        symbol_info = {
            "name": name, 
            "type": dtype, 
            "scope_depth": len(self.scope_stack) - 1, 
            "line": line
        }
        current_scope[name] = symbol_info
        self.all_symbols.append(symbol_info)

    def lookup(self, name, line=0):
        # Search from innermost scope to outermost
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        raise Exception(f"Semantic Error (line {line}): Variable '{name}' not declared")

    def register_function(self, name, param_count, line=0):
        if name in self.functions:
            raise Exception(f"Semantic Error (line {line}): Function '{name}' already defined")
        self.functions[name] = param_count

    def check_function(self, name, arg_count, line=0):
        if name not in self.functions:
            # Built-in functions check (optional)
            if name in ['shout', 'receive']: return
            raise Exception(f"Semantic Error (line {line}): Function '{name}' is not defined")
        
        expected = self.functions[name]
        if arg_count != expected:
            raise Exception(f"Semantic Error (line {line}): Function '{name}' expects {expected} arguments, but got {arg_count}")

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.in_function = False # For Control Flow Validation

    def visit(self, node):
        if not node: return
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.get_children():
            if isinstance(child, list):
                for item in child: self.visit(item)
            else:
                self.visit(child)

    def visit_Program(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_ImportNode(self, node):
        # Mark as a special symbol or just ignore for now
        pass

    def visit_StadiumNode(self, node):
        self.symbol_table.push_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.pop_scope()

    def visit_FunctionDef(self, node):
        # Register the function globally before entering its scope
        self.symbol_table.register_function(node.name, len(node.params))
        self.symbol_table.push_scope()
        
        old_in_function = self.in_function
        self.in_function = True # Now inside a function
        
        for p in node.params:
            self.symbol_table.declare(p, "param")
        for stmt in node.body:
            self.visit(stmt)
            
        self.in_function = old_in_function
        self.symbol_table.pop_scope()

    def visit_Kickoff(self, node):
        self.symbol_table.push_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.pop_scope()

    def visit_Shout(self, node):
        self.visit(node.expr)

    def visit_Receive(self, node):
        try:
            self.symbol_table.lookup(node.name)
        except:
            self.symbol_table.declare(node.name, "var")

    def visit_Assign(self, node):
        self.visit(node.value)
        try:
            self.symbol_table.lookup(node.name)
        except:
            self.symbol_table.declare(node.name, "var")

    def visit_VarDecl(self, node):
        self.symbol_table.declare(node.name, node.dtype)
        if node.value:
            self.visit(node.value)

    def visit_If(self, node):
        self.visit(node.cond)
        self.symbol_table.push_scope()
        for stmt in node.then: self.visit(stmt)
        self.symbol_table.pop_scope()
        if node.otherwise:
            self.symbol_table.push_scope()
            for stmt in node.otherwise: self.visit(stmt)
            self.symbol_table.pop_scope()

    def visit_While(self, node):
        self.visit(node.cond)
        self.symbol_table.push_scope()
        for stmt in node.body: self.visit(stmt)
        self.symbol_table.pop_scope()

    def visit_For(self, node):
        self.symbol_table.push_scope()
        self.symbol_table.declare(node.var, "var")
        self.visit(node.iterable)
        for stmt in node.body: self.visit(stmt)
        self.symbol_table.pop_scope()

    def visit_FunctionCall(self, node):
        for arg in node.args:
            self.visit(arg)
        self.symbol_table.check_function(node.name, len(node.args))

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Variable(self, node):
        self.symbol_table.lookup(node.name)

    def visit_Literal(self, node):
        pass

    def visit_Return(self, node):
        if not self.in_function:
            raise Exception("Semantic Error: 'goal' (return) statement is only allowed inside an 'assist' (function)")
        if node.value:
            self.visit(node.value)
