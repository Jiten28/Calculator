import tkinter as tk
import math

# ── Colour palette ──────────────────────────────────────────────
BG        = "#1a1a2e"
DISPLAY_BG= "#16213e"
BTN_NUM   = "#0f3460"
BTN_OP    = "#e94560"
BTN_SPEC  = "#533483"
BTN_EQUAL = "#e94560"
BTN_CLEAR = "#c84b31"
FG        = "#eaeaea"
FG_OP     = "#ffffff"
FONT_DISP = ("Courier New", 28, "bold")
FONT_BTN  = ("Courier New", 14, "bold")
FONT_HIST = ("Courier New", 10)

class Calculator:
    def __init__(self, root):
        root.title("Calculator")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.expression = ""   # what's being built
        self.just_evaluated = False

        # ── Display ──────────────────────────────────────────────
        disp_frame = tk.Frame(root, bg=DISPLAY_BG, bd=0)
        disp_frame.grid(row=0, column=0, columnspan=4,
                        padx=12, pady=(12, 4), sticky="ew")

        self.expr_var = tk.StringVar(value="")
        self.res_var  = tk.StringVar(value="0")

        tk.Label(disp_frame, textvariable=self.expr_var,
                 font=("Courier New", 11), bg=DISPLAY_BG,
                 fg="#888", anchor="e", width=22
                 ).pack(padx=10, pady=(8, 0), anchor="e")

        tk.Label(disp_frame, textvariable=self.res_var,
                 font=FONT_DISP, bg=DISPLAY_BG,
                 fg=FG, anchor="e", width=16
                 ).pack(padx=10, pady=(0, 10), anchor="e")

        # ── Button layout ────────────────────────────────────────
        # (label, col, row, colspan, bg, command)
        buttons = [
            # Row 1 – clear / special
            ("C",    0, 1, 1, BTN_CLEAR, self.clear),
            ("⌫",   1, 1, 1, BTN_SPEC,  self.backspace),
            ("%",    2, 1, 1, BTN_OP,    lambda: self.append("%")),
            ("÷",    3, 1, 1, BTN_OP,    lambda: self.append("/")),
            # Row 2
            ("7",    0, 2, 1, BTN_NUM,   lambda: self.append("7")),
            ("8",    1, 2, 1, BTN_NUM,   lambda: self.append("8")),
            ("9",    2, 2, 1, BTN_NUM,   lambda: self.append("9")),
            ("×",    3, 2, 1, BTN_OP,    lambda: self.append("*")),
            # Row 3
            ("4",    0, 3, 1, BTN_NUM,   lambda: self.append("4")),
            ("5",    1, 3, 1, BTN_NUM,   lambda: self.append("5")),
            ("6",    2, 3, 1, BTN_NUM,   lambda: self.append("6")),
            ("−",    3, 3, 1, BTN_OP,    lambda: self.append("-")),
            # Row 4
            ("1",    0, 4, 1, BTN_NUM,   lambda: self.append("1")),
            ("2",    1, 4, 1, BTN_NUM,   lambda: self.append("2")),
            ("3",    2, 4, 1, BTN_NUM,   lambda: self.append("3")),
            ("+",    3, 4, 1, BTN_OP,    lambda: self.append("+")),
            # Row 5
            ("0",    0, 5, 1, BTN_NUM,   lambda: self.append("0")),
            (".",    1, 5, 1, BTN_NUM,   lambda: self.append(".")),
            ("xʸ",  2, 5, 1, BTN_SPEC,  lambda: self.append("**")),
            ("=",    3, 5, 1, BTN_EQUAL, self.evaluate),
            # Row 6 – wide special buttons
            ("√x",  0, 6, 2, BTN_SPEC,  self.sqrt),
            ("( )",  2, 6, 2, BTN_SPEC,  self.paren),
        ]

        for (label, col, row, cs, bg, cmd) in buttons:
            self._make_button(root, label, col, row, cs, bg, cmd)

        # keyboard bindings
        root.bind("<Key>", self.key_press)

    # ── Button factory ───────────────────────────────────────────
    def _make_button(self, root, label, col, row, cs, bg, cmd):
        btn = tk.Button(
            root, text=label, font=FONT_BTN,
            bg=bg, fg=FG_OP, activebackground="#ffffff",
            activeforeground="#000000", relief="flat",
            bd=0, padx=0, pady=12, cursor="hand2",
            command=cmd
        )
        btn.grid(row=row, column=col, columnspan=cs,
                 padx=4, pady=4, sticky="nsew")
        # hover effect
        btn.bind("<Enter>", lambda e, b=btn, c=bg: b.config(bg=self._lighten(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        # make columns/rows expand evenly
        for c in range(4):
            root.columnconfigure(c, weight=1)
        for r in range(1, 7):
            root.rowconfigure(r, weight=1)

    def _lighten(self, hex_color):
        """Return a slightly brighter version of a hex colour."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = min(r+40, 255), min(g+40, 255), min(b+40, 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Core logic ───────────────────────────────────────────────
    def append(self, char):
        if self.just_evaluated:
            # start fresh after = unless it's an operator
            if char not in "+-*/**%":
                self.expression = ""
            self.just_evaluated = False
        self.expression += char
        self.expr_var.set(self._pretty(self.expression))
        self.res_var.set(self._pretty(self.expression))

    def clear(self):
        self.expression = ""
        self.expr_var.set("")
        self.res_var.set("0")
        self.just_evaluated = False

    def backspace(self):
        self.expression = self.expression[:-1]
        self.expr_var.set(self._pretty(self.expression))
        self.res_var.set(self._pretty(self.expression) or "0")

    def evaluate(self):
        if not self.expression:
            return
        try:
            raw = self.expression
            # safety: only allow digits and safe operators
            result = eval(raw, {"__builtins__": {}}, {})
            # clean up float display
            if isinstance(result, float) and result == int(result):
                result = int(result)
            self.expr_var.set(self._pretty(raw) + " =")
            self.res_var.set(str(result))
            self.expression = str(result)
            self.just_evaluated = True
        except ZeroDivisionError:
            self.res_var.set("÷ 0 Error")
            self.expression = ""
        except Exception:
            self.res_var.set("Error")
            self.expression = ""

    def sqrt(self):
        if not self.expression:
            return
        try:
            val = eval(self.expression, {"__builtins__": {}}, {})
            if val < 0:
                self.res_var.set("No real root")
                return
            result = math.sqrt(val)
            if result == int(result):
                result = int(result)
            self.expr_var.set(f"√({self._pretty(self.expression)}) =")
            self.res_var.set(str(result))
            self.expression = str(result)
            self.just_evaluated = True
        except Exception:
            self.res_var.set("Error")

    def paren(self):
        # smart parenthesis: open if unbalanced, else close
        opens  = self.expression.count("(")
        closes = self.expression.count(")")
        if opens == closes:
            self.append("(")
        else:
            self.append(")")

    # ── Keyboard support ─────────────────────────────────────────
    def key_press(self, event):
        k = event.char
        if k in "0123456789.+-*/%()":
            self.append(k)
        elif k == "\r" or k == "=":
            self.evaluate()
        elif k == "\x08":           # Backspace
            self.backspace()
        elif k.lower() == "c":
            self.clear()
        elif k == "^":
            self.append("**")

    # ── Helpers ──────────────────────────────────────────────────
    def _pretty(self, expr):
        return (expr
                .replace("**", "^")
                .replace("*",  "×")
                .replace("/",  "÷")
                .replace("-",  "−"))


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()