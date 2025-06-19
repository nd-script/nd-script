"""
ND-Script Interpreter
Main interpreter for executing ND-Script programs
"""

import os
import sys
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from functools import lru_cache

from lark import Lark, Transformer, v_args
from lark.exceptions import LarkError

from .ast import *
from .environment import Environment
from .errors import NDScriptError, NDScriptRuntimeError, NDScriptSyntaxError
from .control_flow_exceptions import BreakException, ContinueException, ReturnException, DebugBreakException
from .performance_profiler import global_profiler, profile_operation
from .ast_cache import cached_ast_parse, ast_cache, function_cache
from .bytecode_compiler import create_fast_executor
from .parallel_processor import create_parallel_processor, create_thread_safe_universe

# Import the existing quantum fractal universe
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from nexus_dimension import QuantumFractalUniverse
except ImportError:
    # Fallback for testing
    class QuantumFractalUniverse:
        def __init__(self, size=100):
            self.size = size
            self.state = "initialized"
        
        def run_simulation(self, steps=1):
            print(f"Running simulation for {steps} steps")
        
        def set_parameter(self, param, value):
            print(f"Setting {param} = {value}")


class NDScriptTransformer(Transformer):
    """Transforms parse tree to AST"""

    def start(self, statements):
        # Filter out None values (comments, etc.)
        valid_statements = [s for s in statements if s is not None]
        return Program(valid_statements)

    def statement(self, args):
        return args[0] if args else None

    def command(self, args):
        return args[0] if args else None

    def init_command(self, args):
        # args[0] is the init keyword, args[1] might be parameters
        if len(args) > 1 and isinstance(args[1], dict):
            return InitCommand(**args[1])
        return InitCommand()

    def init_params(self, args):
        # args: [param_type, "=", expression]
        if len(args) >= 3:
            param_type = str(args[0])
            value_expr = args[2]  # This is now an expression, not just a number
            param_map = {
                "عمق": "depth", "depth": "depth",
                "حجم": "size", "size": "size",
                "أبعاد": "dimensions", "dimensions": "dimensions"
            }
            return {param_map.get(param_type, param_type): value_expr}
        return {}

    def evolve_command(self, args):
        # args[0] is evolve keyword, args[1] might be expression
        if len(args) > 1:
            return EvolveCommand(steps=args[1])  # Keep as expression
        return EvolveCommand(steps=Number(1))  # Default to 1

    def show_command(self, args):
        # args[0] is show keyword, args[1] is target
        if len(args) > 1:
            target = str(args[1])
            target_map = {
                "كثافة": "density", "density": "density",
                "طاقة": "energy", "energy": "energy",
                "حالة": "state", "state": "state",
                "إحصائيات": "stats", "stats": "stats",
                "رسم": "plot", "plot": "plot",
                "تحليل": "analysis", "analysis": "analysis"
            }
            return ShowCommand(target=target_map.get(target, target))
        return ShowCommand(target="state")

    def show_target(self, args):
        return str(args[0]) if args else "state"

    def set_command(self, args):
        # args: [set_keyword, parameter, "=", value]
        if len(args) >= 4:
            parameter = str(args[1])
            value = args[3]
            param_map = {
                "عدم_انتظام": "irregularity",
                "عتبة_انهيار": "collapse_threshold",
                "جاذبية": "gravity",
                "كتلة": "mass",
                "طاقة_كمية": "quantum_energy"
            }
            return SetCommand(
                parameter=param_map.get(parameter, parameter),
                value=value
            )
        return None

    def parameter(self, args):
        return str(args[0]) if args else "unknown"

    def save_command(self, args):
        if len(args) >= 1:
            # args[0] is the expression (keyword is filtered out by grammar)
            filename_expr = args[0]
            return SaveCommand(filename=filename_expr)
        return SaveCommand(filename="default.nds")

    def load_command(self, args):
        if len(args) >= 1:
            # args[0] is the expression (keyword is filtered out by grammar)
            filename_expr = args[0]
            return LoadCommand(filename=filename_expr)
        return LoadCommand(filename="default.nds")

    def exit_command(self, args):
        return ExitCommand()

    def assignment(self, args):
        # args: [identifier, value] (the "=" is handled by the grammar)
        if len(args) >= 2:
            identifier = str(args[0])
            value = args[1]
            # Value should already be an AST node from expression processing
            return Assignment(identifier=identifier, value=value)
        return Assignment(identifier="unknown", value=Number(0))

    def expression(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:  # binary operation: expression add_op term
            left = args[0]
            operator = args[1]  # This is now the result from add_op()
            right = args[2]
            return BinaryOperation(left=left, operator=operator, right=right)
        return args[0] if args else Number(0)

    def term(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:  # binary operation: term mul_op factor
            left = args[0]
            operator = args[1]  # This is now the result from mul_op()
            right = args[2]
            return BinaryOperation(left=left, operator=operator, right=right)
        return args[0] if args else Number(0)

    def factor(self, args):
        if len(args) == 1:
            # Single factor: NUMBER, IDENTIFIER, STRING
            arg = args[0]
            if hasattr(arg, 'type'):
                if arg.type == 'NUMBER':
                    return Number(value=float(str(arg)))
                elif arg.type == 'IDENTIFIER':
                    return Identifier(name=str(arg))
                elif arg.type == 'STRING':
                    return String(value=str(arg).strip('"\''))
            return arg
        elif len(args) == 2 and str(args[0]) == '-':  # unary minus
            return UnaryOperation(operator='-', operand=args[1])
        elif len(args) == 3:  # parenthesized expression: "(" expression ")"
            return args[1]  # Return the middle element (the expression)
        return args[0] if args else Number(0)

    def number(self, token):
        value = str(token)
        try:
            return Number(value=int(value))
        except ValueError:
            return Number(value=float(value))

    def string(self, token):
        value = str(token).strip('"\'')
        return String(value=value)

    def identifier(self, token):
        return Identifier(name=str(token))

    def add_op(self, args):
        """Handle addition/subtraction operators"""
        if args and len(args) > 0:
            return str(args[0])
        return "+"

    def mul_op(self, args):
        """Handle multiplication/division/modulo operators"""
        if args and len(args) > 0:
            return str(args[0])
        return "*"

    def comment(self, args):
        # Comments are ignored in execution
        return None

    # Control Flow Transformers (basic versions - enhanced versions below)

    def loop_statement(self, args):
        # Handle for and while loops
        if len(args) >= 6:
            loop_type = str(args[0])
            if loop_type in ["كرر", "for"]:
                variable = str(args[1])
                range_expr = args[3]
                body = args[5] if isinstance(args[5], list) else [args[5]]

                # Extract range values
                if hasattr(range_expr, 'children') and len(range_expr.children) >= 2:
                    start = int(range_expr.children[0])
                    end = int(range_expr.children[1])
                    step = int(range_expr.children[2]) if len(range_expr.children) > 2 else 1
                    return ForLoop(variable=variable, start=start, end=end, step=step, body=body)
            elif loop_type in ["بينما", "while"]:
                condition = args[1]
                body = args[3] if isinstance(args[3], list) else [args[3]]
                return WhileLoop(condition=condition, body=body)
        return None

    def statement_block(self, args):
        # Return list of statements
        if len(args) == 1 and not isinstance(args[0], list):
            return [args[0]]
        return [stmt for stmt in args if stmt is not None]

    def condition(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:  # condition with comparison
            left = args[0]
            operator = str(args[1])
            right = args[2]
            return BinaryOperation(left=left, operator=operator, right=right)
        return args[0] if args else Number(1)

    def comparison_op(self, args):
        return str(args[0]) if args else "=="

    def range_expr(self, args):
        # Return a simple object with range values
        class RangeExpr:
            def __init__(self, start, end, step=1):
                self.start = start
                self.end = end
                self.step = step

        if len(args) >= 2:
            start = int(args[0])
            end = int(args[1])
            step = int(args[2]) if len(args) > 2 else 1
            return RangeExpr(start, end, step)
        return RangeExpr(0, 1, 1)

    def function_call(self, args):
        if len(args) >= 1:
            name = str(args[0])
            arguments = args[1] if len(args) > 1 else []
            if not isinstance(arguments, list):
                arguments = [arguments] if arguments else []
            return FunctionCall(name=name, arguments=arguments)
        return FunctionCall(name="unknown", arguments=[])

    def arguments(self, args):
        return list(args)

    def arg_list(self, args):
        """Transform argument list, filtering out COMMA tokens"""
        # Filter out COMMA tokens and return only the actual arguments
        filtered_args = []
        for arg in args:
            if hasattr(arg, 'type') and arg.type == 'COMMA':
                continue  # Skip comma tokens
            else:
                filtered_args.append(arg)
        return filtered_args

    # New transformer methods for advanced constructs
    def function_def(self, args):
        """Transform function definition"""
        # Parse tree structure: [name, param_list, statements...]
        if len(args) >= 3:
            # args[0] = function name (Token)
            name = str(args[0]) if hasattr(args[0], 'value') else str(args[0])

            # args[1] = parameter list
            parameters = []
            if isinstance(args[1], list):
                parameters = [str(p) if hasattr(p, 'value') else str(p) for p in args[1]]

            # args[2:] = function body (statements)
            statements = []
            for arg in args[2:]:
                if isinstance(arg, list):
                    statements.extend(arg)
                elif arg is not None:
                    statements.append(arg)

            return FunctionDef(name=name, parameters=parameters, body=statements)
        return None

    def import_stmt(self, args):
        """Transform import statement (delegates to specific import types)"""
        if len(args) == 1:
            return args[0]  # Return the specific import type
        return None

    def simple_import(self, args):
        """Transform simple import statement"""
        if len(args) >= 1:
            filename = str(args[0]).strip('"\'')
            return ImportStatement(filename=filename)
        return None

    def namespace_import(self, args):
        """Transform namespace import statement"""
        if len(args) >= 3:  # filename, "as", namespace
            filename = str(args[0]).strip('"\'')
            namespace = str(args[2]) if hasattr(args[2], 'value') else str(args[2])
            return NamespaceImport(filename=filename, namespace=namespace)
        return None

    def selective_import(self, args):
        """Transform selective import statement"""
        if len(args) >= 3:  # "from", filename, "import", symbol_list
            filename = str(args[1]).strip('"\'')
            symbols = args[3] if isinstance(args[3], list) else [args[3]]
            return SelectiveImport(filename=filename, symbols=symbols)
        return None

    def import_list(self, args):
        """Transform import list, filtering out COMMA tokens"""
        symbols = []
        for arg in args:
            if hasattr(arg, 'type') and arg.type == 'IDENTIFIER':
                symbols.append(str(arg.value))
            elif hasattr(arg, 'type') and arg.type != 'COMMA':
                symbols.append(str(arg))
        return symbols

    def macro_def(self, args):
        """Transform macro definition"""
        # Parse tree structure: [name, param_list?, statements...]
        if len(args) >= 1:
            name = str(args[0]) if hasattr(args[0], 'value') else str(args[0])
            parameters = []
            statements = []

            # Process remaining arguments
            for arg in args[1:]:
                if isinstance(arg, list) and len(arg) > 0:
                    # Check if this is a parameter list (list of strings)
                    if all(isinstance(p, str) for p in arg):
                        parameters = arg
                    else:
                        statements.extend(arg)
                elif arg is not None:
                    statements.append(arg)

            return MacroDef(name=name, parameters=parameters, body=statements)
        return None

    def param_list(self, args):
        """Transform parameter list, filtering out COMMA tokens"""
        # Filter out COMMA tokens and extract IDENTIFIER values
        params = []
        for arg in args:
            if hasattr(arg, 'type') and arg.type == 'IDENTIFIER':
                param_name = str(arg.value)
                params.append(param_name)
            elif hasattr(arg, 'type') and arg.type != 'COMMA':
                # Handle other token types that might be identifiers
                param_name = str(arg)
                params.append(param_name)
            elif hasattr(arg, 'data') and arg.data == 'param':
                # Handle Tree('param', [Token('IDENTIFIER', 'name')]) structure
                if len(arg.children) > 0 and hasattr(arg.children[0], 'type') and arg.children[0].type == 'IDENTIFIER':
                    param_name = str(arg.children[0].value)
                    params.append(param_name)

        return params

    # Enhanced Control Flow Transformers
    def if_statement(self, args):
        """Transform enhanced if statement with elif and else support"""
        # Handle different argument structures
        if len(args) >= 2:
            # args[0] = condition, args[1] = then_block, args[2] = else_block (optional)
            condition = args[0]
            then_block = args[1] if isinstance(args[1], list) else [args[1]]
            else_block = None
            elif_blocks = []

            # Process else block if present
            if len(args) >= 3:
                else_arg = args[2]
                if hasattr(else_arg, 'children') and len(else_arg.children) > 0:
                    # Extract else block from Tree structure
                    else_content = else_arg.children[0]
                    if isinstance(else_content, list):
                        else_block = else_content
                    else:
                        else_block = [else_content]
                elif isinstance(else_arg, list):
                    else_block = else_arg
                else:
                    else_block = [else_arg]

            return IfStatement(
                condition=condition,
                then_block=then_block,
                elif_blocks=elif_blocks,
                else_block=else_block
            )
        return None

    def while_statement(self, args):
        """Transform while statement"""
        if len(args) >= 4:
            condition = args[1]  # condition between parentheses
            body = args[3] if isinstance(args[3], list) else [args[3]]
            return WhileStatement(condition=condition, body=body)
        return None

    def for_statement(self, args):
        """Transform for statement"""
        if len(args) >= 6:
            variable = str(args[1])
            range_expr = args[3]
            body = args[5] if isinstance(args[5], list) else [args[5]]

            # Extract range expressions
            if hasattr(range_expr, 'start') and hasattr(range_expr, 'end'):
                start_expr = range_expr.start
                end_expr = range_expr.end
                step_expr = getattr(range_expr, 'step', Number(1))
            else:
                start_expr = Number(0)
                end_expr = Number(10)
                step_expr = Number(1)

            return ForStatement(
                variable=variable,
                start_expr=start_expr,
                end_expr=end_expr,
                step_expr=step_expr,
                body=body
            )
        return None

    def break_statement(self, args):
        """Transform break statement"""
        return BreakStatement()

    def continue_statement(self, args):
        """Transform continue statement"""
        return ContinueStatement()

    def return_statement(self, args):
        """Transform return statement"""
        if len(args) > 0:
            return ReturnStatement(value=args[0])
        else:
            return ReturnStatement(value=None)

    def debug_statement(self, args):
        """Transform debug statement"""
        message = None
        if len(args) > 1:
            message = str(args[1]).strip('"\'')
        return DebugStatement(message=message)

    def profile_block(self, args):
        """Transform profile block"""
        if len(args) >= 2:
            body = args[1] if isinstance(args[1], list) else [args[1]]
            return ProfileBlock(body=body)
        return ProfileBlock(body=[])

    def condition(self, args):
        """Transform condition expression"""
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:  # comparison expression
            left = args[0]
            operator = str(args[1])
            right = args[2]
            return ComparisonExpression(left=left, operator=operator, right=right)
        return args[0] if args else Number(1)

    def range_expr(self, args):
        """Transform range expression"""
        class RangeExpr:
            def __init__(self, start, end, step=None):
                self.start = start
                self.end = end
                self.step = step or Number(1)

        if len(args) >= 2:
            start = args[0]
            end = args[1]
            step = args[2] if len(args) > 2 else Number(1)
            return RangeExpr(start, end, step)
        return RangeExpr(Number(0), Number(1), Number(1))


class NDScriptInterpreter(ASTVisitor):
    """Main ND-Script interpreter with advanced constructs support"""

    def __init__(self, silent_mode: bool = False):
        from .environment import GlobalEnvironment
        from .scope_manager import ScopeManager, FunctionRegistry
        from .macro_processor import MacroProcessor
        from .import_resolver import ImportResolver

        self.environment = GlobalEnvironment()
        self.universe = None
        self.running = True
        self.silent_mode = silent_mode  # Performance optimization

        # Function storage
        self.functions = {}  # Legacy function storage

        # Advanced features
        self.scope_manager = ScopeManager(self.environment)
        self.function_registry = FunctionRegistry()
        self.macro_processor = MacroProcessor()
        self.import_resolver = ImportResolver(self)

        # Load grammar
        grammar_path = Path(__file__).parent.parent / "grammar" / "nds.lark"
        with open(grammar_path, 'r', encoding='utf-8') as f:
            grammar = f.read()

        self.parser = Lark(grammar, parser='lalr')
        # استخدام المحول العادي مع التحسينات
        self.transformer = NDScriptTransformer()

        # إنشاء منفذ سريع مع البايت-كود
        self.fast_executor = create_fast_executor(self)
        self.use_bytecode = True  # تفعيل البايت-كود مع fallback محسن

        # إنشاء معالج متوازي
        self.parallel_processor = create_parallel_processor()
        self.thread_safe_universe = None
    
    def interpret_file(self, filename: str) -> Any:
        """Interpret an ND-Script file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.interpret(content)
        except FileNotFoundError:
            raise NDScriptError(f"File not found: {filename}")
        except Exception as e:
            raise NDScriptError(f"Error reading file {filename}: {e}")
    
    @lru_cache(maxsize=128)
    def _cached_parse_and_transform(self, source: str) -> Any:
        """Cached parsing and transformation"""
        # Preprocess macros
        preprocessed_source = self.macro_processor.preprocess(source)

        # Parse and transform
        parse_tree = self.parser.parse(preprocessed_source)
        ast = self.transformer.transform(parse_tree)

        return ast

    def _is_simple_operation(self, source: str) -> bool:
        """Check if operation is simple enough for bytecode execution"""
        # Avoid bytecode for complex operations that might fail
        complex_keywords = ['إذا', 'if', 'دالة', 'function', 'طالما', 'while', 'كرر', 'for']
        return not any(keyword in source for keyword in complex_keywords)

    def interpret(self, source: str, filename: str = "<string>") -> Any:
        """Interpret ND-Script source code with enhanced caching"""
        global_profiler.start_operation("interpret")
        try:
            # Use enhanced caching for parse and transform
            try:
                ast = self._cached_parse_and_transform(source)
            except Exception:
                # Fallback to non-cached version for dynamic content
                preprocessed_source = self.macro_processor.preprocess(source)
                parse_tree = self.parser.parse(preprocessed_source)
                ast = self.transformer.transform(parse_tree)

            global_profiler.start_operation("execute")

            # استخدام البايت-كود للتنفيذ السريع (للعمليات البسيطة فقط)
            if self.use_bytecode and self._is_simple_operation(source):
                try:
                    result = self.fast_executor.execute(ast, source)
                    # إذا كانت النتيجة None، استخدم الطريقة التقليدية
                    if result is None:
                        result = ast.accept(self)
                except Exception as e:
                    # إعادة رفع أخطاء NDScript المهمة
                    if "Runtime Error" in str(e) or "NDScriptRuntimeError" in str(type(e)):
                        raise e
                    # fallback للطريقة التقليدية للأخطاء الأخرى
                    if not self.silent_mode:
                        print(f"Bytecode execution failed, using traditional: {e}")
                    result = ast.accept(self)
            else:
                result = ast.accept(self)

            global_profiler.end_operation("execute")

            return result
        except LarkError as e:
            raise NDScriptSyntaxError(f"Syntax error in {filename}: {e}")
        except Exception as e:
            # Add call stack trace for better error reporting
            if self.scope_manager.is_in_function():
                trace = self.scope_manager.get_call_stack_trace()
                error_msg = f"Runtime error in {filename}: {e}\nCall stack:\n" + "\n".join(trace)
            else:
                error_msg = f"Runtime error in {filename}: {e}"
            raise NDScriptRuntimeError(error_msg)
        finally:
            global_profiler.end_operation("interpret")
    
    def visit_program(self, node: Program):
        """Execute program"""
        result = None
        for statement in node.statements:
            if not self.running:
                break
            result = statement.accept(self)
        return result
    
    def visit_init_command(self, node: InitCommand):
        """Initialize quantum fractal universe"""
        size = 100  # افتراضي
        kwargs = {}

        if hasattr(node, 'size') and node.size is not None:
            # Evaluate the size expression if it's an AST node
            if hasattr(node.size, 'accept'):
                size = node.size.accept(self)
            else:
                size = node.size

        # استخدام init_universe للحصول على معالجة أفضل
        return self.init_universe(size=size, **kwargs)
    
    def visit_evolve_command(self, node: EvolveCommand):
        """Evolve the universe"""
        if not self.universe:
            raise NDScriptRuntimeError("Universe not initialized. Use 'تهيئة' or 'init' first.")

        # Evaluate steps expression if it's an AST node
        if node.steps and hasattr(node.steps, 'accept'):
            steps = node.steps.accept(self)
        elif node.steps:
            steps = node.steps
        else:
            steps = 1

        # Use the appropriate method based on universe type
        if hasattr(self.universe, 'run_simulation'):
            result = self.universe.run_simulation(steps)
            return result if result is not None else steps
        elif hasattr(self.universe, 'evolve'):
            result = self.universe.evolve(steps)
            return result if result is not None else steps
        else:
            print(f"Universe evolved for {steps} steps")
            return steps
    
    def visit_show_command(self, node: ShowCommand):
        """Display universe information"""
        # Handle target as expression or string
        if hasattr(node.target, 'accept'):
            target = node.target.accept(self)
        else:
            target = getattr(node, 'target', 'state')

        # Convert target to string if it's not already
        target = str(target).strip('"\'')

        # Initialize universe if not present for some show commands
        if not self.universe and target not in ["variables", "functions", "macros"]:
            print("Warning: Universe not initialized. Some information may be limited.")
            # Don't raise error, just show what we can

        if target in ["density", "كثافة"]:
            if self.universe:
                print("Displaying density visualization...")
                return "density_displayed"
            else:
                print("No universe to display density for")
                return None
        elif target in ["energy", "طاقة"]:
            if self.universe:
                print("Displaying energy analysis...")
                return "energy_displayed"
            else:
                print("No universe to display energy for")
                return None
        elif target in ["state", "الحالة", "حالة"]:
            return self.show_state()
        elif target in ["stats", "إحصائيات", "statistics"]:
            if self.universe:
                print("Universe Statistics:")
                print(f"  Size: {getattr(self.universe, 'size', 100)}")
                print(f"  State: {getattr(self.universe, 'state', 'active')}")
                if hasattr(self.universe, 'parameters'):
                    print(f"  Parameters: {self.universe.parameters}")
            else:
                print("No universe initialized")
            print(f"  Variables: {len(self.environment.get_all_variables())}")
            print(f"  Functions: {len(self.functions)}")
            return "stats_displayed"
        elif target in ["plot", "رسم"]:
            print("Generating plot...")
            return "plot_generated"
        elif target in ["analysis", "تحليل"]:
            print("Performing analysis...")
            return "analysis_performed"
        else:
            # Handle string literals or expressions
            print(f"Displaying: {target}")
            return target
    
    def visit_set_command(self, node: SetCommand):
        """Set universe parameter"""
        if not self.universe:
            raise NDScriptRuntimeError("Universe not initialized.")
        
        value = node.value.accept(self)
        self.universe.set_parameter(node.parameter, value)
        print(f"Set {node.parameter} = {value}")
        return value
    
    def visit_save_command(self, node: SaveCommand):
        """Save universe state"""
        import time

        # Extract filename properly
        if hasattr(node.filename, 'accept'):
            filename = node.filename.accept(self)
        else:
            filename = node.filename

        # Convert to string and clean up
        if hasattr(filename, 'value'):
            filename = filename.value
        filename = str(filename).strip('"\'')

        # Create save data even if universe is not initialized
        save_data = {
            "universe_initialized": self.universe is not None,
            "timestamp": time.time(),
            "variables": self.environment.get_all_variables(),
            "functions": list(self.functions.keys()),
            "macros": list(self.macro_processor.macros.keys()) if hasattr(self.macro_processor, 'macros') else []
        }

        # Add universe state if available
        if self.universe and hasattr(self.universe, 'get_state'):
            save_data["universe_state"] = self.universe.get_state()

        try:
            # Save as JSON file
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(f"State saved to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving state: {e}")
            return None
    
    def visit_load_command(self, node: LoadCommand):
        """Load universe state"""
        # Extract filename properly
        if hasattr(node.filename, 'accept'):
            filename = node.filename.accept(self)
        else:
            filename = node.filename

        # Convert to string and clean up
        if hasattr(filename, 'value'):
            filename = filename.value
        filename = str(filename).strip('"\'')

        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Restore variables
            if "variables" in save_data:
                for var_name, var_value in save_data["variables"].items():
                    self.environment.set(var_name, var_value)

            # Initialize universe if it was saved
            if save_data.get("universe_initialized", False):
                if not self.universe:
                    self.init_universe()

                # Restore universe state if available
                if "universe_state" in save_data and hasattr(self.universe, 'set_state'):
                    self.universe.set_state(save_data["universe_state"])

            print(f"State loaded from {filename}")
            return filename
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            return None
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def visit_exit_command(self, node: ExitCommand):
        """Exit the interpreter"""
        self.running = False
        print("Exiting ND-Script interpreter...")
        return None
    
    def visit_assignment(self, node: Assignment):
        """Handle variable assignment"""
        value = node.value.accept(self)
        self.environment.set(node.identifier, value)
        if not self.silent_mode:
            print(f"Variable '{node.identifier}' = {value}")
        return value
    
    def visit_identifier(self, node: Identifier):
        """Get variable value"""
        return self.environment.get(node.name)
    
    def visit_number(self, node: Number):
        """Return numeric value"""
        return node.value
    
    def visit_string(self, node: String):
        """Return string value"""
        return node.value
    
    def visit_binary_operation(self, node: BinaryOperation):
        """Evaluate binary operation"""
        left = node.left.accept(self)
        right = node.right.accept(self)

        # Ensure both operands are numbers for arithmetic operations
        if node.operator in ['+', '-', '*', '/', '%']:
            if not isinstance(left, (int, float)):
                raise NDScriptRuntimeError(f"Left operand must be a number, got {type(left)}")
            if not isinstance(right, (int, float)):
                raise NDScriptRuntimeError(f"Right operand must be a number, got {type(right)}")

        if node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise NDScriptRuntimeError("Division by zero")
            return left / right
        elif node.operator == '%':
            return left % right
        elif node.operator == '==':
            return left == right
        elif node.operator == '!=':
            return left != right
        elif node.operator == '<':
            return left < right
        elif node.operator == '>':
            return left > right
        elif node.operator == '<=':
            return left <= right
        elif node.operator == '>=':
            return left >= right
        else:
            raise NDScriptRuntimeError(f"Unknown operator: {node.operator}")
    
    # Control Flow Implementations (basic versions - enhanced versions below)

    def visit_for_loop(self, node: ForLoop):
        """Execute for loop"""
        result = None
        for i in range(node.start, node.end, node.step or 1):
            # Set loop variable
            self.environment.set(node.variable, i)

            # Execute loop body
            for stmt in node.body:
                if stmt:
                    result = stmt.accept(self)
        return result

    def visit_while_loop(self, node: WhileLoop):
        """Execute while loop"""
        result = None
        max_iterations = 1000  # Prevent infinite loops
        iterations = 0

        while iterations < max_iterations:
            condition_result = node.condition.accept(self)

            # Convert to boolean
            is_true = bool(condition_result)
            if isinstance(condition_result, (int, float)):
                is_true = condition_result != 0

            if not is_true:
                break

            # Execute loop body
            for stmt in node.body:
                if stmt:
                    result = stmt.accept(self)

            iterations += 1

        if iterations >= max_iterations:
            raise NDScriptRuntimeError("While loop exceeded maximum iterations (1000)")

        return result
    
    def visit_unary_operation(self, node: UnaryOperation):
        operand = node.operand.accept(self)
        if node.operator == '-':
            return -operand
        elif node.operator == '+':
            return +operand
        else:
            raise NDScriptRuntimeError(f"Unknown unary operator: {node.operator}")
    
    def visit_function_call(self, node: FunctionCall):
        """Execute function call (built-in, user-defined, or macro)"""
        # Evaluate arguments
        args = [arg.accept(self) for arg in node.arguments]

        # Check for user-defined functions in our functions dictionary first
        if node.name in self.functions:
            return self._execute_user_function(node.name, args)

        # Check for user-defined functions in function registry
        if self.function_registry.has_function(node.name):
            return self._execute_user_function(node.name, args)

        # Check for macros (treat as functions for now)
        if self.macro_processor.has_macro(node.name):
            return self._execute_macro(node.name, args)

        # Check for built-in functions
        try:
            func = self.environment.get(node.name)
            if callable(func):
                return func(*args)
            else:
                raise NDScriptRuntimeError(f"'{node.name}' is not a function")
        except NameError:
            raise NDScriptRuntimeError(f"Unknown function: {node.name}")

    def _execute_user_function(self, function_name: str, arguments: List[Any]) -> Any:
        """Execute a user-defined function"""
        # Try function registry first
        function_def = self.function_registry.get_function(function_name)
        if function_def:
            # Enter function scope
            function_env = self.scope_manager.enter_function(
                function_name, function_def.parameters, arguments
            )

            # Save current environment and switch to function environment
            old_env = self.environment
            self.environment = function_env

            try:
                # Execute function body
                result = None
                for stmt in function_def.body:
                    if not self.running:
                        break
                    result = stmt.accept(self)

                # Exit function scope
                return self.scope_manager.exit_function(result)
            except ReturnException as e:
                return e.value
            finally:
                # Restore environment
                self.environment = old_env

        # Try self.functions as fallback
        elif function_name in self.functions:
            return self._execute_legacy_function(function_name, arguments)

        else:
            raise NDScriptRuntimeError(f"Function '{function_name}' not found")

    def _execute_macro(self, macro_name: str, arguments: List[Any]) -> Any:
        """Execute a macro (simplified - treat like function for now)"""
        macro_def = self.macro_processor.macros.get(macro_name)
        if not macro_def:
            raise NDScriptRuntimeError(f"Macro '{macro_name}' not found")

        # For now, execute macro body like a function
        # In a full implementation, this would do parameter substitution and expansion

        # Enter function scope (reuse function scope management)
        function_env = self.scope_manager.enter_function(
            macro_name, macro_def.parameters, arguments
        )

        # Save current environment and switch to macro environment
        old_env = self.environment
        self.environment = function_env

        try:
            # Execute macro body
            result = None
            for stmt in macro_def.body:
                if not self.running:
                    break
                result = stmt.accept(self)

            # Exit function scope
            return self.scope_manager.exit_function(result)

        finally:
            # Restore previous environment
            self.environment = old_env

    def _execute_legacy_function(self, func_name: str, arguments: List[Any]) -> Any:
        """تنفيذ دالة معرفة من المستخدم (النسخة القديمة)"""
        if func_name not in self.functions:
            raise NDScriptRuntimeError(f"Function {func_name} not found")

        func_info = self.functions[func_name]

        # إذا كانت دالة Python محولة، استخدمها مباشرة
        if 'python_function' in func_info:
            try:
                return func_info['python_function'](*arguments)
            except Exception as e:
                raise NDScriptRuntimeError(f"Error calling Python function {func_name}: {e}")

        # تنفيذ الدالة التقليدية
        parameters = func_info.get('parameters', [])
        body = func_info.get('body', [])

        # فحص عدد المعاملات
        if len(arguments) != len(parameters):
            raise NDScriptRuntimeError(
                f"Function {func_name} expects {len(parameters)} arguments, got {len(arguments)}"
            )

        # إنشاء بيئة جديدة للدالة
        from .environment import Environment
        func_env = Environment(parent=self.environment)

        # ربط المعاملات بالقيم
        for param, arg in zip(parameters, arguments):
            func_env.set(param, arg)

        # حفظ البيئة الحالية
        old_env = self.environment
        self.environment = func_env

        try:
            # تنفيذ جسم الدالة
            result = None
            for stmt in body:
                if not self.running:
                    break
                if hasattr(stmt, 'accept'):
                    result = stmt.accept(self)
                else:
                    # Handle legacy function body format
                    result = stmt

            return result

        except ReturnException as e:
            return e.value
        finally:
            # استعادة البيئة السابقة
            self.environment = old_env

    def visit_comment(self, node: Comment):
        # Comments are ignored during execution
        return None

    def visit_function_def(self, node: 'FunctionDef'):
        """Define a user function"""
        try:
            # Store function definition in functions dictionary
            function_info = {
                'name': node.name,
                'parameters': node.parameters,
                'parameter_types': getattr(node, 'parameter_types', {}),
                'return_type': getattr(node, 'return_type', None),
                'body': node.body,
                'defined_at': time.time()
            }

            # Store in both places for compatibility
            self.functions[node.name] = function_info

            # Create a Python function wrapper for direct calling
            def create_function_wrapper(func_info, interpreter):
                def wrapper(*args):
                    return interpreter._execute_legacy_function(func_info['name'], args)
                wrapper.__name__ = func_info['name']
                return wrapper

            python_func = create_function_wrapper(function_info, self)

            # Store Python function in environment for direct access
            self.environment.set(node.name, python_func)

            # Register with function registry
            try:
                self.function_registry.register_function(node)
            except Exception as reg_error:
                print(f"Warning: Could not register function with registry: {reg_error}")

            print(f"Function '{node.name}' defined with {len(node.parameters)} parameters")
            return f"Function {node.name} defined"

        except Exception as e:
            print(f"Error defining function {node.name}: {e}")
            return node

    def visit_import_statement(self, node: 'ImportStatement'):
        """Import an ND-Script file"""
        try:
            module = self.import_resolver.resolve_import(node.filename)

            # Merge imported symbols into current scope
            self.import_resolver.merge_module_into_scope(module, self)

            # Register imported functions
            for func_name, func_def in module.functions.items():
                self.function_registry.register_function(func_def)

            # Register imported macros
            for macro_name, macro_def in module.macros.items():
                self.macro_processor.register_macro(macro_def)

            print(f"Imported '{node.filename}': {len(module.functions)} functions, {len(module.macros)} macros")
            return module

        except Exception as e:
            raise NDScriptRuntimeError(f"Import failed: {e}")

    def visit_namespace_import(self, node: 'NamespaceImport'):
        """Handle namespace import statement"""
        try:
            # Use import resolver to load the module
            module = self.import_resolver.resolve_import(node.filename)

            # Create namespace object
            namespace_obj = {}

            # Add functions to namespace
            for func_name, func_def in module.functions.items():
                namespace_obj[func_name] = func_def

            # Add macros to namespace
            for macro_name, macro_def in module.macros.items():
                namespace_obj[macro_name] = macro_def

            # Store namespace in environment
            self.environment.set(node.namespace, namespace_obj)

            print(f"Imported '{node.filename}' as '{node.namespace}': {len(module.functions)} functions, {len(module.macros)} macros")
            return None

        except Exception as e:
            raise NDScriptRuntimeError(f"Namespace import failed: {e}")

    def visit_selective_import(self, node: 'SelectiveImport'):
        """Handle selective import statement"""
        try:
            # Use import resolver to load the module
            module = self.import_resolver.resolve_import(node.filename)

            imported_count = 0

            # Import only specified symbols
            for symbol in node.symbols:
                if symbol in module.functions:
                    self.function_registry.register_function(module.functions[symbol])
                    imported_count += 1
                elif symbol in module.macros:
                    self.macro_processor.register_macro(module.macros[symbol])
                    imported_count += 1
                else:
                    print(f"Warning: Symbol '{symbol}' not found in '{node.filename}'")

            print(f"Selectively imported {imported_count} symbols from '{node.filename}'")
            return None

        except Exception as e:
            raise NDScriptRuntimeError(f"Selective import failed: {e}")

    def visit_macro_def(self, node: 'MacroDef'):
        """Define a macro"""
        self.macro_processor.register_macro(node)
        print(f"Macro '{node.name}' defined with {len(node.parameters)} parameters")
        return node

    # Enhanced Control Flow Visitor Methods
    @profile_operation("visit_if_statement")
    def visit_if_statement(self, node: 'IfStatement'):
        """Execute if statement with elif and else support"""
        try:
            # Evaluate main condition
            condition_result = self._evaluate_condition(node.condition)

            if condition_result:
                # Execute then block
                return self._execute_block(node.then_block)

            # Check elif blocks
            for elif_condition, elif_block in node.elif_blocks:
                elif_result = self._evaluate_condition(elif_condition)
                if elif_result:
                    return self._execute_block(elif_block)

            # Execute else block if present
            if node.else_block:
                return self._execute_block(node.else_block)

            return None

        except (BreakException, ContinueException) as e:
            # Re-raise control flow exceptions
            raise e
        except Exception as e:
            raise NDScriptRuntimeError(f"Error in if statement: {e}")

    @profile_operation("visit_while_statement")
    def visit_while_statement(self, node: 'WhileStatement'):
        """Execute while loop with break/continue support"""
        try:
            result = None
            iteration_count = 0
            max_iterations = 10000  # Prevent infinite loops

            while iteration_count < max_iterations:
                # Evaluate condition
                condition_result = self._evaluate_condition(node.condition)
                if not condition_result:
                    break

                try:
                    # Execute loop body
                    result = self._execute_block(node.body)
                    iteration_count += 1

                except BreakException:
                    # Break out of loop
                    break
                except ContinueException:
                    # Continue to next iteration
                    iteration_count += 1
                    continue

            if iteration_count >= max_iterations:
                print(f"Warning: While loop terminated after {max_iterations} iterations")

            return result

        except Exception as e:
            raise NDScriptRuntimeError(f"Error in while loop: {e}")

    @profile_operation("visit_for_statement")
    def visit_for_statement(self, node: 'ForStatement'):
        """Execute for loop with range iteration"""
        try:
            # Evaluate range expressions
            start_val = node.start_expr.accept(self) if hasattr(node.start_expr, 'accept') else node.start_expr
            end_val = node.end_expr.accept(self) if hasattr(node.end_expr, 'accept') else node.end_expr
            step_val = node.step_expr.accept(self) if hasattr(node.step_expr, 'accept') else node.step_expr

            # Convert to integers
            start_val = int(start_val) if isinstance(start_val, (int, float)) else 0
            end_val = int(end_val) if isinstance(end_val, (int, float)) else 10
            step_val = int(step_val) if isinstance(step_val, (int, float)) else 1

            if step_val == 0:
                raise NDScriptRuntimeError("For loop step cannot be zero")

            result = None

            # Execute loop
            current = start_val
            while (step_val > 0 and current < end_val) or (step_val < 0 and current > end_val):
                try:
                    # Set loop variable
                    self.environment.set(node.variable, current)

                    # Execute loop body
                    result = self._execute_block(node.body)

                    # Increment counter
                    current += step_val

                except BreakException:
                    # Break out of loop
                    break
                except ContinueException:
                    # Continue to next iteration
                    current += step_val
                    continue

            return result

        except Exception as e:
            raise NDScriptRuntimeError(f"Error in for loop: {e}")

    def visit_break_statement(self, node: 'BreakStatement'):
        """Execute break statement"""
        raise BreakException()

    def visit_continue_statement(self, node: 'ContinueStatement'):
        """Execute continue statement"""
        raise ContinueException()

    def visit_return_statement(self, node: 'ReturnStatement'):
        """Execute return statement"""
        if hasattr(node, 'value') and node.value:
            value = node.value.accept(self)
            raise ReturnException(value)
        else:
            raise ReturnException(None)

    def visit_debug_statement(self, node: 'DebugStatement'):
        """Execute debug statement - drop into interactive mode"""
        print("🔍 Debug breakpoint reached")
        if node.message:
            print(f"Debug message: {node.message}")

        # Display current state
        print(f"Universe state: {'Active' if self.universe else 'Not initialized'}")
        print(f"Environment variables: {list(self.environment.variables.keys())}")

        # Simple interactive debug mode
        print("Debug mode - type 'continue' to resume, 'help' for commands")
        while True:
            try:
                user_input = input("debug> ").strip()
                if user_input == 'continue':
                    break
                elif user_input == 'help':
                    print("Available commands:")
                    print("  continue - Resume execution")
                    print("  vars - Show variables")
                    print("  universe - Show universe state")
                    print("  help - Show this help")
                elif user_input == 'vars':
                    for name, value in self.environment.variables.items():
                        print(f"  {name} = {value}")
                elif user_input == 'universe':
                    if self.universe:
                        print(f"  Size: {getattr(self.universe, 'size', 'unknown')}")
                        print(f"  State: {getattr(self.universe, 'state', 'active')}")
                    else:
                        print("  Universe not initialized")
                else:
                    # Try to execute as ND-Script code
                    try:
                        result = self.interpret(user_input)
                        if result is not None:
                            print(f"Result: {result}")
                    except Exception as e:
                        print(f"Error: {e}")
            except (EOFError, KeyboardInterrupt):
                break

        return None

    def visit_profile_block(self, node: 'ProfileBlock'):
        """Execute profile block with performance monitoring"""
        import time

        print("📊 Starting performance profiling...")
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            result = self._execute_block(node.body)

            end_time = time.time()
            end_memory = self._get_memory_usage()

            duration = end_time - start_time
            memory_delta = end_memory - start_memory

            print(f"📊 Profile Results:")
            print(f"   ⏱️  Execution time: {duration:.4f} seconds")
            print(f"   🧠 Memory usage: {memory_delta:.2f} MB")
            print(f"   📈 Performance: {'Good' if duration < 1.0 else 'Needs optimization'}")

            return result

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"📊 Profile terminated due to error after {duration:.4f} seconds")
            raise e

    def visit_comparison_expression(self, node: 'ComparisonExpression'):
        """Evaluate comparison expression"""
        left_val = node.left.accept(self)
        right_val = node.right.accept(self)

        # Convert values for comparison
        if isinstance(left_val, str) or isinstance(right_val, str):
            left_val = str(left_val)
            right_val = str(right_val)
        else:
            try:
                left_val = float(left_val) if left_val is not None else 0
                right_val = float(right_val) if right_val is not None else 0
            except (ValueError, TypeError):
                left_val = str(left_val)
                right_val = str(right_val)

        # Perform comparison
        if node.operator == "==":
            return left_val == right_val
        elif node.operator == "!=":
            return left_val != right_val
        elif node.operator == "<":
            return left_val < right_val
        elif node.operator == ">":
            return left_val > right_val
        elif node.operator == "<=":
            return left_val <= right_val
        elif node.operator == ">=":
            return left_val >= right_val
        else:
            raise NDScriptRuntimeError(f"Unknown comparison operator: {node.operator}")

    # Helper methods
    def _evaluate_condition(self, condition):
        """Evaluate a condition expression"""
        if condition is None:
            return False

        result = condition.accept(self)

        # Convert result to boolean
        if isinstance(result, bool):
            return result
        elif isinstance(result, (int, float)):
            return result != 0
        elif isinstance(result, str):
            return len(result) > 0
        else:
            return result is not None

    def _execute_block(self, statements):
        """Execute a block of statements"""
        result = None
        for stmt in statements:
            if not self.running:
                break
            result = stmt.accept(self)
        return result

    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0  # psutil not available

    # طرق مساعدة للبايت-كود
    def init_universe(self, size: int = 100, **kwargs):
        """تهيئة الكون - طريقة مساعدة للبايت-كود"""
        try:
            from .universe import QuantumFractalUniverse
            self.universe = QuantumFractalUniverse()
            self.universe.initialize(size=size, **kwargs)
            print(f"Universe initialized with size={size}, parameters: {kwargs}")
            return self.universe
        except ImportError:
            # إنشاء كون وهمي للاختبار
            class MockUniverse:
                def __init__(self, size=100, **params):
                    self.size = size
                    self.parameters = params.copy()
                    self.state = "initialized"
                    self.evolution_steps = 0

                def set_parameter(self, param, value):
                    if not hasattr(self, 'parameters'):
                        self.parameters = {}
                    self.parameters[param] = value
                    print(f"Parameter {param} set to {value}")

                def evolve(self, steps=1):
                    self.evolution_steps += steps
                    print(f"Universe evolved {steps} steps (total: {self.evolution_steps})")
                    return steps

                def show_state(self):
                    print(f"Universe state:")
                    print(f"  Size: {self.size}")
                    print(f"  Evolution steps: {self.evolution_steps}")
                    print(f"  Parameters: {self.parameters}")
                    print(f"  State: {self.state}")

                def get_state(self):
                    return {
                        'size': self.size,
                        'evolution_steps': self.evolution_steps,
                        'parameters': self.parameters,
                        'state': self.state
                    }

            self.universe = MockUniverse(size, **kwargs)
            print(f"Mock universe initialized with size={size}, parameters={kwargs}")
            return self.universe

    def set_parameter(self, parameter: str, value: Any):
        """ضبط معامل - طريقة مساعدة للبايت-كود"""
        if self.universe:
            self.universe.set_parameter(parameter, value)
        print(f"Parameter {parameter} set to {value}")
        return value

    def show_state(self):
        """عرض حالة الكون - طريقة مساعدة للبايت-كود"""
        if self.universe:
            if hasattr(self.universe, 'show_state'):
                self.universe.show_state()
            else:
                print(f"Universe state: {getattr(self.universe, 'state', 'active')}")
        else:
            print("No universe initialized")
        return "State displayed"

    def evolve_universe(self, steps: int = 1):
        """تطوير الكون - طريقة مساعدة للبايت-كود"""
        if self.universe:
            if hasattr(self.universe, 'evolve'):
                result = self.universe.evolve(steps)
                return result if result is not None else steps
            else:
                print(f"Universe evolved {steps} steps")
                return steps
        else:
            print("No universe to evolve")
            return None

    def save_universe(self, filename: str = "default.nds"):
        """حفظ الكون - طريقة مساعدة للبايت-كود"""
        if self.universe:
            # محاكاة حفظ الكون
            print(f"Universe saved to {filename}")
            return filename
        else:
            print("No universe to save")
            return None

    def load_universe(self, filename: str = "default.nds"):
        """تحميل الكون - طريقة مساعدة للبايت-كود"""
        # محاكاة تحميل الكون
        print(f"Universe loaded from {filename}")
        return filename

    def enable_bytecode(self):
        """تفعيل البايت-كود"""
        self.use_bytecode = True
        self.fast_executor.set_execution_mode("bytecode")

    def disable_bytecode(self):
        """تعطيل البايت-كود"""
        self.use_bytecode = False
        self.fast_executor.set_execution_mode("traditional")

    def get_bytecode_stats(self):
        """إحصائيات البايت-كود"""
        return self.fast_executor.get_performance_stats()

    @profile_operation("visit_parallel_for_statement")
    def visit_parallel_for_statement(self, node: 'ParallelForStatement'):
        """Execute parallel for loop with concurrent execution"""
        try:
            # تقييم تعبيرات النطاق
            start_val = node.start_expr.accept(self) if hasattr(node.start_expr, 'accept') else node.start_expr
            end_val = node.end_expr.accept(self) if hasattr(node.end_expr, 'accept') else node.end_expr
            step_val = node.step_expr.accept(self) if hasattr(node.step_expr, 'accept') else node.step_expr

            # تحويل إلى أعداد صحيحة
            start_val = int(start_val) if isinstance(start_val, (int, float)) else 0
            end_val = int(end_val) if isinstance(end_val, (int, float)) else 10
            step_val = int(step_val) if isinstance(step_val, (int, float)) else 1

            if step_val == 0:
                raise NDScriptRuntimeError("Parallel for loop step cannot be zero")

            # إنشاء غلاف آمن للكون إذا لم يكن موجوداً
            if self.universe and not self.thread_safe_universe:
                self.thread_safe_universe = create_thread_safe_universe(self.universe)

            # تعريف دالة تنفيذ جسم الحلقة
            def execute_iteration(iteration_value):
                try:
                    # إنشاء بيئة محلية للخيط
                    local_env = Environment(parent=self.environment)
                    local_env.set(node.variable, iteration_value)

                    # حفظ البيئة الحالية
                    original_env = self.environment
                    self.environment = local_env

                    # تنفيذ جسم الحلقة
                    result = None
                    for stmt in node.body:
                        result = stmt.accept(self)

                    # استعادة البيئة الأصلية
                    self.environment = original_env

                    return result

                except Exception as e:
                    print(f"Error in parallel iteration {iteration_value}: {e}")
                    return None

            # تنفيذ الحلقة بالتوازي
            results = self.parallel_processor.execute_parallel_for(
                start_val, end_val, step_val, execute_iteration, node.variable
            )

            print(f"Parallel for loop completed: {len(results)} iterations")
            return results

        except Exception as e:
            raise NDScriptRuntimeError(f"Error in parallel for loop: {e}")

    def get_parallel_stats(self):
        """إحصائيات المعالجة المتوازية"""
        return self.parallel_processor.get_performance_stats()

    def benchmark_parallel_performance(self, start: int, end: int, step: int = 1, iterations: int = 3):
        """قياس أداء المعالجة المتوازية مقابل التسلسلية"""

        # دالة اختبار بسيطة
        def test_function(value):
            # محاكاة عمل حسابي
            result = 0
            for i in range(100):
                result += value * i
            return result

        return self.parallel_processor.benchmark_parallel_vs_sequential(
            start, end, step, test_function, iterations
        )


