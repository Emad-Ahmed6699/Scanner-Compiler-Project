import re

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.line = 1
        self.indent_stack = [0]
        
        # Updated Regex Rules
        self.rules = [
            ('COMMENT',  r'#[^\n]*'),
            ('STRING',   r'"[^"]*"'),
            ('NUMBER',   r'\d+(\.\d+)?'),
            ('KEYWORD',  r'\b(kickoff|shout|receive|training|referee|offside|score|match|import|stadium|player|goal|distance|flag)\b'),
            ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OP',       r'[+\-*/%<>=!&|]+'),
            ('PUNC',     r'[():,\[\]]'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]

    def scan(self):
        lines = self.source.split('\n')
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules)
        
        for line_idx, line in enumerate(lines):
            self.line = line_idx + 1
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            
            if indent > self.indent_stack[-1]:
                self.indent_stack.append(indent)
                self.tokens.append({'type': 'INDENT', 'value': None, 'line': self.line})
            elif indent < self.indent_stack[-1]:
                while indent < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append({'type': 'DEDENT', 'value': None, 'line': self.line})
                if indent != self.indent_stack[-1]:
                    raise Exception(f"Indentation Error at line {self.line}")

            for mo in re.finditer(regex, line):
                kind = mo.lastgroup
                value = mo.group()
                
                if kind == 'SKIP' or kind == 'COMMENT':
                    continue
                elif kind == 'MISMATCH':
                    raise Exception(f"Lexical Error: Unexpected character '{value}' at line {self.line}")
                
                if kind == 'NUMBER':
                    value = float(value) if '.' in value else int(value)
                elif kind == 'STRING':
                    value = value[1:-1]
                    
                self.tokens.append({'type': kind, 'value': value, 'line': self.line})
        
        # Close remaining indents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append({'type': 'DEDENT', 'value': None, 'line': self.line})
            
        self.tokens.append({'type': 'EOF', 'value': None, 'line': self.line})
        return self.tokens