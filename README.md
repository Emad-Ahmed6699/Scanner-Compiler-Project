# Scanner-Compiler-Project

A lexical scanner/tokenizer for Python code, built with Python. This scanner analyzes Python source files and breaks them down into tokens, categorizing each one (keywords, operators, identifiers, strings, numbers, and symbols).

## Features

- **Regex-based Tokenization**: Uses Python's `re` library to efficiently parse and tokenize code
- **Token Classification**: Automatically categorizes tokens into:
  - Keywords (def, if, return, elif, else, for, in)
  - Operators (<=, <, >, =, >=, !=, ==, !, *, \, %, +, -)
  - Numbers (integers and floats)
  - Strings (single and double-quoted)
  - Symbols (parentheses, brackets, braces, colons, commas)
  - Identifiers (variable and function names)
- **Built with Python 3.10**

## Usage

1. Run the scanner:
   ```bash
   python scanner1.py
   ```

2. Enter the filename of the Python file you'd like to scan (e.g., `prog1.py`)

3. The scanner will output a list of tokens with their categories in the format: `(category, 'token')`

## Example

Scanning `prog1.py` will produce output like:
```
(reserved, 'def')
(identifier, 'magic_func')
(symbol, '(')
(identifier, 'num')
(symbol, ')')
(symbol, ':')
...
```