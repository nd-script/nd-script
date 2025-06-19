#!/usr/bin/env python3
"""
نظام تجميع العمليات لـ ND-Script
Operation Batching System for ND-Script
"""

from typing import List, Dict, Any, Optional
from .ast import *

class OperationBatch:
    """مجموعة من العمليات المتشابهة"""
    
    def __init__(self, operation_type: str):
        self.operation_type = operation_type
        self.operations: List[Any] = []
        self.batch_size = 0
    
    def add_operation(self, operation: Any):
        """إضافة عملية إلى المجموعة"""
        self.operations.append(operation)
        self.batch_size += 1
    
    def can_batch_with(self, operation: Any) -> bool:
        """فحص إمكانية تجميع العملية"""
        if self.operation_type == "assignment":
            return isinstance(operation, Assignment)
        elif self.operation_type == "set_command":
            return isinstance(operation, SetCommand)
        elif self.operation_type == "show_command":
            return isinstance(operation, ShowCommand)
        return False
    
    def execute_batch(self, interpreter) -> List[Any]:
        """تنفيذ المجموعة كاملة"""
        results = []
        
        if self.operation_type == "assignment":
            # تجميع الإسنادات
            for assignment in self.operations:
                interpreter.environment.set(assignment.identifier, assignment.value.accept(interpreter))
                results.append(None)
        
        elif self.operation_type == "set_command":
            # تجميع أوامر الضبط
            for set_cmd in self.operations:
                value = set_cmd.value.accept(interpreter) if hasattr(set_cmd.value, 'accept') else set_cmd.value
                if interpreter.universe:
                    interpreter.universe.set_parameter(set_cmd.parameter, value)
                results.append(value)
        
        elif self.operation_type == "show_command":
            # تجميع أوامر العرض
            for show_cmd in self.operations:
                result = interpreter.visit_show_command(show_cmd)
                results.append(result)
        
        return results

class OperationBatcher:
    """نظام تجميع العمليات"""
    
    def __init__(self, max_batch_size: int = 10):
        self.max_batch_size = max_batch_size
        self.current_batches: Dict[str, OperationBatch] = {}
        self.batching_enabled = True
    
    def can_batch_operation(self, operation: Any) -> bool:
        """فحص إمكانية تجميع العملية"""
        if not self.batching_enabled:
            return False
        
        # العمليات القابلة للتجميع
        batchable_types = [
            Assignment,
            SetCommand,
            ShowCommand
        ]
        
        return any(isinstance(operation, op_type) for op_type in batchable_types)
    
    def get_operation_type(self, operation: Any) -> str:
        """الحصول على نوع العملية"""
        if isinstance(operation, Assignment):
            return "assignment"
        elif isinstance(operation, SetCommand):
            return "set_command"
        elif isinstance(operation, ShowCommand):
            return "show_command"
        return "unknown"
    
    def add_to_batch(self, operation: Any) -> bool:
        """إضافة عملية إلى المجموعة"""
        if not self.can_batch_operation(operation):
            return False
        
        op_type = self.get_operation_type(operation)
        
        # إنشاء مجموعة جديدة إذا لم تكن موجودة
        if op_type not in self.current_batches:
            self.current_batches[op_type] = OperationBatch(op_type)
        
        batch = self.current_batches[op_type]
        
        # فحص إمكانية الإضافة
        if batch.batch_size >= self.max_batch_size:
            return False
        
        if not batch.can_batch_with(operation):
            return False
        
        batch.add_operation(operation)
        return True
    
    def should_flush_batch(self, op_type: str) -> bool:
        """فحص ضرورة تفريغ المجموعة"""
        if op_type not in self.current_batches:
            return False
        
        batch = self.current_batches[op_type]
        return batch.batch_size >= self.max_batch_size
    
    def flush_batch(self, op_type: str, interpreter) -> List[Any]:
        """تفريغ وتنفيذ المجموعة"""
        if op_type not in self.current_batches:
            return []
        
        batch = self.current_batches[op_type]
        results = batch.execute_batch(interpreter)
        
        # إعادة تعيين المجموعة
        self.current_batches[op_type] = OperationBatch(op_type)
        
        return results
    
    def flush_all_batches(self, interpreter) -> Dict[str, List[Any]]:
        """تفريغ جميع المجموعات"""
        results = {}
        
        for op_type in list(self.current_batches.keys()):
            if self.current_batches[op_type].batch_size > 0:
                results[op_type] = self.flush_batch(op_type, interpreter)
        
        return results
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """إحصائيات التجميع"""
        stats = {
            "enabled": self.batching_enabled,
            "max_batch_size": self.max_batch_size,
            "current_batches": {}
        }
        
        for op_type, batch in self.current_batches.items():
            stats["current_batches"][op_type] = {
                "size": batch.batch_size,
                "operations": len(batch.operations)
            }
        
        return stats
    
    def enable_batching(self):
        """تفعيل التجميع"""
        self.batching_enabled = True
    
    def disable_batching(self):
        """تعطيل التجميع"""
        self.batching_enabled = False
        # تفريغ المجموعات الحالية
        self.current_batches.clear()

class BatchedExecutor:
    """منفذ العمليات المجمعة"""
    
    def __init__(self, interpreter, batch_size: int = 10):
        self.interpreter = interpreter
        self.batcher = OperationBatcher(max_batch_size=batch_size)
        self.execution_stats = {
            "batched_operations": 0,
            "individual_operations": 0,
            "batch_flushes": 0
        }
    
    def execute_operation(self, operation: Any) -> Any:
        """تنفيذ عملية مع إمكانية التجميع"""
        # محاولة إضافة إلى المجموعة
        if self.batcher.add_to_batch(operation):
            self.execution_stats["batched_operations"] += 1
            
            # فحص ضرورة التفريغ
            op_type = self.batcher.get_operation_type(operation)
            if self.batcher.should_flush_batch(op_type):
                results = self.batcher.flush_batch(op_type, self.interpreter)
                self.execution_stats["batch_flushes"] += 1
                return results[-1] if results else None
            
            return None  # العملية في المجموعة، لم تنفذ بعد
        
        else:
            # تنفيذ فردي
            self.execution_stats["individual_operations"] += 1
            return operation.accept(self.interpreter)
    
    def flush_pending_operations(self) -> Dict[str, List[Any]]:
        """تفريغ العمليات المعلقة"""
        results = self.batcher.flush_all_batches(self.interpreter)
        self.execution_stats["batch_flushes"] += len(results)
        return results
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """إحصائيات التنفيذ"""
        total_ops = self.execution_stats["batched_operations"] + self.execution_stats["individual_operations"]
        batch_ratio = (self.execution_stats["batched_operations"] / total_ops * 100) if total_ops > 0 else 0
        
        return {
            **self.execution_stats,
            "total_operations": total_ops,
            "batch_ratio": batch_ratio,
            "batcher_stats": self.batcher.get_batch_stats()
        }

# دالة مساعدة للاستخدام السريع
def create_batched_executor(interpreter, batch_size: int = 10) -> BatchedExecutor:
    """إنشاء منفذ عمليات مجمعة"""
    return BatchedExecutor(interpreter, batch_size)
