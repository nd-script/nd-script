#!/usr/bin/env python3
"""
نظام الأنواع المتقدم لـ ND-Script
Advanced Type System for ND-Script with Bilingual Support
"""

from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass
from enum import Enum

class TypeKind(Enum):
    """أنواع البيانات الأساسية"""
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    LIST = "list"
    OBJECT = "object"
    VOID = "void"
    UNKNOWN = "unknown"

@dataclass
class NDType:
    """نوع بيانات ND-Script"""
    kind: TypeKind
    element_type: Optional['NDType'] = None  # للقوائم
    name: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = self.kind.value
    
    def is_compatible_with(self, other: 'NDType') -> bool:
        """فحص التوافق بين الأنواع"""
        if self.kind == TypeKind.UNKNOWN or other.kind == TypeKind.UNKNOWN:
            return True
        
        if self.kind == other.kind:
            if self.kind == TypeKind.LIST:
                if self.element_type and other.element_type:
                    return self.element_type.is_compatible_with(other.element_type)
                return True  # قوائم بدون نوع محدد
            return True
        
        # تحويلات ضمنية
        if self.kind == TypeKind.NUMBER and other.kind == TypeKind.BOOLEAN:
            return True
        if self.kind == TypeKind.BOOLEAN and other.kind == TypeKind.NUMBER:
            return True
        
        return False
    
    def __str__(self):
        if self.kind == TypeKind.LIST and self.element_type:
            return f"list[{self.element_type}]"
        return self.name
    
    def __repr__(self):
        return f"NDType({self.kind}, {self.element_type})"

class TypeRegistry:
    """سجل الأنواع ثنائي اللغة"""
    
    def __init__(self):
        # خريطة الأنواع العربية والإنجليزية
        self.type_map = {
            # العربية
            "رقم": NDType(TypeKind.NUMBER, name="رقم"),
            "نص": NDType(TypeKind.STRING, name="نص"),
            "منطق": NDType(TypeKind.BOOLEAN, name="منطق"),
            "قائمة": NDType(TypeKind.LIST, name="قائمة"),
            "كائن": NDType(TypeKind.OBJECT, name="كائن"),
            "فراغ": NDType(TypeKind.VOID, name="فراغ"),
            
            # الإنجليزية
            "number": NDType(TypeKind.NUMBER, name="number"),
            "string": NDType(TypeKind.STRING, name="string"),
            "boolean": NDType(TypeKind.BOOLEAN, name="boolean"),
            "list": NDType(TypeKind.LIST, name="list"),
            "object": NDType(TypeKind.OBJECT, name="object"),
            "void": NDType(TypeKind.VOID, name="void"),
        }
        
        # الأنواع الافتراضية
        self.unknown_type = NDType(TypeKind.UNKNOWN, name="unknown")
        self.number_type = self.type_map["number"]
        self.string_type = self.type_map["string"]
        self.boolean_type = self.type_map["boolean"]
        self.void_type = self.type_map["void"]
    
    def get_type(self, type_name: str) -> NDType:
        """الحصول على نوع بالاسم"""
        # فحص الأنواع البسيطة أولاً
        if type_name in self.type_map:
            return self.type_map[type_name]

        # فحص القوائم المعممة
        if '[' in type_name and ']' in type_name:
            return self._parse_generic_type(type_name)

        return self.unknown_type

    def _parse_generic_type(self, type_name: str) -> NDType:
        """تحليل الأنواع المعممة مثل list[number]"""
        try:
            # استخراج النوع الأساسي ونوع العنصر
            base_type, element_part = type_name.split('[', 1)
            element_type_name = element_part.rstrip(']')

            # التحقق من النوع الأساسي
            if base_type in ['list', 'قائمة']:
                element_type = self.get_type(element_type_name)
                if element_type.kind != TypeKind.UNKNOWN:
                    return self.create_list_type(element_type)

            return self.unknown_type

        except Exception:
            return self.unknown_type
    
    def create_list_type(self, element_type: NDType) -> NDType:
        """إنشاء نوع قائمة"""
        return NDType(TypeKind.LIST, element_type=element_type, name=f"list[{element_type.name}]")
    
    def infer_type_from_value(self, value: Any) -> NDType:
        """استنتاج النوع من القيمة"""
        if isinstance(value, (int, float)):
            return self.number_type
        elif isinstance(value, str):
            return self.string_type
        elif isinstance(value, bool):
            return self.boolean_type
        elif isinstance(value, list):
            if value:
                element_type = self.infer_type_from_value(value[0])
                return self.create_list_type(element_type)
            return self.get_type("list")
        else:
            return self.unknown_type

class TypeChecker:
    """فاحص الأنواع الثابت"""
    
    def __init__(self):
        self.registry = TypeRegistry()
        self.variable_types: Dict[str, NDType] = {}
        self.function_signatures: Dict[str, Dict[str, Any]] = {}
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(self, message: str, line: int = 0, arabic_message: str = ""):
        """إضافة خطأ نوع"""
        self.errors.append({
            "message": message,
            "arabic_message": arabic_message or message,
            "line": line,
            "type": "type_error"
        })
    
    def add_warning(self, message: str, line: int = 0, arabic_message: str = ""):
        """إضافة تحذير نوع"""
        self.warnings.append({
            "message": message,
            "arabic_message": arabic_message or message,
            "line": line,
            "type": "type_warning"
        })
    
    def check_function_definition(self, func_name: str, parameters: List[tuple], return_type: Optional[NDType], body: List[Any]):
        """فحص تعريف الدالة"""
        # تسجيل توقيع الدالة
        param_types = {}
        for param_name, param_type in parameters:
            if param_type:
                param_types[param_name] = param_type
                self.variable_types[param_name] = param_type
            else:
                # استنتاج النوع من الاستخدام
                inferred_type = self._infer_parameter_type(param_name, body)
                param_types[param_name] = inferred_type
                self.variable_types[param_name] = inferred_type
        
        self.function_signatures[func_name] = {
            "parameters": param_types,
            "return_type": return_type or self.registry.unknown_type
        }
        
        # فحص جسم الدالة
        self._check_statements(body)
    
    def check_function_call(self, func_name: str, arguments: List[Any]) -> NDType:
        """فحص استدعاء الدالة"""
        if func_name not in self.function_signatures:
            self.add_error(
                f"Undefined function: {func_name}",
                arabic_message=f"دالة غير معرفة: {func_name}"
            )
            return self.registry.unknown_type
        
        signature = self.function_signatures[func_name]
        expected_params = signature["parameters"]
        
        if len(arguments) != len(expected_params):
            self.add_error(
                f"Function {func_name} expects {len(expected_params)} arguments, got {len(arguments)}",
                arabic_message=f"الدالة {func_name} تتوقع {len(expected_params)} معاملات، تم تمرير {len(arguments)}"
            )
        
        # فحص أنواع المعاملات
        for i, (arg, (param_name, expected_type)) in enumerate(zip(arguments, expected_params.items())):
            arg_type = self._infer_expression_type(arg)
            if not arg_type.is_compatible_with(expected_type):
                self.add_error(
                    f"Argument {i+1} of function {func_name}: expected {expected_type}, got {arg_type}",
                    arabic_message=f"المعامل {i+1} للدالة {func_name}: متوقع {expected_type}، تم تمرير {arg_type}"
                )
        
        return signature["return_type"]
    
    def check_assignment(self, var_name: str, value_type: NDType, declared_type: Optional[NDType] = None):
        """فحص الإسناد"""
        if declared_type:
            # فحص التوافق مع النوع المعلن
            if not value_type.is_compatible_with(declared_type):
                self.add_error(
                    f"Cannot assign {value_type} to variable {var_name} of type {declared_type}",
                    arabic_message=f"لا يمكن إسناد {value_type} للمتغير {var_name} من النوع {declared_type}"
                )
            self.variable_types[var_name] = declared_type
        else:
            # استنتاج النوع
            if var_name in self.variable_types:
                existing_type = self.variable_types[var_name]
                if not value_type.is_compatible_with(existing_type):
                    self.add_warning(
                        f"Type of variable {var_name} changed from {existing_type} to {value_type}",
                        arabic_message=f"تغير نوع المتغير {var_name} من {existing_type} إلى {value_type}"
                    )
            
            self.variable_types[var_name] = value_type
    
    def _infer_expression_type(self, expression: Any) -> NDType:
        """استنتاج نوع التعبير"""
        # هذه دالة مبسطة - في التطبيق الحقيقي ستحتاج لتحليل AST
        if hasattr(expression, 'value'):
            return self.registry.infer_type_from_value(expression.value)
        elif hasattr(expression, 'name'):
            return self.variable_types.get(expression.name, self.registry.unknown_type)
        else:
            return self.registry.unknown_type
    
    def _infer_parameter_type(self, param_name: str, body: List[Any]) -> NDType:
        """استنتاج نوع المعامل من الاستخدام"""
        # تحليل مبسط - في التطبيق الحقيقي سيكون أكثر تعقيداً
        return self.registry.unknown_type
    
    def _check_statements(self, statements: List[Any]):
        """فحص قائمة الجمل"""
        for stmt in statements:
            self._check_statement(stmt)
    
    def _check_statement(self, statement: Any):
        """فحص جملة واحدة"""
        # تطبيق مبسط - سيتم توسيعه
        pass
    
    def get_type_errors(self, language: str = "english") -> List[str]:
        """الحصول على أخطاء الأنواع"""
        if language == "arabic":
            return [error["arabic_message"] for error in self.errors]
        else:
            return [error["message"] for error in self.errors]
    
    def get_type_warnings(self, language: str = "english") -> List[str]:
        """الحصول على تحذيرات الأنواع"""
        if language == "arabic":
            return [warning["arabic_message"] for warning in self.warnings]
        else:
            return [warning["message"] for warning in self.warnings]
    
    def has_errors(self) -> bool:
        """فحص وجود أخطاء"""
        return len(self.errors) > 0
    
    def clear_errors(self):
        """مسح الأخطاء والتحذيرات"""
        self.errors.clear()
        self.warnings.clear()

class TypeInferenceEngine:
    """محرك استنتاج الأنواع"""
    
    def __init__(self, type_checker: TypeChecker):
        self.type_checker = type_checker
        self.registry = type_checker.registry
    
    def infer_function_return_type(self, func_name: str, body: List[Any]) -> NDType:
        """استنتاج نوع الإرجاع للدالة"""
        # تحليل جمل الإرجاع في جسم الدالة
        return_types = []
        
        for stmt in body:
            if self._is_return_statement(stmt):
                return_type = self._infer_return_expression_type(stmt)
                return_types.append(return_type)
        
        if not return_types:
            return self.registry.void_type
        
        # إذا كانت جميع أنواع الإرجاع متوافقة، استخدم النوع الأول
        first_type = return_types[0]
        for ret_type in return_types[1:]:
            if not first_type.is_compatible_with(ret_type):
                self.type_checker.add_warning(
                    f"Function {func_name} has inconsistent return types",
                    arabic_message=f"الدالة {func_name} لها أنواع إرجاع غير متسقة"
                )
                return self.registry.unknown_type
        
        return first_type
    
    def _is_return_statement(self, statement: Any) -> bool:
        """فحص إذا كانت الجملة جملة إرجاع"""
        # تطبيق مبسط
        return False
    
    def _infer_return_expression_type(self, return_stmt: Any) -> NDType:
        """استنتاج نوع تعبير الإرجاع"""
        # تطبيق مبسط
        return self.registry.unknown_type

# دالة مساعدة للاستخدام السريع
def create_type_checker() -> TypeChecker:
    """إنشاء فاحص أنواع جديد"""
    return TypeChecker()
