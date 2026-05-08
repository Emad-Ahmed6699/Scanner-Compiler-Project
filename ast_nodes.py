class ASTNode:
    def __init__(self, line=0):
        self.line = line
    def get_children(self):
        return []
    def get_name(self):
        return self.__class__.__name__

class Program(ASTNode):
    def __init__(self, body, line=0):
        super().__init__(line)
        self.body = body
    def get_children(self):
        return self.body

class ImportNode(ASTNode):
    def __init__(self, module_name, line=0):
        super().__init__(line)
        self.module_name = module_name
    def get_name(self):
        return f"Import({self.module_name})"

class StadiumNode(ASTNode):
    def __init__(self, name, body, line=0):
        super().__init__(line)
        self.name = name
        self.body = body
    def get_name(self):
        return f"Stadium({self.name})"
    def get_children(self):
        return self.body

class Kickoff(ASTNode):
    def __init__(self, body, line=0):
        super().__init__(line)
        self.body = body
    def get_children(self):
        return self.body

class FunctionDef(ASTNode):
    def __init__(self, name, params, body, line=0):
        super().__init__(line)
        self.name = name
        self.params = params # List of strings
        self.body = body
    def get_name(self):
        return f"Score {self.name}({', '.join(self.params)})"
    def get_children(self):
        return self.body

class Shout(ASTNode):
    def __init__(self, expr, line=0):
        super().__init__(line)
        self.expr = expr
    def get_children(self):
        return [self.expr]

class Receive(ASTNode):
    def __init__(self, name, line=0):
        super().__init__(line)
        self.name = name

class Assign(ASTNode):
    def __init__(self, name, value, line=0):
        super().__init__(line)
        self.name = name
        self.value = value
    def get_name(self):
        return f"Assign({self.name})"
    def get_children(self):
        return [self.value]

class VarDecl(ASTNode):
    def __init__(self, name, dtype, value=None, line=0):
        super().__init__(line)
        self.name = name
        self.dtype = dtype
        self.value = value
    def get_name(self):
        return f"Declare {self.name}:{self.dtype}"
    def get_children(self):
        return [self.value] if self.value else []

class If(ASTNode):
    def __init__(self, cond, then, otherwise=None, line=0):
        super().__init__(line)
        self.cond = cond
        self.then = then
        self.otherwise = otherwise
    def get_children(self):
        res = [self.cond] + self.then
        if self.otherwise: res += self.otherwise
        return res

class While(ASTNode):
    def __init__(self, cond, body, line=0):
        super().__init__(line)
        self.cond = cond
        self.body = body
    def get_children(self):
        return [self.cond] + self.body

class For(ASTNode):
    def __init__(self, var, iterable, body, line=0):
        super().__init__(line)
        self.var = var
        self.iterable = iterable
        self.body = body
    def get_children(self):
        return [self.iterable] + self.body

class FunctionCall(ASTNode):
    def __init__(self, name, args, line=0):
        super().__init__(line)
        self.name = name
        self.args = args
    def get_name(self):
        return f"Call {self.name}"
    def get_children(self):
        return self.args

class Return(ASTNode):
    def __init__(self, value, line=0):
        super().__init__(line)
        self.value = value
    def get_children(self):
        return [self.value] if self.value else []

class BinOp(ASTNode):
    def __init__(self, left, op, right, line=0):
        super().__init__(line)
        self.left = left
        self.op = op
        self.right = right
    def get_name(self):
        return f"Op({self.op})"
    def get_children(self):
        return [self.left, self.right]

class UnaryOp(ASTNode):
    def __init__(self, op, expr, line=0):
        super().__init__(line)
        self.op = op
        self.expr = expr
    def get_name(self):
        return f"Unary({self.op})"
    def get_children(self):
        return [self.expr]

class Variable(ASTNode):
    def __init__(self, name, line=0):
        super().__init__(line)
        self.name = name
    def get_name(self):
        return f"Var({self.name})"

class Literal(ASTNode):
    def __init__(self, value, line=0):
        super().__init__(line)
        self.value = value
    def get_name(self):
        return f"Literal({self.value})"