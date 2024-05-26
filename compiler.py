from enum import Enum
from llvmlite import ir, binding
import sys
import os
from ply import lex
from ply import yacc
from lexer import *
from parser import *
# TODO: Improvements on the GID system, can we cache fn arg combos for reuse?
# TODO: ASTIterator is totally hacky. Do this for real

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

def gen_println(module, builder, ir, printval):
    print(f"gen_println: {printval}")
    global GID
    name = f"println_{GID}"
    printval = printval[1:-1]
    printval_global = ir.GlobalVariable(module, ir.ArrayType(ir.IntType(8), len(printval)+1), name=name)
    printval_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), len(printval)+1),
            bytearray((printval+"\0").encode("utf8")))
    printval_global.global_constant = True
    GID = GID+1
    return builder.gep(printval_global, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=True)

def gen_let(module, builder, ir, name, val):
    print(f"gen_let: {name} = {val}")
    global GLOBAL_SCOPE
    val_global = ir.GlobalVariable(module, ir.ArrayType(ir.IntType(8), len(val)+1), name=name)
    val_global.initializer = ir.Constant(ir.ArrayType(ir.IntType(8), len(val)+1),
            bytearray((val+"\0").encode("utf8")))
    val_global.global_constant = True
    GLOBAL_SCOPE[name] = val
    return builder.gep(val_global, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=True)

def import_standard_library(module, ir):
    # Declare the puts function from the C standard library
    puts_func_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=False)
    puts_func = ir.Function(module, puts_func_type, name="puts")

    # Declare the printf function from the C standard library
    # printf_func_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
    # printf_func = ir.Function(module, printf_func_type, name="printf")

    # Declare the strlen function from the C standard library
    strlen_func_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=False)
    strlen_func = ir.Function(module, strlen_func_type, name="strlen")

    return puts_func

def codegen(ast):
    # Create a new LLVM module
    module = ir.Module(name="helloworld")

    println_ptr = None

    #print("AST:")
    #print("="*80)
    #ast = ASTIterator(ast)
    #while ast is not None:
    #    node = ast.next()
    #    print(node)
    #print("="*80)
    builder = None
    puts_func = None
    fn_ptrs = []
    ast = ASTIterator(ast)
    while ast is not None:
        node = ast.next()
        print(node)
        if node is None:
            break
        if node.node_type == ASTNodeType.MAIN:
            main_func, bldr = gen_main(module, ir)
            builder = bldr
            puts_func = import_standard_library(module, ir)
        elif node.node_type == ASTNodeType.PRINTLN:
            print("Println Node: " + str(node.arguments[0]))
            if not node.arguments[0][0] == "\"":
                println_ptr = gen_println(module, builder, ir, GLOBAL_SCOPE[node.arguments[0]])
            else:
                println_ptr = gen_println(module, builder, ir, node.arguments[0])
            builder.call(puts_func, [println_ptr])
        elif node.node_type == ASTNodeType.LET:
            print("Let Node: " + str(node.arguments))
            gen_let(module, builder, ir, node.arguments[0], node.arguments[1])
        else:
            raise Exception("Unknown AST node type")

    #main_func, builder = gen_main(module, ir)
    #println_ptr = gen_println(module, builder, ir, "Hello, world!")

    # Declare the puts function from the C standard library
    # puts_func_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=False)
    # puts_func = ir.Function(module, puts_func_type, name="puts")
    # Call the puts function

    #print("fn_ptrs: " + str(fn_ptrs))
    #for fn in fn_ptrs:
    #    print("Calling println")
    #    builder.call(puts_func, [fn])

    # Return 0 from main
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
    # TODO: Add a lexer/parser to generate the AST
    ast = AST(ASTNode(ASTNodeType.MAIN, []), [])
    parsed = parse_input(code)
    print(parsed)
    for i in range(len(parsed)):
        print("Parsed: " + str(parsed[i]))
        if parsed[i][0] == "PRINTLN":
            print("Parsed println")
            print(parsed[i][1])
            ast.children.append(ASTNode(ASTNodeType.PRINTLN, [parsed[i][1]]))
        if parsed[i][0] == "LET":
            print("Parsed let")
            print(parsed[i][1:])
            ast.children.append(ASTNode(ASTNodeType.LET, parsed[i][1:]))

    codegen(ast)
    #codegen(AST(ASTNodeType.MAIN, [ASTNode(ASTNodeType.PRINTLN, [parsed[1][1:-1]])]))
