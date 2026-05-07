class ASTNode:
    def get_children(self):
        return []
    def get_name(self):
        return self.__class__.__name__

class Program(ASTNode):
    def __init__(self, body):
        self.body = body
    def get_children(self):
        return self.body

class ImportNode(ASTNode):
    def __init__(self, module_name):
        self.module_name = module_name
    def get_name(self):
        return f"Import({self.module_name})"

class StadiumNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body
    def get_name(self):
        return f"Stadium({self.name})"
    def get_children(self):
        return self.body

class Kickoff(ASTNode):
    def __init__(self, body):
        self.body = body
    def get_children(self):
        return self.body

class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params # List of strings
        self.body = body
    def get_name(self):
        return f"Score {self.name}({', '.join(self.params)})"
    def get_children(self):
        return self.body

class Shout(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def get_children(self):
        return [self.expr]

class Receive(ASTNode):
    def __init__(self, name):
        self.name = name

class Assign(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def get_name(self):
        return f"Assign({self.name})"
    def get_children(self):
        return [self.value]

class VarDecl(ASTNode):
    def __init__(self, name, dtype, value=None):
        self.name = name
        self.dtype = dtype
        self.value = value
    def get_name(self):
        return f"Declare {self.name}:{self.dtype}"
    def get_children(self):
        return [self.value] if self.value else []

class If(ASTNode):
    def __init__(self, cond, then, otherwise=None):
        self.cond = cond
        self.then = then
        self.otherwise = otherwise
    def get_children(self):
        res = [self.cond] + self.then
        if self.otherwise: res += self.otherwise
        return res

class While(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    def get_children(self):
        return [self.cond] + self.body

class For(ASTNode):
    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body
    def get_children(self):
        return [self.iterable] + self.body

class FunctionCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def get_name(self):
        return f"Call {self.name}"
    def get_children(self):
        return self.args

class Return(ASTNode):
    def __init__(self, value):
        self.value = value
    def get_children(self):
        return [self.value] if self.value else []

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def get_name(self):
        return f"Op({self.op})"
    def get_children(self):
        return [self.left, self.right]

class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def get_name(self):
        return f"Unary({self.op})"
    def get_children(self):
        return [self.expr]

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
    def get_name(self):
        return f"Var({self.name})"

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value
    def get_name(self):
        return f"Literal({self.value})"