import os
import sys
from enum import Enum
from parser import *

from lexer import *
from llvmlite import binding, ir
from ply import lex, yacc

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
    def __init__(self, node_type, arguments=[], expressions=[], children=[]):
        self.node_type = node_type
        self.arguments = arguments
        self.expressions = expressions
        self.children = children


class ASTNodeType(Enum):
    MAIN = 1
    CONST = 2
    PRINTLN = 3
    END_FN = 4
    FN0_VOID = 5
    INVOKE0 = 6


def parse_input(input_string):
    result = parser.parse(input_string, lexer=lexer)
    return result


def gen_main(module, ir):
    # Create a function signature: int (int, char**)
    func_type = ir.FunctionType(
        ir.IntType(32),
        [ir.IntType(32), ir.PointerType(ir.PointerType(ir.IntType(8)))],
    )
    main_func = ir.Function(module, func_type, name="main")

    # Create an entry block in the function
    entry_block = main_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry_block)

    return main_func, builder


def create_string_struct(module):
    # Define a struct for strings with pointer, capacity, and length
    string_type = ir.global_context.get_identified_type("String")
    string_type.set_body(
        ir.PointerType(ir.IntType(8)),  # Pointer to the data
        ir.IntType(32),  # Capacity
        ir.IntType(32),  # Length
    )
    return string_type


def gen_string(name, module, builder, ir, value, scope):
    string_type = module.context.get_identified_type("String")
    var_name = name
    name = f"str_{name}"

    if value[0] == '"':
        string_value = (
            value[1:-1].encode("utf-8").decode("unicode_escape")
        )  # Interpret escape sequences like \n
        length = len(string_value)
        capacity = length

        # Create global string value
        str_global = ir.GlobalVariable(
            module, ir.ArrayType(ir.IntType(8), capacity), name
        )
        str_global.initializer = ir.Constant(
            ir.ArrayType(ir.IntType(8), capacity),
            bytearray(string_value.encode("utf8")),
        )

        # Create a local string struct
        str_struct = builder.alloca(string_type, name=name)
        data_ptr = builder.gep(
            str_global, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=True
        )
        builder.store(
            data_ptr,
            builder.gep(str_struct, [ir.IntType(32)(0), ir.IntType(32)(0)]),
        )
        builder.store(
            ir.IntType(32)(capacity),
            builder.gep(str_struct, [ir.IntType(32)(0), ir.IntType(32)(1)]),
        )
        builder.store(
            ir.IntType(32)(length),
            builder.gep(str_struct, [ir.IntType(32)(0), ir.IntType(32)(2)]),
        )

        return str_struct
    else:
        # Handle variable lookup
        if var_name not in scope.keys():
            print(f"Scope dump: {scope}")
            raise Exception(f"Undefined variable: {var_name}")
        return scope[var_name]


def gen_u8(name, module, builder, ir, value):
    name = f"u8_{name}"

    u8_value = int(value)
    u8_global = ir.Constant(ir.IntType(8), name)
    u8_global.initializer = ir.Constant(ir.IntType(8), u8_value)

    u8_var = builder.alloca(ir.IntType(8), name=name)
    builder.store(ir.Constant(ir.IntType(8), u8_value), u8_var)

    return u8_var


def create_println_function(module):
    # Define the 'write' syscall function type
    write_ty = ir.FunctionType(
        ir.IntType(64),
        [ir.IntType(64), ir.PointerType(ir.IntType(8)), ir.IntType(32)],
        var_arg=False,
    )
    write_func = ir.Function(module, write_ty, name="write")

    string_type = module.context.get_identified_type("String")
    println_ty = ir.FunctionType(ir.VoidType(), [string_type.as_pointer()])
    println = ir.Function(module, println_ty, name="print")

    block = println.append_basic_block(name="entry_println")
    builder = ir.IRBuilder(block)

    str_ptr = println.args[0]
    data_ptr = builder.load(
        builder.gep(
            str_ptr, [ir.IntType(32)(0), ir.IntType(32)(0)], inbounds=True
        )
    )
    length = builder.load(
        builder.gep(
            str_ptr, [ir.IntType(32)(0), ir.IntType(32)(2)], inbounds=True
        )
    )
    # File descriptor 1 (stdout)
    fd = ir.Constant(ir.IntType(64), 1)
    builder.call(write_func, [fd, data_ptr, length])
    builder.ret_void()

def create_function0_void(module, name):
    fn_ty = ir.FunctionType(ir.VoidType(), [])
    fn = ir.Function(module, fn_ty, name=name)

    # Create the function body
    block = fn.append_basic_block(name="entry_"+str(name))
    builder = ir.IRBuilder(block)
    end_fn_callback = lambda: builder.ret_void()
    return builder, end_fn_callback

def codegen_invoke0(name, module, builder, ir):
    print(f"[codegen] invoke0: {name}")
    builder.call(module.get_global(name), [])

def codegen_println(node_arguments, module, builder, ir, scope, values):
    print("[codegen] println: " + str(node_arguments))
    if not node_arguments[0][0] == '"':
        print("[values-dump] " + str(values))
        if not values.get(node_arguments[0]) is None and isinstance(values[node_arguments[0]], int):
            print("Got integer value")
            arg_ptr = gen_string(
                node_arguments[0],
                module,
                builder,
                ir,
                '"%d"' % values[node_arguments[0]],
                scope # does this need to be a thing?
            )
        else:
            arg_ptr = gen_string(
                node_arguments[0], module, builder, ir, node_arguments[0], scope
            )
    else:
        arg_ptr = gen_string(node_arguments[0], module, builder, ir, node_arguments[0], scope)
    print("Arg Ptr: " + str(type(arg_ptr)))
    builder.call(module.get_global("print"), [arg_ptr])

def codegen_const(node_arguments, module, builder, ir, scope, values):
    print(f"[codegen] const: {node_arguments}")
    var_name = node_arguments[0]
    var_type = node_arguments[1]
    var_value = node_arguments[2]
    var_struct = None
    print("const Args: " + str(node_arguments))
    if var_type == "u8":
        if var_value > 255 or var_value < 0:
            raise Exception("u8 value must be between 0 and 255")
        var_struct = gen_u8(var_name, module, builder, ir, var_value)
    if var_type == "str":
        var_struct = gen_string(var_name, module, builder, ir, var_value, scope)
    scope[var_name] = var_struct
    values[var_name] = var_value

def codegen(ast):
    # Create a new LLVM module
    module = ir.Module(name="helloworld")
    string_type = create_string_struct(module)
    create_println_function(module)
    println_ptr = None

    main_builder = None
    builder = None
    end_fn_callback = None
    puts_func = None
    ast_iter = ASTIterator(ast)
    main_scope = {}
    scope = {}
    # hacky af we need internal type conversions 
    values = {}
    while ast_iter is not None:
        node = ast_iter.next()
        print(node)
        if node is None:
            break
        if node.node_type == ASTNodeType.MAIN:
            main_func, bldr = gen_main(module, ir)
            builder = bldr
            main_builder = bldr
        elif node.node_type == ASTNodeType.PRINTLN:
            codegen_println(node.arguments, module, builder, ir, scope, values)    
        elif node.node_type == ASTNodeType.CONST:
            codegen_const(node.arguments, module, builder, ir, scope, values) 
        elif node.node_type == ASTNodeType.FN0_VOID:
            fn_name = node.arguments[0]
            builder, callback = create_function0_void(module, fn_name) 
            end_fn_callback = callback
            builder = builder
            main_scope = scope
            scope = {}
        elif node.node_type == ASTNodeType.END_FN:
            builder = main_builder
            scope = main_scope
            end_fn_callback()
        elif node.node_type == ASTNodeType.INVOKE0:
            codegen_invoke0(node.arguments[0], module, builder, ir)
        else:
            raise Exception("Unknown AST node type")

    builder.ret(ir.Constant(ir.IntType(32), 0))

    # Write the LLVM IR to a file
    llvm_ir_filename = "main.ll"
    with open(llvm_ir_filename, "w") as f:
        f.write(str(module))

    # Compile the LLVM IR to an object file with PIC
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()  # Required for code generation

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(reloc="pic")

    with open(llvm_ir_filename) as f:
        llvm_ir = f.read()

    mod = binding.parse_assembly(llvm_ir)
    mod.verify()

    object_filename = "main.o"
    with open(object_filename, "wb") as f:
        f.write(target_machine.emit_object(mod))

    # Link the object file to create an executable with the correct flags
    executable_filename = "main"
    os.system(f"gcc -no-pie {object_filename} -o {executable_filename}")

    print(f"Compiled '{executable_filename}' successfully.")

def build_node(stmt, ast):
    if stmt[0] == "PRINTLN":
        print("Adding println to AST")
        print(stmt[1])
        ast.children.append(ASTNode(ASTNodeType.PRINTLN, [stmt[1]]))
    if stmt[0] == "CONST":
        print("Adding const to AST")
        print(stmt[1:])
        ast.children.append(ASTNode(ASTNodeType.CONST, stmt[1:]))
    if stmt[0] == "INVOKE":
        print("Adding INVOKE0 to AST")
        print(stmt[1:])
        ast.children.append(ASTNode(ASTNodeType.INVOKE0, stmt[1:]))

if __name__ == "__main__":
    code_path = sys.argv[1]
    code = ""
    with open(code_path, "r") as f:
        code = f.read()
    ast = AST(ASTNode(ASTNodeType.MAIN, []), [])
    parsed = parse_input(code)
    print(parsed)
    for stmt in parsed:
        if stmt[0] == "PRINTLN":
            build_node(stmt, ast)
        if stmt[0] == "CONST":
            build_node(stmt, ast)
        if stmt[0] == "FN0_VOID":
            print("Adding fn0_void to AST")
            print(stmt)
            ast.children.append(ASTNode(ASTNodeType.FN0_VOID, stmt[1:]))
            for expression in stmt[2]:
                build_node(expression, ast)
            ast.children.append(ASTNode(ASTNodeType.END_FN, [])) 
        if stmt[0] == "INVOKE0":
            print("Adding INVOKE0 to AST")
            print(stmt[1:])
            ast.children.append(ASTNode(ASTNodeType.INVOKE0, stmt[1:]))
    codegen(ast)
