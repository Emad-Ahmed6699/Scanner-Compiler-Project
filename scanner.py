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

# Keyword meanings for documentation
KEYWORD_MEANINGS = {
    'kickoff':  'main entry point',
    'shout':    'output/print',
    'receive':  'input',
    'referee':  'if condition',
    'offside':  'else',
    'training': 'while loop',
    'match':    'for loop',
    'goal':     'return statement',
    'import':   'include module',
    'stadium':  'namespace',
    'range':    'range function',
    'in':       'in operator',
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
            position = match.start()       # Where in the string?
            
            # Skip whitespace tokens
            if token_type == 'WHITESPACE':
                continue
            
            # Skip comment tokens (optional - change if needed)
            if token_type == 'COMMENT':
                continue
            
            # Store token information
            token_info = {
                'type': TOKEN_TYPES[token_type],
                'value': token_value,
                'position': position,
                'regex_group': token_type,
                'meaning': KEYWORD_MEANINGS.get(token_value, '')
            }
            self.tokens.append(token_info)
        
        return self.tokens
    
    def print_header(self):
        """Print GoalLang Scanner header"""
        print("\n" + "="*90)
        print(" " * 25 + "🎯 GoalLang Scanner (Lexical Analyzer)")
        print(" " * 30 + "Code your way to the Goal!")
        print("="*90 + "\n")
    
    def print_tokens(self):
        """Print all tokens in detailed formatted way"""
        self.print_header()
        print(f"{'TOKEN TYPE':<15} {'VALUE':<20} {'POSITION':<10} {'MEANING':<30}")
        print("-"*90)
        
        for token in self.tokens:
            meaning = token['meaning'] if token['meaning'] else '-'
            print(f"{token['type']:<15} {repr(token['value']):<20} {token['position']:<10} {meaning:<30}")
        
        print("="*90)
        print(f"✓ Total Tokens Scanned: {len(self.tokens)}")
        print("="*90 + "\n")
    
    def print_compact(self):
        """Print tokens in compact (Type, Value) format"""
        print("\n📋 Compact Format (Type, Value):")
        print("-" * 50)
        for token in self.tokens:
            print(f"({token['type']:<12}, {repr(token['value'])})")
        print("-" * 50 + "\n")
    
    def get_statistics(self):
        """Get token statistics"""
        stats = {}
        for token in self.tokens:
            token_type = token['type']
            stats[token_type] = stats.get(token_type, 0) + 1
        return stats
    
    def print_statistics(self):
        """Print token type statistics"""
        stats = self.get_statistics()
        print("\n📊 Token Statistics:")
        print("-" * 40)
        for token_type, count in sorted(stats.items()):
            print(f"  {token_type:<15}: {count:>3} tokens")
        print("-" * 40 + "\n")

# ============================================================
# Main Scanner Program
# ============================================================
def main():
    print("\n" + "="*60)
    print("         🎯 GoalLang Lexical Scanner")
    print("   Welcome to GoalLang - Code Your Way to the Goal!")
    print("="*60)
    print("\nEnter Filename (or 'test' to scan prog1.py): ")
    filename = input().strip()
    
    if filename.lower() == 'test':
        filename = 'prog1.py'
    
    try:
        with open(filename, "r", encoding='utf-8') as f:
            code = f.read()
        
        # Create scanner and scan the code
        scanner = Scanner(code)
        scanner.scan()
        
        # Print results with detailed analysis
        scanner.print_tokens()
        scanner.print_compact()
        scanner.print_statistics()
        
    except FileNotFoundError:
        print(f"\n❌ Error: File '{filename}' not found!")
        print("Make sure the file is in the same directory as this script.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
