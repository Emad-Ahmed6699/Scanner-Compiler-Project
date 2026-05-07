import re

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.line = 1
        
        # Updated Regex Rules
        self.rules = [
            ('COMMENT',  r'#[^\n]*'),           # Fixed: Now matches the whole line
            ('STRING',   r'"[^"]*"'),
            ('NUMBER',   r'\d+(\.\d+)?'),
            ('KEYWORD',  r'\b(kickoff|shout|receive|training|referee|offside|score|assist|match|import|stadium|player|goal|distance|flag)\b'),
            ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OP',       r'[+\-*/%<>=!&|]+'),
            ('PUNC',     r'[():,\[\]]'),
            ('NEWLINE',  r'\n'),
            ('SKIP',     r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]

    def scan(self):
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules)
        for mo in re.finditer(regex, self.source):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == 'NEWLINE':
                self.line += 1
                continue
            elif kind == 'SKIP' or kind == 'COMMENT':
                continue
            elif kind == 'MISMATCH':
                raise Exception(f"Lexical Error: Unexpected character '{value}' at line {self.line}")
            
            # Type Conversion
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'STRING':
                value = value[1:-1]
                
            self.tokens.append({'type': kind, 'value': value, 'line': self.line})
        
        # Add EOF Token (End of File)
        self.tokens.append({'type': 'EOF', 'value': None, 'line': self.line})
        return self.tokens