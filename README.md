# MX Languagee



<div align="center">

![MX Language](https://img.shields.io/badge/MX-Language-blue?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Interpreter](https://img.shields.io/badge/Interpreter-Custom-green?style=flat-square)
![Parser](https://img.shields.io/badge/Recursive%20Descent-Parser-orange?style=flat-square)
![AST](https://img.shields.io/badge/AST-Execution-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)

**A Modern Programming Language Built From Scratch**

*Designed for learning compiler construction, interpreters, language design, and runtime systems.*

</div>

----

## Overview

MX Language is a complete interpreted programming language implemented entirely in Python.

It provides a full language pipeline:

- Lexical Analysis
- Parsing
- Abstract Syntax Tree Generation
- Runtime Evaluation
- Scope Management
- Functions & Closures
- Structs
- Arrays
- Module Imports
- Interactive REPL

The project demonstrates how modern programming languages work internally, from source code to execution.

MX combines the simplicity of Python, the structure of C, and the readability of Rust-inspired syntax.

---

## Features

### Language Features

- Variables (`let`, `const`)
- Primitive Types
- Functions
- Default Parameters
- Recursive Functions
- Conditionals
- Loops
- Arrays
- Structs
- Imports
- Built-in Functions
- Range Expressions
- String Utilities
- Arithmetic Operations
- Logical Operations
- Comparison Operations

### Runtime Features

- Tree-Walking Interpreter
- Scoped Environments
- Function Closures
- Dynamic Dispatch
- Runtime Error Handling
- Built-in Standard Library
- Interactive Shell

### Developer Features

- Readable Syntax
- Precise Error Messages
- Line & Column Tracking
- Modular Architecture
- Easy Extensibility
- Educational Implementation

---

# Architecture

```text
                MX Source Code
                        │
                        ▼
        ┌──────────────────────────────┐
        │           Lexer              │
        │  Converts Characters → Tokens│
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │           Parser             │
        │  Converts Tokens → AST       │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │      Abstract Syntax Tree    │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │         Interpreter          │
        │      Executes the AST        │
        └──────────────┬───────────────┘
                       │
                       ▼
                    Output
```

---

# Project Structure

```text
mx-language/
│
├── mx.py
│
├── lexer.py
│
├── parser.py
│
├── ast_nodes.py
│
├── interpreter.py
│
├── SPEC.md
│
├── showcase.mx
├── algorithms.mx
├── projects.mx
│
├── README.md
│
└── examples/
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/mx-language.git

cd mx-language
```

---

## Requirements

```text
Python 3.10+
```

No external dependencies are required.

---

# Quick Start

## Start REPL

```bash
python mx.py
```

Output:

```text
MX Language v1.0
mx>
```

---

## Execute File

```bash
python mx.py showcase.mx
```

---

## Execute Inline Code

```bash
python mx.py -c "print(10 + 20)"
```

---

# Language Guide

## Variables

```mx
let age = 21

let name: str = "Manish"

const PI = 3.14159
```

---

## Functions

```mx
fn add(a: int, b: int) -> int {
    return a + b
}

print(add(5, 10))
```

---

## Default Parameters

```mx
fn greet(name, message = "Hello") {
    print(message + ", " + name)
}

greet("Manish")
```

---

## Recursion

```mx
fn factorial(n) {
    if n <= 1 {
        return 1
    }

    return n * factorial(n - 1)
}

print(factorial(5))
```

---

## If Else

```mx
let age = 20

if age >= 18 {
    print("Adult")
}
else {
    print("Minor")
}
```

---

## While Loop

```mx
let i = 0

while i < 5 {
    print(i)
    i += 1
}
```

---

## For Loop

```mx
for i in range(10) {
    print(i)
}
```

---

## Arrays

```mx
let nums = [1, 2, 3, 4, 5]

print(nums[0])

nums.push(6)

nums.pop()

nums.reverse()

print(nums.length)

print(nums.contains(3))
```

---

## Range Expressions

```mx
let nums = [0..10]

print(nums)
```

Output:

```text
[0,1,2,3,4,5,6,7,8,9]
```

---

## Strings

```mx
let text = "Hello World"

print(text.upper())

print(text.lower())

print(text.contains("World"))

print(text.replace("World", "MX"))
```

---

## Structs

```mx
struct User {
    name: str
    age: int
}

let user = new User {
    name: "Manish",
    age: 21
}

print(user.name)

print(user.age)
```

---

## Imports

```mx
import math

print(sqrt(16))

print(PI)
```

---

# Built-in Functions

| Function | Description |
|-----------|------------|
| print() | Output values |
| input() | User input |
| len() | Length |
| type() | Type name |
| int() | Integer conversion |
| float() | Float conversion |
| str() | String conversion |
| bool() | Boolean conversion |
| range() | Sequence generation |
| push() | Append to array |
| pop() | Remove last element |
| append() | Append & return array |
| contains() | Membership test |
| sqrt() | Square root |
| abs() | Absolute value |
| max() | Maximum |
| min() | Minimum |
| floor() | Floor value |
| ceil() | Ceiling value |
| round() | Rounded value |
| exit() | Exit program |

---

# Example Program

```mx
struct Student {
    name: str
    cgpa: float
}

fn display(student) {
    print("Name:", student.name)
    print("CGPA:", student.cgpa)
}

let s = new Student {
    name: "Manish"
    cgpa: 7.8
}

display(s)
```

---

# Error Handling

MX provides detailed compiler-style diagnostics.

### Lexer Error

```text
[Lexer Error]
Line 3, Col 8:
Unexpected character '@'
```

### Parse Error

```text
[Parse Error]
Line 12, Col 4:
Expected '}'
```

### Runtime Error

```text
[Runtime Error]
Division by zero
```

### Undefined Variable

```text
[Runtime Error]
Undefined variable: 'x'
```

---

# Core Components

## Lexer

Responsible for converting source code into tokens.

Supports:

- Keywords
- Operators
- Identifiers
- Numbers
- Strings
- Comments
- Delimiters

---

## Parser

Recursive-descent parser that converts tokens into AST nodes.

Handles:

- Expressions
- Statements
- Functions
- Structs
- Loops
- Conditionals
- Assignments

---

## AST

The Abstract Syntax Tree represents program structure.

Examples:

- Program
- Variable Declaration
- Function Declaration
- Binary Operation
- Unary Operation
- Struct Creation
- Function Calls
- Loops

---

## Interpreter

Executes AST nodes directly.

Features:

- Environment Scoping
- Closures
- Function Calls
- Struct Instances
- Arrays
- Built-ins
- Error Reporting

---

# Why MX?

Building a programming language teaches:

- Compiler Design
- Language Engineering
- Runtime Systems
- Parsing Techniques
- Abstract Syntax Trees
- Scope Resolution
- Memory Models
- Closures
- Interpreters
- Language Semantics

MX was created to explore all of these concepts in a clean and understandable implementation.

---

# Roadmap

### Version 2.0

- Static Type Checker
- Bytecode Compiler
- Virtual Machine
- Generics
- Pattern Matching
- Lambda Expressions
- Package Manager
- VS Code Extension
- Debugger
- Optimizer
- Constant Folding
- Dead Code Elimination
- Garbage Collector
- Language Server Protocol

---

# Educational Topics Covered

- Compiler Construction
- Lexical Analysis
- Parsing
- AST Design
- Tree Walking Interpreters
- Scope Resolution
- Closures
- Language Runtime Design
- Custom Data Structures
- Programming Language Theory

---

# Performance Notes

Current Runtime:

- Recursive Descent Parsing
- Tree-Walking Interpreter
- Dynamic Runtime Evaluation
- Scoped Environment Execution

Future Runtime:

- Bytecode Generation
- Register VM
- JIT Compilation
- Runtime Optimizations

---

# Contributing

Contributions are welcome.

Ideas:

- New Built-in Functions
- Additional Modules
- Type Checking
- Optimizations
- Better Error Messages
- Tooling Support

---

# Author

### Manish Nalumachu

Computer Science Engineer

AI • Systems Programming • Language Design • Machine Learning • Compiler Construction

---

<div align="center">

### Build Languages. Understand Systems. Master Computing.

⭐ Star the repository if you found MX Language interesting.

</div>
