# MX Language — Official Specification v1.0

MX is a statically-typed, expression-oriented programming language with
Python-like readability and C-like structure. It features C-style `{}`
blocks, Rust-inspired `fn`/`let`/`->` syntax, and Python-style `and/or/not`.

---

## File Extension

`.mx`

---

## Running MX Programs

```
python mx.py                     # Start REPL
python mx.py script.mx           # Run a file
python mx.py -c "print(1 + 2)"  # Inline execution
```

---

## Syntax Reference

### Variables

```mx
let x = 10              // inferred type
let name: str = "Alice" // explicit type
const MAX: int = 100    // immutable constant
```

### Types

| Type    | Example          |
|---------|-----------------|
| `int`   | `42`, `-7`      |
| `float` | `3.14`, `-0.5`  |
| `str`   | `"hello"`       |
| `bool`  | `true`, `false` |
| `void`  | (return type)   |
| array   | `[1, 2, 3]`     |
| struct  | `new Point {...}`|

### Functions

```mx
fn add(a: int, b: int) -> int {
    return a + b
}

// Default parameters
fn greet(name: str, greeting: str = "Hello") -> str {
    return greeting + ", " + name + "!"
}

// Void function
fn log(msg: str) {
    print("[LOG]", msg)
}
```

### Operators

```mx
// Arithmetic
+  -  *  /  %  **       // ** = power

// Comparison
==  !=  <  >  <=  >=

// Logical
and  or  not             // also: &&  ||  !

// Assignment
=  +=  -=  *=  /=
```

### Control Flow

```mx
// If / else if / else
if x > 0 {
    print("positive")
} else if x < 0 {
    print("negative")
} else {
    print("zero")
}

// While loop
while x > 0 {
    x -= 1
}

// For loop
for i in range(10) {
    print(i)
}

for item in my_array {
    print(item)
}

// Break & continue
while true {
    if done { break }
    if skip { continue }
}
```

### Arrays

```mx
let nums = [1, 2, 3, 4, 5]

// Access
nums[0]           // → 1

// Methods
nums.push(6)      // append
nums.pop()        // remove last
nums.length       // → 6
nums.reverse()    // in-place
nums.join(", ")   // → "1, 2, 3, 4, 5"
nums.slice(1, 3)  // → [2, 3]
nums.first        // → 1
nums.last         // → 5
nums.contains(3)  // → true

// Range shorthand
let r = [0..10]   // → [0, 1, 2, ..., 9]
```

### Strings

```mx
let s = "Hello, World!"
s.length           // → 13
s.upper()          // → "HELLO, WORLD!"
s.lower()          // → "hello, world!"
s.split(", ")      // → ["Hello", "World!"]
s.trim()           // strip whitespace
s.contains("ell")  // → true
s.starts_with("He")// → true
s.ends_with("!")   // → true
s.replace("o","0") // → "Hell0, W0rld!"
s.to_int()         // parse as int
s.to_float()       // parse as float
```

### Structs

```mx
struct Point {
    x: float
    y: float
}

let p = new Point { x: 3.0, y: 4.0 }
print(p.x)          // → 3.0
p.y = 10.0          // field assignment
```

### Comments

```mx
// Single-line comment
# Python-style comment
/* Multi-line
   comment */
```

### Import

```mx
import math

// Gives access to: sin, cos, tan, sqrt, log, pow, floor, ceil, PI, E
print(sin(PI / 2))  // → 1.0
```

---

## Built-in Functions

| Function        | Description                         |
|----------------|-------------------------------------|
| `print(...)`   | Print values with spaces            |
| `input(prompt)`| Read line from user                 |
| `len(x)`       | Length of array or string           |
| `type(x)`      | Type name as string                 |
| `int(x)`       | Convert to integer                  |
| `float(x)`     | Convert to float                    |
| `str(x)`       | Convert to string                   |
| `bool(x)`      | Convert to bool                     |
| `range(n)`     | Array `[0, 1, ..., n-1]`           |
| `range(s,e)`   | Array `[s, s+1, ..., e-1]`         |
| `range(s,e,step)` | Stepped range                   |
| `push(arr, v)` | Append to array                     |
| `pop(arr)`     | Remove + return last element        |
| `append(arr,v)`| Append, return array                |
| `contains(a,v)`| Check membership                    |
| `sqrt(x)`      | Square root                         |
| `abs(x)`       | Absolute value                      |
| `max(...)`     | Maximum value                       |
| `min(...)`     | Minimum value                       |
| `floor(x)`     | Floor                               |
| `ceil(x)`      | Ceiling                             |
| `round(x, n)`  | Round to n decimal places           |
| `exit(code)`   | Exit program                        |

---

## REPL Commands

```
help    — Show quick reference
clear   — Clear the screen
exit    — Quit the REPL
```

---

## Architecture

```
source.mx
    │
    ▼
 Lexer (lexer.py)
    │  Tokenizes source into Token stream
    ▼
 Parser (parser.py)
    │  Recursive-descent parser → AST
    ▼
 AST Nodes (ast_nodes.py)
    │  Typed dataclasses for every construct
    ▼
 Interpreter (interpreter.py)
    │  Tree-walking interpreter
    │  Scoped Environments (closures)
    │  Built-in functions & modules
    ▼
  Output
```

---

## Error Handling

MX gives precise error messages with line and column numbers:

```
[Lexer Error]   Line 3, Col 5: Unexpected character: '@'
[Parse Error]   Line 7, Col 12: Expected '}', got EOF
[Runtime Error] Division by zero
[Runtime Error] Undefined variable: 'x'
[Runtime Error] Index 5 out of bounds (size 3)
```

---

## Example Programs

### Hello World
```mx
print("Hello, World!")
```

### Recursive Fibonacci
```mx
fn fib(n: int) -> int {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}

for i in range(10) {
    print(fib(i))
}
```

### Structs + Methods
```mx
struct Rectangle {
    width: float
    height: float
}

fn area(r) -> float {
    return r.width * r.height
}

fn perimeter(r) -> float {
    return 2.0 * (r.width + r.height)
}

let rect = new Rectangle { width: 5.0, height: 3.0 }
print("Area:", area(rect))
print("Perimeter:", perimeter(rect))
```

---

*MX Language v1.0 — designed for learning and fun*
