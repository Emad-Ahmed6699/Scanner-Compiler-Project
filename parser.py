from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        index = self.pos + offset
        return self.tokens[index] if index < len(self.tokens) else {'type': 'EOF', 'value': None}

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def match(self, expected_value=None, expected_type=None):
        tok = self.peek()
        if expected_value and tok['value'] != expected_value:
            raise Exception(f"Syntax Error (line {tok['line']}): Expected '{expected_value}', found '{tok['value']}'")
        if expected_type and tok['type'] != expected_type:
            raise Exception(f"Syntax Error (line {tok['line']}): Expected type '{expected_type}', found '{tok['type']}'")
        return self.advance()

    def parse(self):
        body = []
        while self.peek()['type'] != 'EOF':
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        return Program(body)

    def statement(self):
        tok = self.peek()
        
        # Handle Import
        if tok['value'] == 'import':
            line = tok['line']
            self.advance()
            module = self.match(expected_type='ID')['value']
            return ImportNode(module, line)
        
        # Handle Stadium (Class/Module)
        if tok['value'] == 'stadium':
            line = tok['line']
            self.advance()
            name = self.match(expected_type='ID')['value']
            self.match(':')
            body = self._block()
            return StadiumNode(name, body, line)

        # Handle Function Definition: score [assist] [name](params):
        if tok['value'] == 'score' and self.peek(1)['type'] == 'ID' and self.peek(2)['value'] == '(':
            line = tok['line']
            self.advance() # score
            name = self.match(expected_type='ID')['value']
            self.match('(')
            params = []
            if self.peek()['value'] != ')':
                params.append(self.match(expected_type='ID')['value'])
                while self.peek()['value'] == ',':
                    self.advance()
                    params.append(self.match(expected_type='ID')['value'])
            self.match(')')
            self.match(':')
            body = self._block()
            return FunctionDef(name, params, body, line)

        # Handle Kickoff (Main Entry) - Support both 'kickoff:' and 'score kickoff:'
        if tok['value'] == 'kickoff' or (tok['value'] == 'score' and self.peek(1)['value'] == 'kickoff'):
            line = tok['line']
            if tok['value'] == 'score': self.advance()
            self.advance() # kickoff
            self.match(':')
            return Kickoff(self._block(), line)

        # Other statements
        if tok['value'] == 'shout':
            line = tok['line']
            self.advance()
            return Shout(self.expression(), line)
        
        if tok['value'] == 'receive':
            line = tok['line']
            self.advance()
            name = self.match(expected_type='ID')['value']
            return Receive(name, line)

        if tok['value'] == 'referee': # If
            line = tok['line']
            self.advance()
            cond = self.expression()
            self.match(':')
            then_block = self._block()
            otherwise = None
            if self.peek()['value'] == 'offside':
                self.advance()
                self.match(':')
                otherwise = self._block()
            return If(cond, then_block, otherwise, line)

        if tok['value'] == 'training': # While
            line = tok['line']
            self.advance()
            cond = self.expression()
            self.match(':')
            return While(cond, self._block(), line)

        if tok['value'] == 'match': # For
            line = tok['line']
            self.advance()
            var = self.match(expected_type='ID')['value']
            self.match('in')
            iterable = self.expression()
            self.match(':')
            return For(var, iterable, self._block(), line)

        if tok['value'] == 'goal': # Return
            line = tok['line']
            self.advance()
            return Return(self.expression(), line)

        # Assignments or function calls
        if tok['type'] == 'ID':
            line = tok['line']
            if self.peek(1)['value'] == '=':
                name = self.advance()['value']
                self.advance() # =
                return Assign(name, self.expression(), line)
            elif self.peek(1)['value'] == '(':
                return self.expression() # It's a function call expression

        # Variable declarations
        if tok['value'] in ['score', 'distance', 'player', 'flag']:
            line = tok['line']
            dtype = self.advance()['value']
            name = self.match(expected_type='ID')['value']
            value = None
            if self.peek()['value'] == '=':
                self.advance()
                value = self.expression()
            return VarDecl(name, dtype, value, line)

        self.advance() # Skip unknown to avoid infinite loop
        return None

    def _block(self):
        self.match(expected_type='INDENT')
        body = []
        while self.peek()['type'] != 'DEDENT' and self.peek()['type'] != 'EOF':
            stmt = self.statement()
            if stmt: body.append(stmt)
        self.match(expected_type='DEDENT')
        return body

    def expression(self):
        return self.comparison()

    def comparison(self):
        left = self.term()
        while self.peek()['value'] in ['>', '<', '>=', '<=', '==', '!=']:
            tok = self.peek()
            op = self.advance()['value']
            left = BinOp(left, op, self.term(), tok['line'])
        return left

    def term(self):
        left = self.factor()
        while self.peek()['value'] in ['+', '-']:
            tok = self.peek()
            op = self.advance()['value']
            left = BinOp(left, op, self.factor(), tok['line'])
        return left

    def factor(self):
        left = self.unary()
        while self.peek()['value'] in ['*', '/', '%']:
            tok = self.peek()
            op = self.advance()['value']
            left = BinOp(left, op, self.unary(), tok['line'])
        return left

    def unary(self):
        if self.peek()['value'] in ['-', '+', '!']:
            tok = self.peek()
            op = self.advance()['value']
            return UnaryOp(op, self.unary(), tok['line'])
        return self.primary()

    def primary(self):
        tok = self.peek()
        if tok['type'] == 'NUMBER':
            return Literal(self.advance()['value'], tok['line'])
        if tok['type'] == 'STRING':
            return Literal(self.advance()['value'], tok['line'])
        if tok['type'] == 'ID':
            line = tok['line']
            name = self.advance()['value']
            if self.peek()['value'] == '(':
                self.advance()
                args = []
                if self.peek()['value'] != ')':
                    args.append(self.expression())
                    while self.peek()['value'] == ',':
                        self.advance()
                        args.append(self.expression())
                self.match(')')
                return FunctionCall(name, args, line)
            return Variable(name, line)
        if tok['value'] == '(':
            self.advance()
            expr = self.expression()
            self.match(')')
            return expr
        
        raise Exception(f"Syntax Error (line {tok['line']}): Unexpected token '{tok['value']}' in expression")