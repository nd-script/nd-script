#!/usr/bin/env python3
"""
محول AST سريع ومحسن لـ ND-Script
Fast and Optimized AST Transformer for ND-Script
"""

from lark import Transformer, v_args
from .ast import *
import functools

class FastNDScriptTransformer(Transformer):
    """محول AST محسن للأداء"""
    
    def __init__(self):
        super().__init__()
        # تخزين مؤقت للعقد المتكررة
        self._node_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _cache_node(self, node_type, *args):
        """تخزين مؤقت للعقد المتشابهة"""
        cache_key = (node_type, args)
        if cache_key in self._node_cache:
            self._cache_hits += 1
            return self._node_cache[cache_key]
        
        # إنشاء عقدة جديدة
        if node_type == "Number":
            node = Number(value=args[0])
        elif node_type == "String":
            node = String(value=args[0])
        elif node_type == "Identifier":
            node = Identifier(name=args[0])
        else:
            # للعقد المعقدة، لا نستخدم التخزين المؤقت
            self._cache_misses += 1
            return None
        
        self._node_cache[cache_key] = node
        self._cache_misses += 1
        return node
    
    @v_args(inline=True)
    def start(self, *statements):
        """تحويل البرنامج الرئيسي"""
        valid_statements = [s for s in statements if s is not None]
        return Program(valid_statements)
    
    @v_args(inline=True)
    def statement(self, stmt):
        """تحويل الجملة"""
        return stmt
    
    @v_args(inline=True)
    def command(self, cmd):
        """تحويل الأمر"""
        return cmd
    
    @v_args(inline=True)
    def init_command(self, *args):
        """تحويل أمر التهيئة"""
        params = {}

        # معالجة المعاملات
        for arg in args:
            if isinstance(arg, dict):
                params.update(arg)
            elif hasattr(arg, '__iter__') and not isinstance(arg, str):
                # قائمة معاملات
                for item in arg:
                    if isinstance(item, dict):
                        params.update(item)

        return InitCommand(**params)
    
    @v_args(inline=True)
    def init_params(self, *args):
        """تحويل معاملات التهيئة"""
        if len(args) >= 3:
            param_type = args[0]
            expression = args[2]  # تخطي علامة =

            param_map = {
                "عمق": "depth", "depth": "depth",
                "حجم": "size", "size": "size",
                "أبعاد": "dimensions", "dimensions": "dimensions"
            }
            return {param_map.get(str(param_type), str(param_type)): expression}
        return {}
    
    @v_args(inline=True)
    def evolve_command(self, *args):
        """تحويل أمر التطور"""
        if len(args) > 0:
            return EvolveCommand(steps=args[0])
        return EvolveCommand(steps=Number(1))
    
    @v_args(inline=True)
    def show_command(self, *args):
        """تحويل أمر العرض"""
        # معالجة الحالات المختلفة
        if len(args) == 1:
            target = args[0]
        elif len(args) == 2:
            # "عرض الحالة" أو "عرض إحصائيات"
            if str(args[1]) in ["الحالة", "إحصائيات"]:
                target = str(args[1])
            else:
                target = args[1]
        else:
            target = "state"  # افتراضي

        target_map = {
            "كثافة": "density", "density": "density",
            "طاقة": "energy", "energy": "energy",
            "حالة": "state", "state": "state", "الحالة": "state",
            "إحصائيات": "stats", "stats": "stats",
            "رسم": "plot", "plot": "plot",
            "تحليل": "analysis", "analysis": "analysis"
        }

        final_target = target_map.get(str(target), str(target))
        return ShowCommand(target=final_target)
    
    def set_command(self, args):
        """تحويل أمر الضبط"""
        if len(args) >= 3:
            parameter = args[0]
            value = args[2]  # تخطي علامة =

            param_map = {
                "عدم_انتظام": "irregularity",
                "عتبة_انهيار": "collapse_threshold",
                "جاذبية": "gravity",
                "كتلة": "mass",
                "طاقة_كمية": "quantum_energy"
            }
            return SetCommand(
                parameter=param_map.get(str(parameter), str(parameter)),
                value=value
            )
        return SetCommand(parameter="unknown", value=Number(0))
    
    @v_args(inline=True)
    def save_command(self, keyword, filename_expr):
        """تحويل أمر الحفظ"""
        # Extract filename value if it's a String object
        if isinstance(filename_expr, String):
            return SaveCommand(filename=filename_expr.value)
        elif hasattr(filename_expr, 'value'):
            return SaveCommand(filename=filename_expr.value)
        else:
            # Store the expression directly for evaluation later
            return SaveCommand(filename=filename_expr)

    @v_args(inline=True)
    def load_command(self, keyword, filename_expr):
        """تحويل أمر التحميل"""
        # Extract filename value if it's a String object
        if isinstance(filename_expr, String):
            return LoadCommand(filename=filename_expr.value)
        elif hasattr(filename_expr, 'value'):
            return LoadCommand(filename=filename_expr.value)
        else:
            # Store the expression directly for evaluation later
            return LoadCommand(filename=filename_expr)
    
    @v_args(inline=True)
    def exit_command(self):
        """تحويل أمر الخروج"""
        return ExitCommand()
    
    def assignment(self, args):
        """تحويل الإسناد مع دعم type annotations"""
        if len(args) >= 3:
            identifier = args[0]
            # Find the equals sign and value
            equals_index = -1
            for i, arg in enumerate(args):
                if str(arg) == '=':
                    equals_index = i
                    break

            if equals_index > 0 and equals_index < len(args) - 1:
                value = args[equals_index + 1]
                # Extract type annotation if present (between identifier and =)
                type_annotation = None
                if equals_index > 1:
                    type_annotation = args[1:equals_index]

                return Assignment(
                    identifier=str(identifier),
                    value=value,
                    type_annotation=type_annotation
                )
            else:
                # Fallback to old behavior
                value = args[2] if len(args) > 2 else Number(0)
                return Assignment(identifier=str(identifier), value=value)
        return Assignment(identifier="unknown", value=Number(0))
    
    @v_args(inline=True)
    def expression(self, *args):
        """تحويل التعبير"""
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            return BinaryOperation(left=args[0], operator=str(args[1]), right=args[2])
        return args[0] if args else Number(0)
    
    @v_args(inline=True)
    def term(self, *args):
        """تحويل المصطلح"""
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            return BinaryOperation(left=args[0], operator=str(args[1]), right=args[2])
        return args[0] if args else Number(0)
    
    @v_args(inline=True)
    def factor(self, *args):
        """تحويل العامل"""
        if len(args) == 1:
            arg = args[0]
            if hasattr(arg, 'type'):
                if arg.type == 'NUMBER':
                    # استخدام التخزين المؤقت للأرقام
                    cached = self._cache_node("Number", float(str(arg)))
                    if cached:
                        return cached
                    return Number(value=float(str(arg)))
                elif arg.type == 'IDENTIFIER':
                    # استخدام التخزين المؤقت للمعرفات
                    cached = self._cache_node("Identifier", str(arg))
                    if cached:
                        return cached
                    return Identifier(name=str(arg))
                elif arg.type == 'STRING':
                    # استخدام التخزين المؤقت للنصوص
                    cached = self._cache_node("String", str(arg).strip('"\''))
                    if cached:
                        return cached
                    return String(value=str(arg).strip('"\''))
            return arg
        elif len(args) == 2 and str(args[0]) == '-':
            return UnaryOperation(operator='-', operand=args[1])
        elif len(args) == 3:
            return args[1]  # التعبير بين الأقواس
        return args[0] if args else Number(0)
    
    def function_def(self, args):
        """تحويل تعريف الدالة - نسخة محسنة من المفسر"""
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

            return FunctionDef(name=name, parameters=parameters, body=statements)
        return None
    
    @v_args(inline=True)
    def macro_def(self, name, *args):
        """تحويل تعريف الماكرو"""
        parameters = []
        statements = []
        
        for arg in args:
            if isinstance(arg, list):
                if all(isinstance(p, str) for p in arg):
                    parameters = arg
                else:
                    statements.extend(arg)
            elif arg is not None:
                statements.append(arg)
        
        return MacroDef(name=str(name), parameters=parameters, body=statements)
    
    def param_list(self, args):
        """تحويل قائمة المعاملات - نسخة محسنة من المفسر"""
        # Filter out COMMA tokens and extract IDENTIFIER values
        params = []
        for arg in args:
            if hasattr(arg, 'type') and arg.type == 'IDENTIFIER':
                params.append(str(arg.value))
            elif hasattr(arg, 'type') and arg.type != 'COMMA':
                # Handle other token types that might be identifiers
                params.append(str(arg))
        return params

    @v_args(inline=True)
    def param(self, identifier, *type_info):
        """تحويل معامل واحد مع أو بدون تعليق توضيحي للنوع"""
        param_name = str(identifier)

        # إرجاع اسم المعامل فقط للآن
        return param_name
    
    @v_args(inline=True)
    def function_call(self, name, *args):
        """تحويل استدعاء الدالة"""
        arguments = []
        for arg in args:
            if isinstance(arg, list):
                arguments.extend(arg)
            elif arg is not None:
                arguments.append(arg)
        return FunctionCall(name=str(name), arguments=arguments)
    
    @v_args(inline=True)
    def arg_list(self, *args):
        """تحويل قائمة الحجج"""
        return [arg for arg in args if not (hasattr(arg, 'type') and arg.type == 'COMMA')]
    
    @v_args(inline=True)
    def if_statement(self, condition, then_block, *rest):
        """تحويل جملة if"""
        elif_blocks = []
        else_block = None
        
        # معالجة elif و else
        i = 0
        while i < len(rest):
            if i < len(rest) - 1 and hasattr(rest[i], 'children'):
                # elif block
                elif_condition = rest[i].children[1] if len(rest[i].children) > 1 else None
                elif_body = rest[i+1] if isinstance(rest[i+1], list) else [rest[i+1]]
                elif_blocks.append((elif_condition, elif_body))
                i += 2
            elif str(rest[i]) in ["وإلا", "else"]:
                # else block
                else_block = rest[i+1] if isinstance(rest[i+1], list) else [rest[i+1]]
                break
            else:
                i += 1
        
        then_block = then_block if isinstance(then_block, list) else [then_block]
        
        return IfStatement(
            condition=condition,
            then_block=then_block,
            elif_blocks=elif_blocks,
            else_block=else_block
        )
    
    @v_args(inline=True)
    def while_statement(self, condition, body):
        """تحويل جملة while"""
        body = body if isinstance(body, list) else [body]
        return WhileStatement(condition=condition, body=body)
    
    @v_args(inline=True)
    def for_statement(self, variable, range_expr, body):
        """تحويل جملة for"""
        body = body if isinstance(body, list) else [body]
        
        if hasattr(range_expr, 'start') and hasattr(range_expr, 'end'):
            start_expr = range_expr.start
            end_expr = range_expr.end
            step_expr = getattr(range_expr, 'step', Number(1))
        else:
            start_expr = Number(0)
            end_expr = Number(10)
            step_expr = Number(1)
        
        return ForStatement(
            variable=str(variable),
            start_expr=start_expr,
            end_expr=end_expr,
            step_expr=step_expr,
            body=body
        )
    
    @v_args(inline=True)
    def break_statement(self):
        """تحويل جملة break"""
        return BreakStatement()
    
    @v_args(inline=True)
    def continue_statement(self):
        """تحويل جملة continue"""
        return ContinueStatement()
    
    @v_args(inline=True)
    def debug_statement(self, *args):
        """تحويل جملة debug"""
        message = None
        if len(args) > 0:
            message = str(args[0]).strip('"\'')
        return DebugStatement(message=message)
    
    @v_args(inline=True)
    def profile_block(self, body):
        """تحويل كتلة profile"""
        body = body if isinstance(body, list) else [body]
        return ProfileBlock(body=body)
    
    @v_args(inline=True)
    def condition(self, *args):
        """تحويل الشرط"""
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            return ComparisonExpression(left=args[0], operator=str(args[1]), right=args[2])
        return args[0] if args else Number(1)
    
    @v_args(inline=True)
    def range_expr(self, *args):
        """تحويل تعبير النطاق"""
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
    
    @v_args(inline=True)
    def statement_block(self, *statements):
        """تحويل كتلة الجمل"""
        return [stmt for stmt in statements if stmt is not None]
    
    @v_args(inline=True)
    def comment(self, *args):
        """تحويل التعليق"""
        return None
    
    def get_cache_stats(self):
        """إحصائيات التخزين المؤقت"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self._node_cache)
        }
