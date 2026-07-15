#!/usr/bin/env python3
"""
MX Language — Main Entry Point
Usage:
    python mx.py                  → Start REPL
    python mx.py script.mx        → Run a .mx file
    python mx.py -c "code here"   → Run inline code
"""

import sys
import os
import traceback

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, RuntimeError_

BANNER = r"""
  __  ____  __  _
 |  \/  \ \/ / | |    __ _ _ __   __ _ _   _  __ _  __ _  ___
 | |\/| |\  /  | |   / _` | '_ \ / _` | | | |/ _` |/ _` |/ _ \
 | |  | |/  \  | |__| (_| | | | | (_| | |_| | (_| | (_| |  __/
 |_|  |_/_/\_\ |_____\__,_|_| |_|\__, |\__,_|\__,_|\__, |\___|
                                   |___/             |___/
 MX Language v1.0  |  Type 'exit' to quit, 'help' for commands
"""

HELP_TEXT = """
MX Language Quick Reference
─────────────────────────────────────────────────
Variables:    let x = 10         const PI = 3.14
Types:        int  float  str  bool  void
Functions:    fn add(a: int, b: int) -> int { return a + b }
If/Else:      if x > 0 { print("pos") } else { print("neg") }
While:        while x > 0 { x -= 1 }
For loop:     for i in range(10) { print(i) }
Arrays:       let arr = [1, 2, 3]   arr.push(4)
Structs:      struct Point { x: int  y: int }
              let p = new Point { x: 10, y: 20 }
Import:       import math   (gives: sin, cos, sqrt, PI ...)
Comments:     // single line   /* multi line */   # hash style
─────────────────────────────────────────────────
Builtins: print  input  len  type  int  float  str  bool
          range  push  pop  append  contains  sqrt  abs
          max  min  floor  ceil  round  exit
"""


def run_source(source: str, interpreter: Interpreter, filename="<input>"):
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter.run(ast)
        return True
    except LexerError as e:
        print(f"\n{e}", file=sys.stderr)
    except ParseError as e:
        print(f"\n{e}", file=sys.stderr)
    except RuntimeError_ as e:
        print(f"\n{e}", file=sys.stderr)
    except SystemExit:
        raise
    except Exception as e:
        print(f"\n[Internal Error] {e}", file=sys.stderr)
        if os.getenv("MX_DEBUG"):
            traceback.print_exc()
    return False


def run_file(path: str):
    if not os.path.exists(path):
        print(f"[Error] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    interpreter = Interpreter()
    ok = run_source(source, interpreter, filename=path)
    if not ok:
        sys.exit(1)


def run_repl():
    print(BANNER)
    interpreter = Interpreter()
    buf = []
    depth = 0  # brace depth for multi-line input

    while True:
        prompt = "mx> " if depth == 0 else "... "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        stripped = line.strip()

        # REPL commands
        if depth == 0 and stripped in ('exit', 'quit', 'q'):
            print("Bye!")
            break
        if depth == 0 and stripped == 'help':
            print(HELP_TEXT)
            continue
        if depth == 0 and stripped == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        buf.append(line)
        depth += line.count('{') - line.count('}')
        depth = max(0, depth)

        if depth == 0:
            source = '\n'.join(buf)
            buf.clear()
            if source.strip():
                run_source(source, interpreter, "<repl>")


def main():
    args = sys.argv[1:]

    if not args:
        run_repl()
    elif args[0] == '-c' and len(args) >= 2:
        interp = Interpreter()
        run_source(args[1], interp)
    elif args[0] in ('-h', '--help'):
        print(HELP_TEXT)
    else:
        run_file(args[0])


if __name__ == '__main__':
    main()
