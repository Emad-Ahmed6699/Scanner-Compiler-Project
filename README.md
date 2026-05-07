# ⚽ GoalLang Scanner & Compiler Project

A complete compiler project for **GoalLang**, a sports-themed programming language. It includes a GUI IDE with lexical analysis, syntax parsing, semantic analysis, and Python code generation.

## Components

- **Lexer** (`lexer.py`): Tokenizes GoalLang source code into tokens
- **Parser** (`parser.py`): Builds an Abstract Syntax Tree (AST) from tokens
- **Semantic Analyzer** (`analyzer.py`): Performs type checking and semantic validation
- **Code Generator** (`generator.py`): Converts AST to executable Python code
- **IDE** (`ide.py`): Full-featured GUI for writing and testing GoalLang code

## Features

✨ **Modern IDE**:
- Syntax highlighting for GoalLang keywords
- Live compilation and error reporting
- AST visualization
- Token and symbol table inspection
- Auto-indentation support
- Line numbers

🔧 **Complete Compilation Pipeline**:
- Lexical Analysis (scanning)
- Syntax Analysis (parsing)
- Semantic Analysis (validation)
- Code Generation (Python)

## Usage

### GUI IDE
```bash
python ide.py
```

The IDE provides:
- **Code Editor**: Write GoalLang code
- **Compiler**: Run code and see results instantly
- **Tabs**:
  - 💻 TERMINAL: Execution output
  - 🐍 PYTHON: Generated Python code
  - 🔍 TOKENS: Token analysis
  - 📊 SYMBOLS: Symbol table
  - 🌳 PARSER TREE: AST visualization

### Command Line
```bash
python main.py test.goal
```

## GoalLang Syntax Example

```goal
score kickoff:
    shout "Enter player name: "
    receive name
    
    shout "Enter goals: "
    receive goals
    
    shout name + " scored " + goals + " goals!"
    goal 0
```

## Key Keywords

- `score` - Variable declaration
- `shout` - Print output
- `receive` - Read input
- `kickoff` - Main function
- `goal` - Exit/return
- `player` - Parameter
- `assistant` - Helper function