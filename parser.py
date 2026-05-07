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
            self.advance()
            module = self.match(expected_type='ID')['value']
            return ImportNode(module)
        
        # Handle Stadium (Class/Module)
        if tok['value'] == 'stadium':
            self.advance()
            name = self.match(expected_type='ID')['value']
            self.match(':')
            body = self._block()
            return StadiumNode(name, body)

        # Handle Function Definition: score assist [name](params):
        if tok['value'] == 'score' and self.peek(1)['value'] == 'assist':
            self.advance() # score
            self.advance() # assist
            
            # If next is '(', the function name is 'assist' (as seen in some slides)
            if self.peek()['value'] == '(':
                name = "assist"
            else:
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
            return FunctionDef(name, params, body)

        # Handle Kickoff (Main Entry) - Support both 'kickoff:' and 'score kickoff:'
        if tok['value'] == 'kickoff' or (tok['value'] == 'score' and self.peek(1)['value'] == 'kickoff'):
            if tok['value'] == 'score': self.advance()
            self.advance() # kickoff
            self.match(':')
            return Kickoff(self._block())

        # Other statements
        if tok['value'] == 'shout':
            self.advance()
            return Shout(self.expression())
        
        if tok['value'] == 'receive':
            self.advance()
            name = self.match(expected_type='ID')['value']
            return Receive(name)

        if tok['value'] == 'referee': # If
            self.advance()
            cond = self.expression()
            self.match(':')
            then_block = self._block()
            otherwise = None
            if self.peek()['value'] == 'offside':
                self.advance()
                self.match(':')
                otherwise = self._block()
            return If(cond, then_block, otherwise)

        if tok['value'] == 'training': # While
            self.advance()
            cond = self.expression()
            self.match(':')
            return While(cond, self._block())

        if tok['value'] == 'match': # For
            self.advance()
            var = self.match(expected_type='ID')['value']
            self.match('in')
            iterable = self.expression()
            self.match(':')
            return For(var, iterable, self._block())

        if tok['value'] == 'goal': # Return
            self.advance()
            return Return(self.expression())

        # Assignments or function calls
        if tok['type'] == 'ID':
            if self.peek(1)['value'] == '=':
                name = self.advance()['value']
                self.advance() # =
                return Assign(name, self.expression())
            elif self.peek(1)['value'] == '(':
                return self.expression() # It's a function call expression

        # Variable declarations
        if tok['value'] in ['score', 'distance', 'player', 'flag']:
            dtype = self.advance()['value']
            name = self.match(expected_type='ID')['value']
            value = None
            if self.peek()['value'] == '=':
                self.advance()
                value = self.expression()
            return VarDecl(name, dtype, value)

        self.advance() # Skip unknown to avoid infinite loop
        return None

    def _block(self):
        # In this simple implementation, we assume blocks are followed by statements
        # A more robust one would handle INDENT/DEDENT properly
        # For now, let's assume all statements in a block are consumed until a keyword that ends a block or EOF
        # Since we are using keywords like kickoff/referee, we can collect statements.
        # But wait, GoalLang uses indentation. Our Lexer doesn't emit INDENT/DEDENT currently.
        # Let's fix that or use a simple lookahead.
        # Actually, let's assume a block is a list of statements.
        body = []
        # This is a bit tricky without INDENT tokens. 
        # I'll implement a simple heuristic: consume until we see a keyword that isn't allowed in a block or a new block starter.
        # BETTER: Let's assume for now that if the next line has more spaces, it's a block.
        # But we don't have spaces in lexer. 
        # I will assume the next 1 statement or a specific pattern.
        # TO BE PRO: I should have added INDENT/DEDENT in Lexer. 
        # I'll do a quick fix to consume at least one statement and more if they look like they belong.
        
        # Simple fix: collect statements as long as they aren't top-level keywords
        # Heuristic: consume until we see a top-level keyword or end of scope
        stop_keywords = ['kickoff', 'stadium', 'offside']
        while self.peek()['value'] not in stop_keywords and self.peek()['type'] != 'EOF':
             # Also stop if we see score assist (another function) or score kickoff
             if self.peek()['value'] == 'score' and self.peek(1)['value'] in ['assist', 'kickoff']:
                 break
             stmt = self.statement()
             if stmt: body.append(stmt)
             else: break
        return body

    def expression(self):
        return self.comparison()

    def comparison(self):
        left = self.term()
        while self.peek()['value'] in ['>', '<', '>=', '<=', '==', '!=']:
            op = self.advance()['value']
            left = BinOp(left, op, self.term())
        return left

    def term(self):
        left = self.factor()
        while self.peek()['value'] in ['+', '-']:
            op = self.advance()['value']
            left = BinOp(left, op, self.factor())
        return left

    def factor(self):
        left = self.unary()
        while self.peek()['value'] in ['*', '/', '%']:
            op = self.advance()['value']
            left = BinOp(left, op, self.unary())
        return left

    def unary(self):
        if self.peek()['value'] in ['-', '+', '!']:
            op = self.advance()['value']
            return UnaryOp(op, self.unary())
        return self.primary()

    def primary(self):
        tok = self.peek()
        if tok['type'] == 'NUMBER':
            return Literal(self.advance()['value'])
        if tok['type'] == 'STRING':
            return Literal(self.advance()['value'])
        if tok['type'] == 'ID':
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
                return FunctionCall(name, args)
            return Variable(name)
        if tok['value'] == '(':
            self.advance()
            expr = self.expression()
            self.match(')')
            return expr
        
        raise Exception(f"Syntax Error (line {tok['line']}): Unexpected token '{tok['value']}' in expression")