## Python-Assembly Interpreter

The Python-Assembly Interpreter translates Python code into PEP/9 assembly language.

Supports:
* Integers
* If, Elif, Else
* While loop
* Global, Local variables
* Function Call
* I/O: Print Input

Usage: 
```commandline
translator.py [-h] [-f F] [--ast-only]
```

Examples:
<br/> Pep/9 Code
```commandline
python translator.py -f _samples/1_global/simple.py
```
Output
```commandline
; Translating _samples/1_global/simple.py
; Branching to top level (tl) instructions
                BR tl
; Allocating Global (static) memory
x:              .BLOCK 4
; Top Level instructions
tl:             NOP1
                LDWA 3,i
                ADDA 2,i
                STWA x,d
                DECO x,d
                .END
```
<br/>Abstract Syntax Tree
```commandline
python translator.py --ast-only -f _samples/1_global/simple.py
```
Output
```commandline
Module(
  body=[
    Assign(
      targets=[
        Name(id='x', ctx=Store())],
      value=BinOp(
        left=Constant(value=3),
        op=Add(),
        right=Constant(value=2))),
    Expr(
      value=Call(
        func=Name(id='print', ctx=Load()),
        args=[
          Name(id='x', ctx=Load())],
        keywords=[]))],
  type_ignores=[])
```