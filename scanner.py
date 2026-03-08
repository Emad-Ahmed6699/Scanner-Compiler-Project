import re

# ============================================================
# GoalLang Scanner - Token Patterns Dictionary
# ============================================================
TOKEN_PATTERNS = {
    'COMMENT':      r'#[^\n]*',
    'STRING':       r'(["\'])([^\\]\1|\\.|[^\1\\])*?\1',
    'BOOLEAN':      r'\b(true|false)\b',
    'NUMBER':       r'\d+(?:\.\d+)?',
    'RESERVED':     r'\b(kickoff|shout|receive|referee|offside|training|match|goal|import|stadium|range|in)\b',
    'OPERATOR':     r'(<=|>=|==|!=|<<|>>|\*\*|\*|//|/|%|\+|-|=|<|>|!)',
    'SYMBOL':       r'[(){}\[\]:,.]',
    'IDENTIFIER':   r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'WHITESPACE':   r'\s+',
}

# ============================================================
# Build Combined Regex Pattern from Dictionary
# ============================================================
def build_token_pattern(patterns_dict):
    """Create a combined regex pattern with named groups"""
    pattern_list = [f'(?P<{name}>{pattern})' for name, pattern in patterns_dict.items()]
    return '|'.join(pattern_list)

# ============================================================
# GoalLang Token Type Classification and Keywords Mapping
# ============================================================
TOKEN_TYPES = {
    'COMMENT':      'Comment',
    'STRING':       'String',
    'NUMBER':       'Number',
    'BOOLEAN':      'Boolean',
    'RESERVED':     'Keyword',
    'OPERATOR':     'Operator',
    'SYMBOL':       'Symbol',
    'IDENTIFIER':   'Identifier',
    'WHITESPACE':   'Whitespace',
}

# ============================================================
# Scanner Class using re.finditer()
# ============================================================
class Scanner:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.pattern = build_token_pattern(TOKEN_PATTERNS)
        
    def scan(self):
        """Scan code and extract tokens using re.finditer()"""
        for match in re.finditer(self.pattern, self.code):
            token_type = match.lastgroup  # Which group matched?
            token_value = match.group()    # What text matched?
            
            # Skip whitespace and comment tokens
            if token_type in ['WHITESPACE', 'COMMENT']:
                continue
            
            # Store token information
            token_info = {
                'type': TOKEN_TYPES[token_type],
                'value': token_value,
            }
            self.tokens.append(token_info)
        
        return self.tokens
    
    def print_compact(self):
        """Print tokens in compact (Type, Value) format"""
        for token in self.tokens:
            print(f"({token['type']}, {repr(token['value'])})")

# ============================================================
# Main Scanner Program
# ============================================================
def main():
    print("Enter Filename: ")
    filename = input().strip()
    
    try:
        with open(filename, "r", encoding='utf-8') as f:
            code = f.read()
        
        # Create scanner and scan the code
        scanner = Scanner(code)
        scanner.scan()
        
        # Print tokens
        scanner.print_compact()
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
