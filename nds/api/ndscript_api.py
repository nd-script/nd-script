#!/usr/bin/env python3
"""
واجهة برمجة التطبيقات الرئيسية لـ ND-Script
Main Python API for ND-Script Integration
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json

# إضافة مسار nds للاستيراد
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.interpreter import NDScriptInterpreter
from runtime.errors import NDScriptError as CoreNDScriptError
from runtime.type_system import create_type_checker

class NDScriptError(Exception):
    """خطأ ND-Script للواجهة العامة"""
    def __init__(self, message: str, line: int = 0, column: int = 0, error_type: str = "runtime"):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.error_type = error_type
    
    def __str__(self):
        if self.line > 0:
            return f"ND-Script {self.error_type} error at line {self.line}: {self.message}"
        return f"ND-Script {self.error_type} error: {self.message}"

@dataclass
class ExecutionResult:
    """نتيجة تنفيذ الكود"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: float = 0.0
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class NDScriptSession:
    """جلسة ND-Script للتنفيذ التفاعلي"""
    
    def __init__(self, enable_parallel: bool = True, enable_bytecode: bool = True):
        self.interpreter = NDScriptInterpreter()
        self.type_checker = create_type_checker()
        self.session_id = id(self)
        self.execution_history: List[Dict[str, Any]] = []
        
        # إعدادات الأداء
        if enable_bytecode:
            self.interpreter.enable_bytecode()
        else:
            self.interpreter.disable_bytecode()
        
        self.enable_parallel = enable_parallel
        
        # إحصائيات الجلسة
        self.stats = {
            "executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0.0,
            "functions_defined": 0,
            "variables_created": 0
        }
    
    def execute(self, code: str, filename: str = "<interactive>") -> ExecutionResult:
        """تنفيذ كود ND-Script"""
        import time
        
        start_time = time.perf_counter()
        
        try:
            # فحص النحو أولاً
            syntax_errors = self.validate_syntax(code)
            if syntax_errors:
                return ExecutionResult(
                    success=False,
                    error=f"Syntax errors: {'; '.join(syntax_errors)}",
                    execution_time=0.0
                )
            
            # تنفيذ الكود
            result = self.interpreter.interpret(code, filename)
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            # تحديث الإحصائيات
            self.stats["executions"] += 1
            self.stats["successful_executions"] += 1
            self.stats["total_execution_time"] += execution_time
            
            # حفظ في التاريخ
            self.execution_history.append({
                "code": code,
                "result": result,
                "execution_time": execution_time,
                "timestamp": time.time(),
                "success": True
            })
            
            return ExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time,
                memory_usage=self._get_memory_usage()
            )
            
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            # تحديث الإحصائيات
            self.stats["executions"] += 1
            self.stats["failed_executions"] += 1
            
            # حفظ في التاريخ
            self.execution_history.append({
                "code": code,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time(),
                "success": False
            })
            
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def execute_file(self, filepath: str) -> ExecutionResult:
        """تنفيذ ملف ND-Script"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.execute(code, filepath)
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                error=f"File not found: {filepath}"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Error reading file {filepath}: {e}"
            )
    
    def validate_syntax(self, code: str) -> List[str]:
        """فحص النحو"""
        try:
            # محاولة تحليل الكود
            self.interpreter.parser.parse(code)
            return []
        except Exception as e:
            return [str(e)]
    
    def get_variables(self) -> Dict[str, Any]:
        """الحصول على المتغيرات المعرفة"""
        return self.interpreter.environment.get_all_variables()
    
    def get_functions(self) -> Dict[str, Dict[str, Any]]:
        """الحصول على الدوال المعرفة"""
        functions = {}
        for name, func_info in self.interpreter.functions.items():
            functions[name] = {
                "name": name,
                "parameters": func_info.get("parameters", []),
                "body_length": len(func_info.get("body", [])),
                "defined_at": func_info.get("defined_at", "unknown")
            }
        return functions
    
    def clear_session(self):
        """مسح الجلسة"""
        self.interpreter = NDScriptInterpreter()
        self.execution_history.clear()
        self.stats = {
            "executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0.0,
            "functions_defined": 0,
            "variables_created": 0
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """إحصائيات الجلسة"""
        return {
            **self.stats,
            "session_id": self.session_id,
            "history_length": len(self.execution_history),
            "average_execution_time": (
                self.stats["total_execution_time"] / self.stats["executions"]
                if self.stats["executions"] > 0 else 0.0
            ),
            "success_rate": (
                self.stats["successful_executions"] / self.stats["executions"] * 100
                if self.stats["executions"] > 0 else 0.0
            )
        }
    
    def _get_memory_usage(self) -> float:
        """الحصول على استهلاك الذاكرة"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

class NDScript:
    """الواجهة الرئيسية لـ ND-Script"""
    
    @staticmethod
    def create_session(**kwargs) -> NDScriptSession:
        """إنشاء جلسة جديدة"""
        return NDScriptSession(**kwargs)
    
    @staticmethod
    def execute_code(code: str, **kwargs) -> ExecutionResult:
        """تنفيذ كود مباشر"""
        session = NDScriptSession(**kwargs)
        return session.execute(code)
    
    @staticmethod
    def execute_file(filepath: str, **kwargs) -> ExecutionResult:
        """تنفيذ ملف"""
        session = NDScriptSession(**kwargs)
        return session.execute_file(filepath)
    
    @staticmethod
    def validate_syntax(code: str) -> List[str]:
        """فحص النحو"""
        session = NDScriptSession()
        return session.validate_syntax(code)
    
    @staticmethod
    def get_version() -> str:
        """الحصول على الإصدار"""
        return "2.0.0"
    
    @staticmethod
    def get_language_info() -> Dict[str, Any]:
        """معلومات اللغة"""
        return {
            "name": "ND-Script",
            "version": "2.0.0",
            "description": "Bilingual Domain-Specific Language for Quantum Fractal Universe Simulation",
            "supported_languages": ["Arabic", "English"],
            "features": [
                "Bilingual syntax",
                "Type system",
                "Parallel processing",
                "Bytecode compilation",
                "Interactive debugging",
                "Performance profiling"
            ]
        }

# دوال مساعدة للاستخدام السريع
def create_session(**kwargs) -> NDScriptSession:
    """إنشاء جلسة ND-Script"""
    return NDScript.create_session(**kwargs)

def execute_code(code: str, **kwargs) -> ExecutionResult:
    """تنفيذ كود ND-Script"""
    return NDScript.execute_code(code, **kwargs)

def execute_file(filepath: str, **kwargs) -> ExecutionResult:
    """تنفيذ ملف ND-Script"""
    return NDScript.execute_file(filepath, **kwargs)

def get_version() -> str:
    """الحصول على إصدار ND-Script"""
    return NDScript.get_version()

def list_functions(session: NDScriptSession) -> List[str]:
    """قائمة الدوال المعرفة"""
    return list(session.get_functions().keys())

def get_function_signature(session: NDScriptSession, function_name: str) -> Optional[Dict[str, Any]]:
    """الحصول على توقيع الدالة"""
    functions = session.get_functions()
    return functions.get(function_name)

def validate_syntax(code: str) -> List[str]:
    """فحص نحو الكود"""
    return NDScript.validate_syntax(code)

def format_code(code: str) -> str:
    """تنسيق الكود (تطبيق أساسي)"""
    # تطبيق بسيط للتنسيق
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue
        
        # تقليل المسافة البادئة للأقواس المغلقة
        if stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        # إضافة المسافة البادئة
        formatted_line = '    ' * indent_level + stripped
        formatted_lines.append(formatted_line)
        
        # زيادة المسافة البادئة للأقواس المفتوحة
        if stripped.endswith('{'):
            indent_level += 1
    
    return '\n'.join(formatted_lines)

def get_performance_stats(session: NDScriptSession) -> Dict[str, Any]:
    """إحصائيات الأداء"""
    session_stats = session.get_session_stats()

    # إضافة إحصائيات المفسر
    try:
        if hasattr(session.interpreter, 'get_bytecode_stats'):
            bytecode_stats = session.interpreter.get_bytecode_stats()
            session_stats["bytecode"] = bytecode_stats

        if hasattr(session.interpreter, 'get_parallel_stats'):
            parallel_stats = session.interpreter.get_parallel_stats()
            session_stats["parallel"] = parallel_stats
    except Exception as e:
        session_stats["stats_error"] = str(e)

    return session_stats
