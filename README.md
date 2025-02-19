# lang-compiler: Hobby Programming Language Compiler
See code.lng for an example program.

## Expressions
`let {name}: {type} = expression`
`print(expression)`

Variable names can be alphanumeric.

## Types
- `u8`: Unsigned 8-bit integer
- `str`: String

## Functions
Void Functions
```
fn {name}(){
 ...statements
}
```

Function Arguments
```
fn {name}({arg_name}: {arg_type}){
 ...statements
}
```

Non-Void Functions
```
fn {name}(): {type} {
 ...statements
 // last statement must evaluate to return type
}
```

Supported Functions:
- 0 argument void return

## Comments

`//` At the start of a line starts a single-line comment

## Compiling
`python3 compile.py <input file>`

## Running
`./main`
