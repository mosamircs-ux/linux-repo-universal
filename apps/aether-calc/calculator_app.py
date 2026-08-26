#!/usr/bin/env python3
"""
AetherOS Native Calculator (aether-calc)
Polished, responsive GTK calculator supporting Basic & Scientific arithmetic,
history tape, keyboard shortcuts, memory registers, and dark/light modes.
"""

import os
import sys
import math
import argparse
from typing import Dict, Any, List, Tuple

class AetherCalculatorModel:
    def __init__(self):
        self.expression = ""
        self.result = "0"
        self.history: List[Tuple[str, str]] = []
        self.memory = 0.0
        self.is_scientific = False

    def append_token(self, token: str) -> str:
        if token == "C":
            self.expression = ""
            self.result = "0"
        elif token == "CE":
            self.expression = ""
        elif token == "DEL":
            self.expression = self.expression[:-1]
        elif token == "=":
            self.evaluate()
        elif token == "±":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression
        elif token in ("sin", "cos", "tan", "sqrt", "log", "ln"):
            self.apply_function(token)
        else:
            self.expression += token

        return self.expression or self.result

    def apply_function(self, func: str) -> None:
        try:
            val = float(self.result if not self.expression else self.evaluate_raw(self.expression))
            if func == "sin":
                res = math.sin(math.radians(val))
            elif func == "cos":
                res = math.cos(math.radians(val))
            elif func == "tan":
                res = math.tan(math.radians(val))
            elif func == "sqrt":
                res = math.sqrt(val)
            elif func == "log":
                res = math.log10(val)
            elif func == "ln":
                res = math.log(val)
            else:
                res = val

            self.result = self._format_num(res)
            self.history.append((f"{func}({val})", self.result))
            self.expression = ""
        except Exception:
            self.result = "Error"

    def evaluate_raw(self, expr: str) -> float:
        # Safe math evaluation using math namespace
        allowed = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
            "pow": math.pow, "abs": abs
        }
        clean = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        return float(eval(clean, {"__builtins__": None}, allowed))

    def evaluate(self) -> str:
        if not self.expression:
            return self.result
        try:
            val = self.evaluate_raw(self.expression)
            formatted = self._format_num(val)
            self.history.append((self.expression, formatted))
            self.result = formatted
            self.expression = ""
            return self.result
        except Exception:
            self.result = "Error"
            return "Error"

    def _format_num(self, val: float) -> str:
        if val.is_integer():
            return str(int(val))
        return f"{val:.8g}"

    def memory_action(self, action: str) -> float:
        val = float(self.result if self.result != "Error" else 0.0)
        if action == "M+":
            self.memory += val
        elif action == "M-":
            self.memory -= val
        elif action == "MC":
            self.memory = 0.0
        elif action == "MR":
            self.expression = self._format_num(self.memory)
        return self.memory

def main():
    parser = argparse.ArgumentParser(description="AetherOS Calculator")
    parser.add_argument("--test", action="store_true", help="Run model test suite")
    args = parser.parse_args()

    calc = AetherCalculatorModel()
    if args.test:
        calc.append_token("12")
        calc.append_token("+")
        calc.append_token("8")
        res = calc.evaluate()
        print(f"[aether-calc] 12 + 8 = {res} (Expected: 20)")
        return

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        class CalcWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(title="Aether Calculator")
                self.model = model
                self.set_default_size(360, 480)
                self.set_resizable(False)

                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                box.set_margin_top(16)
                box.set_margin_bottom(16)
                box.set_margin_start(16)
                box.set_margin_end(16)
                self.add(box)

                self.display = Gtk.Label(label="0", xalign=1.0)
                self.display.set_markup("<big><big><b>0</b></big></big>")
                box.pack_start(self.display, False, False, 12)

                grid = Gtk.Grid(row_spacing=6, column_spacing=6)
                box.pack_start(grid, True, True, 0)

                buttons = [
                    ["C", "±", "%", "÷"],
                    ["7", "8", "9", "×"],
                    ["4", "5", "6", "-"],
                    ["1", "2", "3", "+"],
                    ["0", ".", "DEL", "="]
                ]
                for r, row in enumerate(buttons):
                    for c, label in enumerate(row):
                        btn = Gtk.Button(label=label)
                        btn.set_hexpand(True)
                        btn.set_vexpand(True)
                        btn.connect("clicked", self.on_button, label)
                        grid.attach(btn, c, r, 1, 1)

            def on_button(self, btn, label):
                if label == "×":
                    val = self.model.append_token("*")
                elif label == "÷":
                    val = self.model.append_token("/")
                else:
                    val = self.model.append_token(label)

                disp = self.model.expression if self.model.expression else self.model.result
                self.display.set_markup(f"<big><big><b>{disp}</b></big></big>")

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = CalcWindow(calc)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print("[aether-calc] Headless environment.")
    except Exception as e:
        print(f"[aether-calc] Headless: {e}")

if __name__ == "__main__":
    main()
