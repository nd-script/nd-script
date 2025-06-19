#!/usr/bin/env python3
"""
مُجمّع البايت-كود لـ ND-Script
Bytecode Compiler for ND-Script - Converts AST to Python bytecode
"""

import ast
import types
import functools
import time
from typing import Dict, Any, Optional, List
from .ast import *

class BytecodeCompiler:
    """مُجمّع يحول AST إلى كود Python قابل للتنفيذ المباشر"""
    
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.compiled_cache: Dict[str, types.CodeType] = {}
        self.function_cache: Dict[str, callable] = {}
        self.compile_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "compilations": 0
        }
    
    def compile_to_python_ast(self, node: ASTNode) -> ast.AST:
        """تحويل عقدة ND-Script AST إلى Python AST"""
        
        if isinstance(node, Number):
            return ast.Constant(value=node.value)
        
        elif isinstance(node, String):
            return ast.Constant(value=node.value)
        
        elif isinstance(node, Identifier):
            return ast.Name(id=node.name, ctx=ast.Load())
        
        elif isinstance(node, Assignment):
            target = ast.Name(id=node.identifier, ctx=ast.Store())
            value = self.compile_to_python_ast(node.value)
            return ast.Assign(targets=[target], value=value)
        
        elif isinstance(node, BinaryOperation):
            left = self.compile_to_python_ast(node.left)
            right = self.compile_to_python_ast(node.right)
            
            op_map = {
                '+': ast.Add(),
                '-': ast.Sub(),
                '*': ast.Mult(),
                '/': ast.Div(),
                '==': ast.Eq(),
                '!=': ast.NotEq(),
                '<': ast.Lt(),
                '>': ast.Gt(),
                '<=': ast.LtE(),
                '>=': ast.GtE()
            }
            
            if node.operator in ['+', '-', '*', '/']:
                return ast.BinOp(left=left, op=op_map[node.operator], right=right)
            else:
                return ast.Compare(left=left, ops=[op_map[node.operator]], comparators=[right])
        
        elif isinstance(node, IfStatement):
            test = self.compile_to_python_ast(node.condition)
            body = [self.compile_to_python_ast(stmt) for stmt in node.then_block]
            
            # معالجة elif و else
            orelse = []
            for elif_condition, elif_body in node.elif_blocks:
                elif_test = self.compile_to_python_ast(elif_condition)
                elif_stmts = [self.compile_to_python_ast(stmt) for stmt in elif_body]
                orelse = [ast.If(test=elif_test, body=elif_stmts, orelse=orelse)]
            
            if node.else_block:
                else_stmts = [self.compile_to_python_ast(stmt) for stmt in node.else_block]
                if orelse:
                    orelse[-1].orelse = else_stmts
                else:
                    orelse = else_stmts
            
            return ast.If(test=test, body=body, orelse=orelse)
        
        elif isinstance(node, ForStatement):
            # تحويل for loop إلى Python for loop
            target = ast.Name(id=node.variable, ctx=ast.Store())
            
            # إنشاء range call
            start = self.compile_to_python_ast(node.start_expr)
            end = self.compile_to_python_ast(node.end_expr)
            step = self.compile_to_python_ast(node.step_expr) if node.step_expr else ast.Constant(value=1)
            
            iter_value = ast.Call(
                func=ast.Name(id='range', ctx=ast.Load()),
                args=[start, end, step],
                keywords=[]
            )
            
            body = [self.compile_to_python_ast(stmt) for stmt in node.body]
            
            return ast.For(target=target, iter=iter_value, body=body, orelse=[])
        
        elif isinstance(node, WhileStatement):
            test = self.compile_to_python_ast(node.condition)
            body = [self.compile_to_python_ast(stmt) for stmt in node.body]
            return ast.While(test=test, body=body, orelse=[])
        
        elif isinstance(node, InitCommand):
            # تحويل أمر التهيئة إلى استدعاء دالة
            size_value = 100  # قيمة افتراضية
            if hasattr(node, 'parameters') and 'size' in node.parameters:
                size_value = node.parameters['size']
            elif hasattr(node, 'size') and node.size is not None:
                size_value = node.size

            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='init_universe',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[
                    ast.keyword(arg='size', value=ast.Constant(value=size_value))
                ]
            )

            # حفظ النتيجة في __last_result__
            assignment = ast.Assign(
                targets=[ast.Name(id='__last_result__', ctx=ast.Store())],
                value=func_call
            )
            return assignment

        elif isinstance(node, EvolveCommand):
            # تحويل أمر التطور إلى استدعاء دالة
            steps_value = 1  # قيمة افتراضية
            if hasattr(node, 'steps') and node.steps is not None:
                if hasattr(node.steps, 'accept'):
                    steps_ast = self.compile_to_python_ast(node.steps)
                else:
                    steps_ast = ast.Constant(value=node.steps)
            else:
                steps_ast = ast.Constant(value=1)

            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='visit_evolve_command',
                    ctx=ast.Load()
                ),
                args=[ast.Name(id='node', ctx=ast.Load())],  # سنحتاج لتمرير node
                keywords=[]
            )

            # استدعاء visit_evolve_command للحصول على فحص الأخطاء الصحيح
            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='visit_evolve_command',
                    ctx=ast.Load()
                ),
                args=[
                    ast.Call(
                        func=ast.Name(id='EvolveCommand', ctx=ast.Load()),
                        args=[],
                        keywords=[
                            ast.keyword(arg='steps', value=steps_ast)
                        ]
                    )
                ],
                keywords=[]
            )

            # حفظ النتيجة في __last_result__
            assignment = ast.Assign(
                targets=[ast.Name(id='__last_result__', ctx=ast.Store())],
                value=func_call
            )
            return assignment

        elif isinstance(node, SetCommand):
            # تحويل أمر الضبط إلى استدعاء دالة
            param_name = getattr(node, 'parameter', 'unknown')
            param_value = getattr(node, 'value', 0)

            if hasattr(param_value, 'accept'):
                value_ast = self.compile_to_python_ast(param_value)
            else:
                value_ast = ast.Constant(value=param_value)

            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='set_parameter',
                    ctx=ast.Load()
                ),
                args=[
                    ast.Constant(value=param_name),
                    value_ast
                ],
                keywords=[]
            )

            # حفظ النتيجة في __last_result__
            assignment = ast.Assign(
                targets=[ast.Name(id='__last_result__', ctx=ast.Store())],
                value=func_call
            )
            return assignment

        elif isinstance(node, SaveCommand):
            # تحويل أمر الحفظ إلى استدعاء دالة مباشر
            filename = getattr(node, 'filename', 'default.nds')

            # استدعاء save_universe مباشرة
            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='save_universe',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=filename)],
                keywords=[]
            )

            # حفظ النتيجة في __last_result__
            assignment = ast.Assign(
                targets=[ast.Name(id='__last_result__', ctx=ast.Store())],
                value=func_call
            )
            return assignment

        elif isinstance(node, LoadCommand):
            # تحويل أمر التحميل إلى استدعاء دالة مباشر
            filename = getattr(node, 'filename', 'default.nds')

            # استدعاء load_universe مباشرة
            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='load_universe',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(value=filename)],
                keywords=[]
            )

            # حفظ النتيجة في __last_result__
            assignment = ast.Assign(
                targets=[ast.Name(id='__last_result__', ctx=ast.Store())],
                value=func_call
            )
            return assignment

        elif isinstance(node, ShowCommand):
            # تحويل أمر العرض إلى استدعاء دالة
            target = getattr(node, 'target', 'state')

            # استدعاء visit_show_command مباشرة
            func_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='interpreter', ctx=ast.Load()),
                    attr='visit_show_command',
                    ctx=ast.Load()
                ),
                args=[
                    ast.Call(
                        func=ast.Name(id='ShowCommand', ctx=ast.Load()),
                        args=[],
                        keywords=[
                            ast.keyword(arg='target', value=ast.Constant(value=target))
                        ]
                    )
                ],
                keywords=[]
            )

            # حفظ النتيجة في __last_result__
            assignment = ast.Assign(
                targets=[ast.Name(id='__last_result__', ctx=ast.Store())],
                value=func_call
            )
            return assignment

        elif isinstance(node, Assignment):
            # تحويل التعيين - استخدام الطريقة التقليدية
            target = ast.Name(id=node.identifier, ctx=ast.Store())
            value = self.compile_to_python_ast(node.value)
            return ast.Assign(targets=[target], value=value)

        elif isinstance(node, FunctionDef):
            # تحويل تعريف الدالة إلى Python function
            func_name = node.name

            # إنشاء معاملات الدالة
            args = []
            param_names = []
            if hasattr(node, 'parameters') and node.parameters:
                for param in node.parameters:
                    param_name = str(param)
                    args.append(ast.arg(arg=param_name, annotation=None))
                    param_names.append(param_name)

            # تحويل جسم الدالة
            body = []
            for stmt in node.body:
                compiled_stmt = self.compile_to_python_ast(stmt)
                if compiled_stmt and not isinstance(compiled_stmt, ast.Pass):
                    body.append(compiled_stmt)

            if not body:
                body = [ast.Pass()]

            # إنشاء تعريف الدالة
            func_def = ast.FunctionDef(
                name=func_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=args,
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[]
                ),
                body=body,
                decorator_list=[],
                returns=None
            )

            # حفظ معلومات الدالة للاستخدام لاحقاً
            if not hasattr(self, '_function_params'):
                self._function_params = {}
            self._function_params[func_name] = param_names

            # حفظ معلومات الدالة في المفسر مباشرة
            if not hasattr(self.interpreter, 'functions'):
                self.interpreter.functions = {}

            import time
            func_info = {
                'name': func_name,
                'parameters': param_names,
                'body': [],
                'defined_at': time.time()
            }
            self.interpreter.functions[func_name] = func_info
            if not getattr(self.interpreter, 'silent_mode', False):
                print(f"Pre-registered function: {func_name} with parameters: {param_names}")

            return func_def

        elif isinstance(node, FunctionCall):
            # تحويل استدعاء الدالة
            func_name = node.name

            # تحويل المعاملات
            args = []
            for arg in node.arguments:
                if hasattr(arg, 'accept'):
                    compiled_arg = self.compile_to_python_ast(arg)
                    if compiled_arg:
                        args.append(compiled_arg)
                else:
                    args.append(ast.Constant(value=arg))

            func_call = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=args,
                keywords=[]
            )

            return func_call  # إرجاع ast.Call مباشرة بدلاً من ast.Expr

        elif isinstance(node, ReturnStatement):
            # تحويل جملة الإرجاع
            if hasattr(node, 'value') and node.value:
                value_ast = self.compile_to_python_ast(node.value)
                return ast.Return(value=value_ast)
            else:
                return ast.Return(value=ast.Constant(value=None))

        elif isinstance(node, Program):
            body = []
            for stmt in node.statements:
                compiled_stmt = self.compile_to_python_ast(stmt)
                if compiled_stmt and not isinstance(compiled_stmt, ast.Pass):
                    body.append(compiled_stmt)
            return ast.Module(body=body, type_ignores=[])
        
        else:
            # للعقد غير المدعومة، إرجاع None أو تخطي
            return ast.Pass()
    
    def compile_to_bytecode(self, node: ASTNode, source_code: str) -> types.CodeType:
        """تجميع عقدة AST إلى بايت-كود Python"""
        
        # فحص التخزين المؤقت
        cache_key = hash(source_code)
        if cache_key in self.compiled_cache:
            self.compile_stats["cache_hits"] += 1
            return self.compiled_cache[cache_key]
        
        self.compile_stats["cache_misses"] += 1
        self.compile_stats["compilations"] += 1
        
        try:
            # تحويل إلى Python AST
            python_ast = self.compile_to_python_ast(node)
            
            # إصلاح AST
            ast.fix_missing_locations(python_ast)
            
            # تجميع إلى بايت-كود
            bytecode = compile(python_ast, '<ndscript>', 'exec')
            
            # حفظ في التخزين المؤقت
            self.compiled_cache[cache_key] = bytecode
            
            return bytecode
            
        except Exception as e:
            # في حالة فشل التجميع، استخدم الطريقة التقليدية
            print(f"Bytecode compilation failed: {e}")
            return None
    
    def execute_bytecode(self, bytecode: types.CodeType, globals_dict: Dict[str, Any] = None) -> Any:
        """تنفيذ البايت-كود المُجمّع"""

        if globals_dict is None:
            import time
            # Import AST classes for bytecode
            from .ast import SaveCommand, LoadCommand, InitCommand, EvolveCommand, ShowCommand

            globals_dict = {
                'interpreter': self.interpreter,
                'range': range,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'print': print,
                'time': time,
                'SaveCommand': SaveCommand,
                'LoadCommand': LoadCommand,
                'InitCommand': InitCommand,
                'EvolveCommand': EvolveCommand,
                'ShowCommand': ShowCommand
            }

        # إضافة متغيرات البيئة
        env_vars = self.interpreter.environment.get_all_variables()
        globals_dict.update(env_vars)

        # إضافة الدوال المعرفة
        if hasattr(self.interpreter, 'functions'):
            for func_name, func_info in self.interpreter.functions.items():
                # إنشاء wrapper للدالة
                def create_function_wrapper(name, info):
                    def wrapper(*args):
                        return self.interpreter._execute_user_function(name, list(args))
                    return wrapper

                globals_dict[func_name] = create_function_wrapper(func_name, func_info)

        try:
            # إضافة متغير خاص لتتبع آخر نتيجة
            globals_dict['__last_result__'] = None

            # تنفيذ البايت-كود
            result = None
            exec(bytecode, globals_dict)

            # الحصول على آخر نتيجة إذا كانت متوفرة
            result = globals_dict.get('__last_result__', None)

            # تحديث متغيرات البيئة
            excluded_names = {'interpreter', 'range', 'len', 'str', 'int', 'float', 'print', '__last_result__'}
            for name, value in globals_dict.items():
                if (not name.startswith('__') and
                    name not in excluded_names and
                    not callable(value)):
                    self.interpreter.environment.set(name, value)

            # تحديث الدوال المعرفة
            for name, value in globals_dict.items():
                if (callable(value) and
                    not name.startswith('__') and
                    name not in excluded_names and
                    hasattr(value, '__name__') and
                    value.__name__ == name):  # تأكد أن الاسم يطابق

                    # إضافة الدالة إلى سجل الدوال
                    if not hasattr(self.interpreter, 'functions'):
                        self.interpreter.functions = {}

                    # تجاهل الدوال المدمجة
                    if name in ['abs', 'min', 'max', 'round', 'sin', 'cos', 'tan', 'sqrt', 'log', 'exp', 'pow']:
                        continue  # تخطي الدوال المدمجة

                    # تجاهل AST classes
                    if name in ['SaveCommand', 'LoadCommand', 'InitCommand', 'EvolveCommand', 'ShowCommand']:
                        continue  # تخطي AST classes

                    # استخراج معلومات المعاملات من الدالة المحفوظة
                    parameters = []
                    if hasattr(self, '_function_params') and name in self._function_params:
                        parameters = self._function_params[name]
                    else:
                        # محاولة استخراج من inspect كحل احتياطي
                        import inspect
                        try:
                            sig = inspect.signature(value)
                            parameters = list(sig.parameters.keys())
                        except:
                            parameters = []

                    # تحويل الدالة إلى معلومات دالة
                    import time
                    func_info = {
                        'name': name,
                        'parameters': parameters,
                        'body': [],
                        'python_function': value,
                        'defined_at': time.time()
                    }
                    self.interpreter.functions[name] = func_info

                    # إضافة الدالة إلى البيئة أيضاً للوصول المباشر
                    self.interpreter.environment.set(name, value)

                    if not getattr(self.interpreter, 'silent_mode', False):
                        print(f"Registered function: {name} with parameters: {parameters}")

            return result

        except Exception as e:
            # إعادة رفع الأخطاء المهمة
            if "Runtime Error" in str(e) or "NDScriptRuntimeError" in str(type(e)):
                raise e
            print(f"Bytecode execution failed: {e}")
            return None
    
    def compile_and_execute(self, node: ASTNode, source_code: str) -> Any:
        """تجميع وتنفيذ في خطوة واحدة"""
        
        bytecode = self.compile_to_bytecode(node, source_code)
        
        if bytecode:
            return self.execute_bytecode(bytecode)
        else:
            # fallback للطريقة التقليدية
            return node.accept(self.interpreter)
    
    def get_compile_stats(self) -> Dict[str, Any]:
        """إحصائيات التجميع"""
        total_requests = self.compile_stats["cache_hits"] + self.compile_stats["cache_misses"]
        hit_rate = (self.compile_stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.compile_stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "cache_size": len(self.compiled_cache)
        }
    
    def clear_cache(self):
        """مسح التخزين المؤقت"""
        self.compiled_cache.clear()
        self.function_cache.clear()
        self.compile_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "compilations": 0
        }

class FastExecutor:
    """منفذ سريع يستخدم البايت-كود"""
    
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.compiler = BytecodeCompiler(interpreter)
        self.execution_mode = "bytecode"  # "bytecode" أو "traditional"
    
    def execute(self, node: ASTNode, source_code: str = "") -> Any:
        """تنفيذ سريع للعقدة"""
        
        if self.execution_mode == "bytecode":
            try:
                return self.compiler.compile_and_execute(node, source_code)
            except Exception as e:
                # إعادة رفع أخطاء NDScript المهمة
                if "Runtime Error" in str(e) or "NDScriptRuntimeError" in str(type(e)):
                    raise e
                # fallback للطريقة التقليدية للأخطاء الأخرى
                print(f"Fast execution failed, falling back: {e}")
                return node.accept(self.interpreter)
        else:
            return node.accept(self.interpreter)
    
    def set_execution_mode(self, mode: str):
        """تعيين وضع التنفيذ"""
        if mode in ["bytecode", "traditional"]:
            self.execution_mode = mode
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """إحصائيات الأداء"""
        return {
            "execution_mode": self.execution_mode,
            "compiler_stats": self.compiler.get_compile_stats()
        }

# دالة مساعدة للاستخدام السريع
def create_fast_executor(interpreter) -> FastExecutor:
    """إنشاء منفذ سريع"""
    return FastExecutor(interpreter)
