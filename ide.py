import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import sys
import io
import threading
import time
import queue
from datetime import datetime
import re

# Import compiler components
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from generator import CodeGenerator

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ASTVisualizer:
    """Custom class to draw the AST graphically on a Canvas"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_radius = 22
        self.v_spacing = 70
        self.colors = {
            "Control": "#f43f5e",    # Rose 500
            "Statement": "#3b82f6",  # Blue 500
            "Literal": "#10b981",    # Emerald 500
            "Variable": "#f59e0b",   # Amber 500
            "Function": "#8b5cf6",   # Violet 500
            "Default": "#475569"     # Slate 600
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
        self._draw_node(node, 1000, 50, 350)
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
                self.canvas.create_line(x, y, child_x, child_y, fill="#334155", width=2, smooth=True)
                self._draw_node(child, child_x, child_y, max(x_offset / 1.8, 50))
        
        # Draw node shadow
        self.canvas.create_oval(x-self.node_radius+2, y-self.node_radius+2, x+self.node_radius+2, y+self.node_radius+2, fill="#000000", outline="", stipple="gray50")
        # Draw node
        self.canvas.create_oval(x-self.node_radius, y-self.node_radius, x+self.node_radius, y+self.node_radius, fill=color, outline="#ffffff", width=2)
        
        clean_name = name.split('(')[0]
        self.canvas.create_text(x, y, text=clean_name, fill="white", font=("Segoe UI", 8, "bold"))

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
            self.create_text(18, y, anchor="n", text=linenum, fill="#4b5563", font=("JetBrains Mono", 10))
            i = self.textwidget.index("%s+1line" % i)

class GoalIDE(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚽ GoalLang IDE - Pro Edition")
        self.geometry("1400x900")
        self.configure(fg_color="#0f172a") # Slate 950
        
        # Window icon/scaling
        try: self.after(0, lambda: self.state('zoomed'))
        except: pass
        
        self.setup_menubar()
        self.setup_ui()
        self.setup_syntax_highlighting()
        
        self.editor.bind("<<Change>>", self.on_content_change)
        self.editor.bind("<Return>", self.handle_auto_indent)
        self.editor.bind("<Key>", self.clear_error_highlight)
        
        # Terminal Interaction State
        self.input_queue = queue.Queue()
        self.is_running = False
        self.console.bind("<Return>", self.handle_terminal_input)

    def setup_menubar(self):
        menubar = tk.Menu(self, bg="#1e293b", fg="white", activebackground="#3b82f6", borderwidth=0)
        file_menu = tk.Menu(menubar, tearoff=0, bg="#1e293b", fg="white", activebackground="#3b82f6")
        file_menu.add_command(label="New File", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export Python", command=self.export_python)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def setup_ui(self):
        # Header / Toolbar
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.header.pack(side=tk.TOP, fill=tk.X)
        
        title_lbl = ctk.CTkLabel(self.header, text="⚽ GOALLANG COMPILER", font=("Segoe UI", 16, "bold"), text_color="#3b82f6")
        title_lbl.pack(side=tk.LEFT, padx=20)
        
        self.btn_run = ctk.CTkButton(self.header, text="▶  RUN COMPILER", command=self.run_code, 
                                    fg_color="#10b981", hover_color="#059669", font=("Segoe UI", 13, "bold"), 
                                    width=160, height=35, corner_radius=8)
        self.btn_run.pack(side=tk.LEFT, padx=15, pady=12)
        
        self.btn_export = ctk.CTkButton(self.header, text="💾  EXPORT PY", command=self.export_python, 
                                       fg_color="#3b82f6", hover_color="#2563eb", font=("Segoe UI", 12, "bold"), 
                                       width=130, height=35, corner_radius=8)
        self.btn_export.pack(side=tk.LEFT, padx=5, pady=12)

        # Main Layout (Sidebar + Editor + Tabs)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paned Window for flexibility
        self.paned = tk.PanedWindow(self.main_container, orient=tk.HORIZONTAL, bg="#0f172a", sashwidth=4, borderwidth=0)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Editor Section
        self.ed_frame = ctk.CTkFrame(self.paned, fg_color="#1e293b", corner_radius=12, border_width=1, border_color="#334155")
        self.paned.add(self.ed_frame, width=700)
        
        ed_title_bar = ctk.CTkFrame(self.ed_frame, height=35, fg_color="#334155", corner_radius=0)
        ed_title_bar.pack(fill=tk.X)
        ctk.CTkLabel(ed_title_bar, text="📄 SOURCE CODE", font=("Segoe UI", 11, "bold"), text_color="#e2e8f0").pack(side=tk.LEFT, padx=15)
        
        ed_content = ctk.CTkFrame(self.ed_frame, fg_color="transparent")
        ed_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.line_nums = LineNumbers(ed_content, width=40, bg="#1e293b", highlightthickness=0)
        self.line_nums.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        
        self.editor = CustomText(ed_content, bg="#1e293b", fg="#e2e8f0", insertbackground="white", 
                                font=("Consolas", 14), undo=True, borderwidth=0, wrap="none",
                                padx=10, pady=10, selectbackground="#3b82f6")
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.line_nums.textwidget = self.editor

        # Output Section (Tabs)
        self.out_frame = ctk.CTkFrame(self.paned, fg_color="transparent")
        self.paned.add(self.out_frame)
        
        self.tabs = ctk.CTkTabview(self.out_frame, fg_color="#1e293b", segmented_button_selected_color="#3b82f6",
                                  segmented_button_unselected_hover_color="#334155", corner_radius=12,
                                  border_width=1, border_color="#334155")
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        tab_list = ["💻 TERMINAL", "📝 OUTPUT", "🐍 PYTHON", "🔍 TOKENS", "📊 SYMBOLS", "🌳 PARSER TREE"]
        for t in tab_list: self.tabs.add(t)

        # Terminal Tab
        self.console = tk.Text(self.tabs.tab("💻 TERMINAL"), bg="#020617", fg="#ffffff", font=("Consolas", 11), 
                              borderwidth=0, padx=15, pady=15)
        self.console.pack(fill=tk.BOTH, expand=True)

        # Output Tab
        self.output_view = tk.Text(self.tabs.tab("📝 OUTPUT"), bg="#020617", fg="#10b981", font=("Consolas", 12, "bold"), 
                                  borderwidth=0, padx=15, pady=15)
        self.output_view.pack(fill=tk.BOTH, expand=True)
        
        # Python Tab
        self.py_view = tk.Text(self.tabs.tab("🐍 PYTHON"), bg="#020617", fg="#80cbc4", font=("Consolas", 11), 
                              state="disabled", borderwidth=0, padx=15, pady=15)
        self.py_view.pack(fill=tk.BOTH, expand=True)
        
        # Tokens Tab
        self.setup_treeview(self.tabs.tab("🔍 TOKENS"), ("Type", "Value", "Line"), "token_tree")
        
        # Symbols Tab
        self.setup_treeview(self.tabs.tab("📊 SYMBOLS"), ("Name", "Type", "Scope", "Line"), "sym_tree")
        
        # AST Tab
        ast_cont = ctk.CTkFrame(self.tabs.tab("🌳 PARSER TREE"), fg_color="#0f172a")
        ast_cont.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal Scrollbar
        self.ast_xscroll = ctk.CTkScrollbar(ast_cont, orientation="horizontal")
        self.ast_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vertical Scrollbar
        self.ast_yscroll = ctk.CTkScrollbar(ast_cont, orientation="vertical")
        self.ast_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ast_canvas = tk.Canvas(ast_cont, bg="#0f172a", highlightthickness=0,
                                   xscrollcommand=self.ast_xscroll.set,
                                   yscrollcommand=self.ast_yscroll.set)
        self.ast_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.ast_xscroll.configure(command=self.ast_canvas.xview)
        self.ast_yscroll.configure(command=self.ast_canvas.yview)
        
        # Mouse wheel support for AST
        self.ast_canvas.bind("<MouseWheel>", lambda e: self.ast_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.ast_canvas.bind("<Shift-MouseWheel>", lambda e: self.ast_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Drag to pan support
        self.ast_canvas.bind("<ButtonPress-1>", lambda e: self.ast_canvas.scan_mark(e.x, e.y))
        self.ast_canvas.bind("<B1-Motion>", lambda e: self.ast_canvas.scan_dragto(e.x, e.y, gain=1))
        
        self.visualizer = ASTVisualizer(self.ast_canvas)

        # Status Bar
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#1e293b")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_lbl = ctk.CTkLabel(self.status_bar, text="Ready", font=("Segoe UI", 10), text_color="#94a3b8")
        self.status_lbl.pack(side=tk.LEFT, padx=20)
        
        # Default code
        self.editor.insert("1.0", "score kickoff:\n    shout \"Hello GoalLang!\"\n    score x = 10\n    score y = 20\n    score result = x + y\n    shout \"The result is: \" + result")

    def setup_treeview(self, parent, columns, attr_name):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#334155", foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[('selected', '#3b82f6')])
        
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for i, col in enumerate(columns):
            tree.heading(f"#{i+1}", text=col)
            tree.column(f"#{i+1}", width=100, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        setattr(self, attr_name, tree)

    def setup_syntax_highlighting(self):
        self.editor.tag_configure("KEYWORD", foreground="#c084fc") # Purple 400
        self.editor.tag_configure("CONTROL", foreground="#60a5fa") # Blue 400
        self.editor.tag_configure("STRING", foreground="#fbbf24")  # Amber 400
        self.editor.tag_configure("COMMENT", foreground="#6b7280") # Gray 500
        self.editor.tag_configure("ERROR_LINE", background="#7f1d1d", foreground="white") # Dark Red background, white text
        self.editor.tag_raise("ERROR_LINE")

    def highlight_syntax(self):
        content = self.editor.get("1.0", tk.END)
        for tag in ["KEYWORD", "CONTROL", "STRING", "COMMENT"]: self.editor.tag_remove(tag, "1.0", tk.END)
        
        patterns = [
            (r'\b(shout|receive|import|assist|player|goal|score|distance|flag)\b', "KEYWORD"),
            (r'\b(kickoff|referee|offside|training|stadium|match)\b', "CONTROL"),
            (r'"[^"\n]*"', "STRING"),
            (r'#.*', "COMMENT")
        ]
        
        for p, t in patterns:
            for m in re.finditer(p, content):
                start = f"1.0 + {m.start()} chars"
                end = f"1.0 + {m.end()} chars"
                self.editor.tag_add(t, start, end)

    def handle_auto_indent(self, event):
        line = self.editor.get("insert linestart", "insert lineend")
        indent = len(line) - len(line.lstrip())
        self.editor.insert("insert", "\n" + " " * indent)
        if line.strip().endswith(":"): self.editor.insert("insert", "    ")
        return "break"

    def clear_error_highlight(self, event=None): self.editor.tag_remove("ERROR_LINE", "1.0", tk.END)
    def on_content_change(self, event=None): self.line_nums.redraw(); self.highlight_syntax()
    
    def log(self, msg, mode="INFO"):
        c = {"INFO": "#3b82f6", "SUCCESS": "#10b981", "ERROR": "#f43f5e", "OUTPUT": "#ffffff"}
        self.append_to_console(f"[{datetime.now().strftime('%H:%M:%S')}] ", "#475569", is_system=True)
        self.append_to_console(msg + "\n", mode, is_system=True)
        self.console.tag_config(mode, foreground=c.get(mode, "white"))
        self.console.tag_config("#475569", foreground="#475569")

    def append_to_console(self, text, tag=None, is_system=False):
        def _append():
            self.console.configure(state="normal")
            self.console.insert(tk.END, text, tag)
            self.console.see(tk.END)
            
            # Smart filtering for Output tab:
            # We only want actual program output (shout results)
            # Skip system logs and input prompts
            is_prompt = any(text.strip().endswith(c) for c in [":", "?", ">"]) or "Enter " in text
            
            if not is_system and not is_prompt:
                self.output_view.configure(state="normal")
                self.output_view.insert(tk.END, text, tag)
                self.output_view.see(tk.END)
            
            if not self.is_running:
                 self.console.configure(state="disabled")
                 self.output_view.configure(state="disabled")
        self.after(0, _append)

    def stop_execution(self):
        if self.is_running:
            self.is_running = False
            self.input_queue.put(None) # Unblock queue.get()
            self.status_lbl.configure(text="Stopped", text_color="#f43f5e")
            self.log("Previous execution stopped.", "ERROR")

    def handle_terminal_input(self, event):
        if not self.is_running: return "break"
        
        line = self.console.get("insert linestart", "insert lineend")
        self.input_queue.put(line + "\n")
        
        # Move cursor to end and add newline
        self.console.insert(tk.END, "\n")
        self.console.see(tk.END)
        return "break"

    def set_waiting_input(self, waiting):
        if waiting:
            self.after(0, lambda: self.status_lbl.configure(text="Waiting for input...", text_color="#fbbf24"))
            self.after(0, lambda: self.console.configure(state="normal"))
            self.after(0, lambda: self.console.focus_set())
        else:
            self.after(0, lambda: self.status_lbl.configure(text="Running...", text_color="#3b82f6"))

    def run_code(self):
        if self.is_running:
            self.stop_execution()
            self.after(100, self.run_code) # Wait a bit and retry
            return

        self.clear_error_highlight()
        code = self.editor.get("1.0", tk.END).strip()
        if not code: return
        
        self.console.configure(state="normal")
        self.console.delete("1.0", tk.END)
        self.output_view.configure(state="normal")
        self.output_view.delete("1.0", tk.END)
        
        self.status_lbl.configure(text="Compiling...", text_color="#fbbf24")
        self.update_idletasks()
        
        try:
            lexer = Lexer(code); tokens = lexer.scan()
            for i in self.token_tree.get_children(): self.token_tree.delete(i)
            for t in tokens: self.token_tree.insert("", tk.END, values=(t['type'], t['value'], t['line']))
            
            parser = Parser(tokens); ast = parser.parse(); self.visualizer.draw(ast)
            
            analyzer = SemanticAnalyzer(); analyzer.visit(ast)
            for i in self.sym_tree.get_children(): self.sym_tree.delete(i)
            for s in analyzer.symbol_table.all_symbols: 
                self.sym_tree.insert("", tk.END, values=(s['name'], s['type'], s['scope_depth'], s['line']))
            
            generator = CodeGenerator(); py_code = generator.generate(ast)
            self.py_view.config(state="normal"); self.py_view.delete("1.0", tk.END); self.py_view.insert("1.0", py_code); self.py_view.config(state="disabled")
            
            self.log("Compile Successful!", "SUCCESS")
            
            # Switch to Terminal Tab for execution
            self.tabs.set("💻 TERMINAL")
            self.is_running = True
            
            # Start execution thread
            threading.Thread(target=self.execute_thread, args=(py_code,), daemon=True).start()
            
        except Exception as e:
            msg = str(e); self.log(msg, "ERROR")
            self.status_lbl.configure(text="Error", text_color="#f43f5e")
            match = re.search(r"line (\d+)", msg)
            if match:
                line = match.group(1)
                self.editor.tag_add("ERROR_LINE", f"{line}.0", f"{line}.end")
                self.editor.tag_raise("ERROR_LINE")
                self.editor.mark_set("insert", f"{line}.0")
                self.editor.see(f"{line}.0")
                self.editor.focus_set()

    def execute_thread(self, py_code):
        class TerminalIO:
            def __init__(self, app): self.app = app
            def write(self, s):
                if not self.app.is_running: raise SystemExit()
                self.app.append_to_console(s)
            def flush(self): pass
            def readline(self):
                self.app.set_waiting_input(True)
                val = self.app.input_queue.get()
                if not self.app.is_running: raise SystemExit()
                self.app.set_waiting_input(False)
                return val

        old_stdout, old_stdin = sys.stdout, sys.stdin
        sys.stdout = sys.stderr = TerminalIO(self)
        sys.stdin = TerminalIO(self)
        
        try:
            # Use a wrapper for input that strips the trailing newline, matching standard input() behavior
            exec(py_code, {"__name__": "__main__", "input": lambda prompt="": sys.stdin.readline().rstrip('\n')})
            if self.is_running:
                self.after(0, lambda: self.status_lbl.configure(text="Ready", text_color="#94a3b8"))
                self.log("Execution Finished", "SUCCESS")
        except SystemExit:
            pass # Stopped by user
        except Exception as e:
            if self.is_running:
                self.append_to_console(f"\nRuntime Error:\n{str(e)}\n", "ERROR", is_system=True)
                self.after(0, lambda: self.status_lbl.configure(text="Runtime Error", text_color="#f43f5e"))
                match = re.search(r"line (\d+)", str(e))
                if match:
                    line = match.group(1)
                    self.after(0, lambda: self.editor.tag_add("ERROR_LINE", f"{line}.0", f"{line}.end"))
                    self.after(0, lambda: self.editor.tag_raise("ERROR_LINE"))
                    self.after(0, lambda: self.editor.mark_set("insert", f"{line}.0"))
                    self.after(0, lambda: self.editor.see(f"{line}.0"))
        finally:
            sys.stdout, sys.stdin = old_stdout, old_stdin
            self.is_running = False
            self.after(0, lambda: self.console.configure(state="disabled"))
            self.after(0, lambda: self.output_view.configure(state="disabled"))
            # Automatically switch back to OUTPUT tab when finished
            self.after(200, lambda: self.tabs.set("📝 OUTPUT"))

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
    app = GoalIDE()
    app.mainloop()
