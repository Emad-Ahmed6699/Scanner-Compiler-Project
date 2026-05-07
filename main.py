import sys
import os
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from generator import CodeGenerator

def compile_goal(source_file):
    if not os.path.exists(source_file):
        print(f"❌ Error: File '{source_file}' not found.")
        return

    with open(source_file, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        # 1. Lexical Analysis
        lexer = Lexer(code)
        tokens = lexer.scan()
        
        # 2. Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()
        
        # 3. Semantic Analysis
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        
        # 4. Code Generation
        generator = CodeGenerator()
        python_code = generator.generate(ast)
        
        # Output results
        output_file = source_file.replace('.goal', '.py')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
            
        print(f"Compilation Successful!")
        print(f"Generated Python code saved to: {output_file}")
        
        # Suggest running the code
        print("\n--- Execution Result ---")
        exec(python_code, {"__name__": "__main__"})
        
    except Exception as e:
        print(f"\nCompilation Error: {str(e)}")

if __name__ == "__main__":
    target = "test.goal"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    
    print(f"--- GoalLang Compiler (Senior Version) ---")
    print(f"Compiling {target}...\n")
    compile_goal(target)