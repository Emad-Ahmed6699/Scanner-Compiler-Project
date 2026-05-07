import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import io
import threading
import time
from datetime import datetime
import re

# Import compiler components
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from generator import CodeGenerator

class ASTVisualizer:
    """Custom class to draw the AST graphically on a Canvas"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_radius = 18
        self.v_spacing = 60
        self.colors = {
            "Control": "#d13438",
            "Statement": "#007acc",
            "Literal": "#28a745",
            "Variable": "#ce9178",
            "Function": "#c586c0",
            "Default": "#333333"
        }

    def get_node_color(self, name):
        if any(x in name for x in ["If", "While", "For", "Kickoff", "Import", "Stadium"]): return self.colors["Control"]
        if "Literal" in name: return self.colors["Literal"]
        if "Assign" in name or "Declare" in name or "FunctionDef" in name: return self.colors["Function"]
        if "Var" in name: return self.colors["Variable"]
        return self.colors["Statement"]

    def draw(self, node):
        self.canvas.delete("all")
        if not node: return
        self._draw_node(node, 1000, 40, 300)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _draw_node(self, node, x, y, x_offset):
        name = node.get_name()
        color = self.get_node_color(name)
        children = [c for c in node.get_children() if c]
        if children:
            num_children = len(children)
            start_x = x - (x_offset * (num_children - 1) / 2)
            for i, child in enumerate(children):
                child_x = start_x + (i * x_offset)
                child_y = y + self.v_spacing
                self.canvas.create_line(x, y, child_x, child_y, fill="#444444", width=1)
                self._draw_node(child, child_x, child_y, max(x_offset / 1.9, 40))
        self.canvas.create_oval(x-self.node_radius, y-self.node_radius, x+self.node_radius, y+self.node_radius, fill=color, outline="#ffffff", width=1)
        clean_name = name.split('(')[0]
        self.canvas.create_text(x, y, text=clean_name, fill="white", font=("Segoe UI", 7, "bold"))

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
    def _proxy(self, *args):
        try:
            cmd = (self._orig,) + args
            result = self.tk.call(cmd)
            if (args[0] in ("insert", "replace", "delete") or args[0:3] == ("mark", "set", "insert") or args[0:2] == ("xview", "moveto") or args[0:2] == ("yview", "moveto")):
                self.event_generate("<<Change>>", when="tail")
            return result
        except Exception: return None

class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
    def redraw(self, *args):
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(18, y, anchor="n", text=linenum, fill="#858585", font=("Consolas", 10))
            i = self.textwidget.index("%s+1line" % i)

class GoalIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("⚽ GoalLang IDE - Pro Compiler")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")
        self.setup_styles()
        self.setup_menubar()
        self.setup_ui()
        self.setup_syntax_highlighting()
        self.editor.bind("<<Change>>", self.on_content_change)
        self.editor.bind("<Return>", self.handle_auto_indent)
        self.editor.bind("<Key>", self.clear_error_highlight)

    def setup_styles(self):
        style = ttk.Style(); style.theme_use("clam")
        style.configure("TNotebook", background="#2d2d2d", borderwidth=0)
        style.configure("TNotebook.Tab", background="#333333", foreground="#d4d4d4", padding=[12, 4])
        style.map("TNotebook.Tab", background=[("selected", "#1e1e1e")], foreground=[("selected", "#007acc")])
        style.configure("Treeview", background="#252526", foreground="white", fieldbackground="#252526", borderwidth=0)
        style.configure("Treeview.Heading", background="#333333", foreground="white", font=("Segoe UI", 9, "bold"))

    def setup_menubar(self):
        menubar = tk.Menu(self.root, bg="#333333", fg="white")
        file_menu = tk.Menu(menubar, tearoff=0, bg="#333333", fg="white")
        file_menu.add_command(label="New File", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export Python", command=self.export_python)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

    def setup_ui(self):
        toolbar = tk.Frame(self.root, bg="#2d2d2d", height=45)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self.btn_run = tk.Button(toolbar, text=" ▶ RUN COMPILER ", command=self.run_code, bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15)
        self.btn_run.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(toolbar, text=" 💾 EXPORT PY ", command=self.export_python, bg="#007acc", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#2d2d2d", sashwidth=4)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        ed_cont = tk.Frame(self.main_pane, bg="#1e1e1e"); self.main_pane.add(ed_cont, width=650)
        tk.Label(ed_cont, text=" ⚽ GOALLANG SOURCE", bg="#2d2d2d", fg="#007acc", font=("Segoe UI", 10, "bold"), pady=5).pack(fill=tk.X)
        ed_sub = tk.Frame(ed_cont, bg="#1e1e1e"); ed_sub.pack(fill=tk.BOTH, expand=True)
        self.line_nums = LineNumbers(ed_sub, width=35, bg="#1e1e1e", highlightthickness=0); self.line_nums.pack(side=tk.LEFT, fill=tk.Y)
        self.editor = CustomText(ed_sub, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Consolas", 13), undo=True, borderwidth=0, wrap="none")
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); self.line_nums.textwidget = self.editor
        self.tabs = ttk.Notebook(self.main_pane); self.main_pane.add(self.tabs)
        self.console = tk.Text(self.tabs, bg="#000000", fg="#ffffff", font=("Consolas", 11), borderwidth=0); self.tabs.add(self.console, text=" 💻 TERMINAL ")
        self.py_view = tk.Text(self.tabs, bg="#1e1e1e", fg="#80cbc4", font=("Consolas", 11), state="disabled", borderwidth=0); self.tabs.add(self.py_view, text=" 🐍 PYTHON ")
        tk_fr = tk.Frame(self.tabs); self.tabs.add(tk_fr, text=" 🔍 TOKENS ")
        self.token_tree = ttk.Treeview(tk_fr, columns=("T", "V", "L"), show="headings")
        for c, h in zip(("T", "V", "L"), ("Type", "Value", "Line")): self.token_tree.heading(c, text=h)
        self.token_tree.pack(fill=tk.BOTH, expand=True)
        sym_fr = tk.Frame(self.tabs); self.tabs.add(sym_fr, text=" 📊 SYMBOLS ")
        self.sym_tree = ttk.Treeview(sym_fr, columns=("N", "T", "S", "L"), show="headings")
        for c, h in zip(("N", "T", "S", "L"), ("Name", "Type", "Scope", "Line")): self.sym_tree.heading(c, text=h)
        self.sym_tree.pack(fill=tk.BOTH, expand=True)
        ast_fr = tk.Frame(self.tabs, bg="#1e1e1e"); self.tabs.add(ast_fr, text=" 🌳 PARSER TREE ")
        sx = tk.Scrollbar(ast_fr, orient=tk.HORIZONTAL); sx.pack(side=tk.BOTTOM, fill=tk.X)
        sy = tk.Scrollbar(ast_fr, orient=tk.VERTICAL); sy.pack(side=tk.RIGHT, fill=tk.Y)
        self.ast_canvas = tk.Canvas(ast_fr, bg="#1e1e1e", highlightthickness=0, xscrollcommand=sx.set, yscrollcommand=sy.set); self.ast_canvas.pack(fill=tk.BOTH, expand=True)
        sx.config(command=self.ast_canvas.xview); sy.config(command=self.ast_canvas.yview); self.visualizer = ASTVisualizer(self.ast_canvas)
        self.editor.insert("1.0", "score kickoff:\n    shout \"Hello GoalLang!\"\n    score x = 10\n    score y = 20\n    score result = x + y\n    shout \"The result is: \" + result")

    def setup_syntax_highlighting(self):
        self.editor.tag_configure("KEYWORD", foreground="#c586c0")
        self.editor.tag_configure("CONTROL", foreground="#569cd6")
        self.editor.tag_configure("ERROR_LINE", background="#4b1d1d")

    def highlight_syntax(self):
        content = self.editor.get("1.0", tk.END)
        for tag in ["KEYWORD", "CONTROL"]: self.editor.tag_remove(tag, "1.0", tk.END)
        # Added new keywords to highlighter
        kw_p = r'\b(shout|receive|import|assist|player|goal|score|distance|flag)\b'
        ct_p = r'\b(kickoff|referee|offside|training|stadium|match)\b'
        for p, t in [(kw_p, "KEYWORD"), (ct_p, "CONTROL")]:
            for m in re.finditer(p, content): self.editor.tag_add(t, f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

    def handle_auto_indent(self, event):
        line = self.editor.get("insert linestart", "insert lineend")
        indent = len(line) - len(line.lstrip())
        self.editor.insert("insert", "\n" + " " * indent)
        if line.strip().endswith(":"): self.editor.insert("insert", "    ")
        return "break"
    def clear_error_highlight(self, event=None): self.editor.tag_remove("ERROR_LINE", "1.0", tk.END)
    def on_content_change(self, event=None): self.line_nums.redraw(); self.highlight_syntax()
    def log(self, msg, mode="INFO"):
        c = {"INFO": "#00d1ff", "SUCCESS": "#28a745", "ERROR": "#ff3333", "OUTPUT": "#ffffff"}
        self.console.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] ", "#666666")
        self.console.insert(tk.END, msg + "\n", mode)
        self.console.tag_config(mode, foreground=c.get(mode, "white")); self.console.see(tk.END)

    def run_code(self):
        self.clear_error_highlight()
        code = self.editor.get("1.0", tk.END).strip()
        if not code: return
        self.console.delete("1.0", tk.END)
        try:
            lexer = Lexer(code); tokens = lexer.scan()
            for i in self.token_tree.get_children(): self.token_tree.delete(i)
            for t in tokens: self.token_tree.insert("", tk.END, values=(t['type'], t['value'], t['line']))
            parser = Parser(tokens); ast = parser.parse(); self.visualizer.draw(ast)
            analyzer = SemanticAnalyzer(); analyzer.visit(ast)
            for i in self.sym_tree.get_children(): self.sym_tree.delete(i)
            for s in analyzer.symbol_table.all_symbols: self.sym_tree.insert("", tk.END, values=(s['name'], s['type'], s['scope_depth'], s['line']))
            generator = CodeGenerator(); py_code = generator.generate(ast)
            self.py_view.config(state="normal"); self.py_view.delete("1.0", tk.END); self.py_view.insert("1.0", py_code); self.py_view.config(state="disabled")
            self.log("Compile Successful!", "SUCCESS"); exec_out = io.StringIO(); sys.stdout = exec_out
            exec(py_code, {}); sys.stdout = sys.__stdout__; self.log(exec_out.getvalue(), "OUTPUT")
        except Exception as e:
            msg = str(e); self.log(msg, "ERROR")
            match = re.search(r"line (\d+)", msg)
            if match:
                line = match.group(1); self.editor.tag_add("ERROR_LINE", f"{line}.0", f"{line}.end"); self.editor.see(f"{line}.0")

    def export_python(self):
        code = self.py_view.get("1.0", tk.END).strip()
        if not code: return messagebox.showwarning("Warning", "No Python code generated yet!")
        path = filedialog.asksaveasfilename(defaultextension=".py")
        if path:
            with open(path, "w") as f: f.write(code)
            messagebox.showinfo("Success", f"Exported to {path}")
    def new_file(self): self.editor.delete("1.0", tk.END)
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("GoalLang Files", "*.goal"), ("All Files", "*.*")])
        if path:
            with open(path, "r") as f: self.editor.delete("1.0", tk.END); self.editor.insert("1.0", f.read())
            self.on_content_change()
    def save_file(self):
        path = filedialog.asksaveasfilename(filetypes=[("GoalLang Files", "*.goal")], defaultextension=".goal")
        if path:
            with open(path, "w") as f: f.write(self.editor.get("1.0", tk.END))

if __name__ == "__main__":
    root = tk.Tk(); app = GoalIDE(root); root.mainloop()
