# ⚽ GoalLang Scanner & Compiler Project

A complete, production-ready compiler for **GoalLang**, a sports-themed programming language that makes coding fun! This project implements a full compiler stack with a modern GUI IDE, transforming GoalLang code into executable Python.

---

## 🎯 Project Overview

GoalLang Compiler is an educational yet powerful compiler project that demonstrates all four phases of compilation:

1. **Lexical Analysis** → Tokenization
2. **Syntax Analysis** → AST Generation
3. **Semantic Analysis** → Type Checking & Validation
4. **Code Generation** → Python Translation

---

## 🏗️ Architecture & Components

| Component | File | Purpose |
|-----------|------|---------|
| **Lexer** | `lexer.py` | Tokenizes GoalLang source into meaningful tokens |
| **Parser** | `parser.py` | Builds Abstract Syntax Tree (AST) from token stream |
| **Analyzer** | `analyzer.py` | Semantic validation, type checking, symbol table management |
| **Generator** | `generator.py` | Converts AST to executable Python code |
| **AST Nodes** | `ast_nodes.py` | Core data structures for tree representation |
| **IDE** | `ide.py` | Feature-rich GUI IDE for development |
| **CLI** | `main.py` | Command-line compiler interface |

---

## ✨ Features

### 🖥️ Modern IDE
- 🎨 **Syntax Highlighting** - Color-coded GoalLang keywords and constructs
- ⚡ **Live Compilation** - Real-time error detection and reporting
- 📊 **Multi-Panel Interface** with 5 integrated analysis tabs:
  - **Terminal** - Program execution output
  - **Python** - Generated Python code viewer
  - **Tokens** - Token stream analysis table
  - **Symbols** - Symbol table with scope tracking
  - **Parser Tree** - Visual AST representation
- 🔢 **Line Numbers** - Easy code navigation
- ↔️ **Smart Auto-Indentation** - Context-aware formatting
- 💾 **File Management** - Open/Save `.goal` files with type filtering

### 🔧 Compiler Features
- ✅ Full lexical analysis with pattern matching
- ✅ Recursive descent parser for GoalLang grammar
- ✅ Symbol table with scope management
- ✅ Semantic error reporting with line numbers
- ✅ Direct Python code generation
- ✅ Clean, executable output code

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- tkinter (included with Python on most systems)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Emad-Ahmed6699/Scanner-Compiler-Project.git
   cd Scanner-Compiler-Project
   ```

2. **Verify Python installation**
   ```bash
   python --version  # Should be 3.10+
   ```

---

## 📋 Usage Guide

### Option 1: GUI IDE (Recommended for Development)

Start the interactive IDE:
```bash
python ide.py
```

**In the IDE:**
1. Write GoalLang code in the main editor
2. Click **▶ RUN COMPILER** to compile and execute
3. View results in the **Terminal** tab
4. Inspect generated Python in the **Python** tab
5. Use **Open** in File menu to load `.goal` files
6. Use **Save** to save your work

---

### Option 2: Command Line Compiler

Compile and execute a GoalLang file:
```bash
python main.py <filename.goal>
```

**Example:**
```bash
python main.py test.goal
```

**Output:**
- Generates `<filename>.py` in the same directory
- Displays compilation status
- Executes and shows program output

---

### Option 3: Direct Python Generation

For custom workflows:
```python
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from generator import CodeGenerator

code = """
score kickoff:
    shout "Hello GoalLang!"
"""

lexer = Lexer(code)
tokens = lexer.scan()

parser = Parser(tokens)
ast = parser.parse()

analyzer = SemanticAnalyzer()
analyzer.visit(ast)

generator = CodeGenerator()
python_code = generator.generate(ast)

# Execute the generated code
exec(python_code)
```

---

## 📝 GoalLang Language Guide

### Basic Syntax

**Variable Declaration:**
```goal
score x = 10          # Integer variable
distance y = 3.14     # Float variable
player name           # Parameter/local variable
```

**Output:**
```goal
shout "Hello!"                    # Print string
shout result                      # Print variable
shout "Score: " + score           # String concatenation
```

**Input:**
```goal
receive user_input                # Read from stdin
receive player_name               # Store in variable
```

**Main Function:**
```goal
score kickoff:
    # Your code here
    goal 0            # Exit with status
```

**Control Flow:**
```goal
referee condition:                # if statement
    shout "Yes"
offside:                          # else statement
    shout "No"
```

### Complete Example

```goal
score kickoff:
    shout "=== Welcome to GoalLang ==="
    
    shout "Enter your name: "
    receive name
    
    shout "Enter number of goals: "
    receive goals
    
    # Calculate bonus
    score bonus = 10
    score total = goals + bonus
    
    # Display result
    shout "Player: " + name
    shout "Total Score: " + total
    
    # Conditional
    referee total > 50:
        shout "Champion!"
    offside:
        shout "Keep training"
    
    goal 0
```

---

## 🧪 Test Files

The project includes example GoalLang files:

| File | Purpose |
|------|---------|
| `test.goal` | Basic syntax and control flow demo |
| `io_test.goal` | Input/output operations example |
| `goallang_example.goal` | Interactive user input example |

Run them:
```bash
python main.py test.goal
python main.py io_test.goal
```

Or load them in the IDE and click **▶ RUN COMPILER**.

---

## 📊 Compiler Output Example

**Input (`test.goal`):**
```goal
score kickoff:
    score x = 5
    shout "Result: " + x
    goal 0
```

**Generated Python:**
```python
x = 5
print("Result: ", x)
```

---

## 🐛 Error Handling

The compiler provides detailed error messages:

```
[HH:MM:SS] Error: Unexpected token 'xyz' at line 3
```

- Errors are highlighted in the IDE
- Line number is provided for easy debugging
- Symbol table shows scope conflicts

---

## 📁 Project Structure

```
.
├── ide.py                    # GUI IDE application
├── main.py                   # CLI compiler
├── lexer.py                  # Lexical analyzer
├── parser.py                 # Syntax parser
├── analyzer.py               # Semantic analyzer
├── generator.py              # Code generator
├── ast_nodes.py              # AST node definitions
├── test.goal                 # Test example
├── io_test.goal              # I/O example
├── goallang_example.goal     # Interactive example
├── README.md                 # This file
├── LICENSE                   # MIT License
└── .gitignore                # Git ignore rules
```

---

## 🎓 Educational Value

This project demonstrates:
- **Compiler Design** - Complete compilation pipeline
- **Language Theory** - Lexical, syntax, and semantic analysis
- **Data Structures** - AST, symbol tables, token streams
- **Python Programming** - OOP, pattern matching, recursion
- **GUI Development** - tkinter for desktop applications
- **Software Engineering** - Clean code, modular design

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new GoalLang features
- Improve documentation
- Submit pull requests

---

## 📞 Support

For issues or questions:
1. Check the examples in `*.goal` files
2. Review error messages in the IDE Terminal tab
3. Inspect the generated Python code
4. Open an issue on GitHub

---

## 🎉 Get Started Now!

```bash
# Clone and run
git clone https://github.com/Emad-Ahmed6699/Scanner-Compiler-Project.git
cd Scanner-Compiler-Project
python ide.py
```

Happy coding with GoalLang! ⚽✨