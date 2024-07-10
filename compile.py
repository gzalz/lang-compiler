from enum import Enum
from llvmlite import ir, binding
import sys
import os
from ply import lex
from ply import yacc
from lexer import *
from parser import *

GID = 0
GLOBAL_SCOPE = {}

lexer = lex.lex()
parser = yacc.yacc()

class AST:
    def __init__(self, node, children):
        self.node = node
        self.children = children

class ASTIterator:
    def __init__(self, ast):
        self.ast = ast
        self.current = 0

    def next(self):
        if self.current == 0:
            self.current += 1
            return self.ast.node
        elif self.current == len(self.ast.children) + 1:
            print("End of AST")
            return None
        elif self.current >= 1:
            self.current += 1
            idx = 0 if self.current - 2 < 0 else self.current - 2
            print("Current: " + str(self.ast.children[idx]))
            return self.ast.children[idx]
        else:
            return None 

class ASTNode:
    def __init__(self, node_type, arguments):
        self.node_type = node_type
        self.arguments = arguments

class ASTNodeType(Enum):
    MAIN = 1
    LET = 2
    PRINTLN = 3

def parse_input(input_string):
    result = parser.parse(input_string, lexer=lexer)
    return result

def gen_main(module, ir):
    # Create a function signature: int (int, char**)
    func_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32), ir.PointerType(ir.PointerType(ir.IntType(8)))])
    main_func = ir.Function(module, func_type, name="main")

    # Create an entry block in the function
    entry_block = main_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry_block)

    return main_func, builder

def create_string_struct(module):
    # Define a struct for strings with pointer, capacity, and length
    string_type = ir.global_context.get_identified_type('String')
    string_type.set_body(
        ir.PointerType(ir.IntType(8)),  # Pointer to the data
        ir.IntType(64),                 # Capacity
        ir.IntType(64)                  # Length
    )
    return string_type

def gen_string(module, builder, ir, value):
    global GID
    string_type = module.context.get_identified_type('String')
    name = f"str_{GID}"
    
    if value[0] == '"':
        string_value = value[1:-1]
        length = len(string_value)
        capacity = length + 1  # Adding space for null terminator

        # Create global string value
        str_global = ir.GlobalVariable(module, ir.ArrayType(ir.IntType(8), capacity), name)
        str_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), capacity), bytearray((string_value + '\0').encode('utf8')))
        str_global.global_constant = True

        # Create a local string struct
        str_struct = builder.alloca(string_type, name=name)
        data_ptr = builder.gep(str_global, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=True)
        builder.store(data_ptr, builder.gep(str_struct, [ir.IntType(32)(0), ir.IntType(32)(0)]))
        builder.store(ir.IntType(64)(capacity), builder.gep(str_struct, [ir.IntType(32)(0), ir.IntType(32)(1)]))
        builder.store(ir.IntType(64)(length), builder.gep(str_struct, [ir.IntType(32)(0), ir.IntType(32)(2)]))

        GID += 1
        return str_struct
    else:
        # Handle variable lookup
        if value not in GLOBAL_SCOPE:
            raise Exception(f"Undefined variable: {value}")
        return GLOBAL_SCOPE[value]

def create_println_function(module):
    # Define the printf function type
    printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
    printf = ir.Function(module, printf_ty, name="printf")

    # Define the println function type
    string_type = module.context.get_identified_type('String')
    println_ty = ir.FunctionType(ir.VoidType(), [string_type.as_pointer()])
    println = ir.Function(module, println_ty, name="println")

    # Create the function body
    block = println.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Extract the string struct fields
    str_ptr = println.args[0]
    data_ptr = builder.load(builder.gep(str_ptr, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=True))

    # Call printf to print the string
    builder.call(printf, [data_ptr])

    # Return void
    builder.ret_void()

def codegen(ast):
    # Create a new LLVM module
    module = ir.Module(name="helloworld")
    string_type = create_string_struct(module)
    create_println_function(module)

    builder = None
    fn_ptrs = []
    ast_iter = ASTIterator(ast)
    while ast_iter is not None:
        node = ast_iter.next()
        print(node)
        if node is None:
            break
        if node.node_type == ASTNodeType.MAIN:
            main_func, bldr = gen_main(module, ir)
            builder = bldr
        elif node.node_type == ASTNodeType.PRINTLN:
            print("Println Args: " + str(node.arguments))
            if node.arguments[0][0] == "\"":
                arg_ptr = gen_string(module, builder, ir, node.arguments[0])
            else:
                arg_ptr = GLOBAL_SCOPE[node.arguments[0]]
            print("Arg Ptr: " + str(type(arg_ptr)))
            builder.call(module.get_global('println'), [arg_ptr])
        elif node.node_type == ASTNodeType.LET:
            print("Let Args: " + str(node.arguments))
            var_name = node.arguments[0]
            var_value = node.arguments[1]
            var_struct = gen_string(module, builder, ir, var_value)
            GLOBAL_SCOPE[var_name] = var_struct
        else:
            raise Exception("Unknown AST node type")

    builder.ret(ir.Constant(ir.IntType(32), 0))

    # Write the LLVM IR to a file
    llvm_ir_filename = "hello_world.ll"
    with open(llvm_ir_filename, "w") as f:
        f.write(str(module))

    # Compile the LLVM IR to an object file with PIC
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()  # Required for code generation

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(reloc='pic')

    with open(llvm_ir_filename) as f:
        llvm_ir = f.read()

    mod = binding.parse_assembly(llvm_ir)
    mod.verify()

    object_filename = "hello_world.o"
    with open(object_filename, "wb") as f:
        f.write(target_machine.emit_object(mod))

    # Link the object file to create an executable with the correct flags
    executable_filename = "hello_world"
    os.system(f"gcc -no-pie {object_filename} -o {executable_filename}")

    print(f"Compiled '{executable_filename}' successfully.")

if __name__ == "__main__":
    code_path = sys.argv[1]
    code = ""
    with open(code_path, "r") as f:
        code = f.read()
    ast = AST(ASTNode(ASTNodeType.MAIN, []), [])
    parsed = parse_input(code)
    print(parsed)
    for stmt in parsed:
        print("Parsed: " + str(stmt))
        if stmt[0] == "PRINTLN":
            print("Parsed println")
            print(stmt[1])
            ast.children.append(ASTNode(ASTNodeType.PRINTLN, [stmt[1]]))
        elif stmt[0] == "LET":
            print("Parsed let")
            print(stmt[1:])
            ast.children.append(ASTNode(ASTNodeType.LET, stmt[1:]))

    codegen(ast)

