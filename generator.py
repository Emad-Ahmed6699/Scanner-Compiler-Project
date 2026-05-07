from ast_nodes import *

class CodeGenerator:
    RUNTIME_HEADER = """
# GoalLang Runtime Library
def goal_shout(*args):
    print(*(str(arg) for arg in args))

def goal_add(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return str(a) + str(b)
    return a + b

def goal_receive():
    val = input()
    try:
        if '.' in val: return float(val)
        return int(val)
    except ValueError:
        return val
"""

    def __init__(self):
        self.indent_level = 0
        self.result = [self.RUNTIME_HEADER.strip()]

    def _indent(self):
        return "    " * self.indent_level

    def visit(self, node):
        if not node: return ""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return ""

    def generate(self, ast):
        self.visit(ast)
        return "\n".join(self.result)

    def visit_Program(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_ImportNode(self, node):
        self.result.append(f"{self._indent()}import {node.module_name}")

    def visit_StadiumNode(self, node):
        self.result.append(f"\n{self._indent()}class {node.name}:")
        self.indent_level += 1
        if not node.body:
            self.result.append(f"{self._indent()}pass")
        else:
            for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1

    def visit_FunctionDef(self, node):
        params = ", ".join(node.params)
        self.result.append(f"\n{self._indent()}def {node.name}({params}):")
        self.indent_level += 1
        if not node.body:
            self.result.append(f"{self._indent()}pass")
        else:
            for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1

    def visit_Kickoff(self, node):
        self.result.append('\nif __name__ == "__main__":')
        self.indent_level += 1
        if not node.body:
            self.result.append(f"{self._indent()}pass")
        else:
            for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1

    def visit_Shout(self, node):
        expr_code = self.visit(node.expr)
        self.result.append(f"{self._indent()}goal_shout({expr_code})")

    def visit_Receive(self, node):
        self.result.append(f"{self._indent()}{node.name} = goal_receive()")

    def visit_Assign(self, node):
        val_code = self.visit(node.value)
        self.result.append(f"{self._indent()}{node.name} = {val_code}")

    def visit_VarDecl(self, node):
        val_code = self.visit(node.value) if node.value else "None"
        self.result.append(f"{self._indent()}{node.name} = {val_code}")

    def visit_If(self, node):
        cond_code = self.visit(node.cond)
        self.result.append(f"{self._indent()}if {cond_code}:")
        self.indent_level += 1
        for stmt in node.then: self.visit(stmt)
        self.indent_level -= 1
        if node.otherwise:
            self.result.append(f"{self._indent()}else:")
            self.indent_level += 1
            for stmt in node.otherwise: self.visit(stmt)
            self.indent_level -= 1

    def visit_While(self, node):
        cond_code = self.visit(node.cond)
        self.result.append(f"{self._indent()}while {cond_code}:")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1

    def visit_For(self, node):
        iter_code = self.visit(node.iterable)
        self.result.append(f"{self._indent()}for {node.var} in {iter_code}:")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+': return f"goal_add({left}, {right})"
        return f"({left} {node.op} {right})"

    def visit_UnaryOp(self, node):
        expr = self.visit(node.expr)
        op = node.op if node.op != '!' else 'not '
        return f"({op}{expr})"

    def visit_Literal(self, node):
        if isinstance(node.value, str): return repr(node.value)
        return str(node.value)

    def visit_Variable(self, node):
        return node.name

    def visit_Return(self, node):
        val = self.visit(node.value) if node.value else ""
        self.result.append(f"{self._indent()}return {val}")

    def visit_FunctionCall(self, node):
        args = [self.visit(arg) for arg in node.args]
        return f"{node.name}({', '.join(args)})"
