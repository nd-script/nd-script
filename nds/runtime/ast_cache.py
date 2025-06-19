#!/usr/bin/env python3
"""
نظام التخزين المؤقت للـ AST في ND-Script
AST Caching System for ND-Script
"""

import hashlib
import pickle
import functools
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import threading
import time

class ASTCache:
    """نظام تخزين مؤقت متقدم للـ AST"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}  # hash -> (ast, timestamp)
        self.access_times: Dict[str, float] = {}  # hash -> last_access_time
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
    
    def _generate_hash(self, source_code: str) -> str:
        """إنشاء hash للكود المصدري"""
        # تطبيع الكود (إزالة المسافات الزائدة والتعليقات)
        normalized = self._normalize_code(source_code)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]
    
    def _normalize_code(self, code: str) -> str:
        """تطبيع الكود لتحسين التخزين المؤقت"""
        lines = []
        for line in code.split('\n'):
            # إزالة التعليقات والمسافات الزائدة
            line = line.strip()
            if line and not line.startswith('//'):
                lines.append(line)
        return '\n'.join(lines)
    
    def _is_expired(self, timestamp: float) -> bool:
        """فحص انتهاء صلاحية العنصر"""
        return time.time() - timestamp > self.ttl_seconds
    
    def _evict_expired(self):
        """إزالة العناصر منتهية الصلاحية"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _evict_lru(self):
        """إزالة العناصر الأقل استخداماً"""
        if len(self.cache) <= self.max_size:
            return
        
        # ترتيب حسب آخر وقت وصول
        sorted_items = sorted(
            self.access_times.items(),
            key=lambda x: x[1]
        )
        
        # إزالة العناصر الأقدم
        items_to_remove = len(self.cache) - self.max_size + 1
        for key, _ in sorted_items[:items_to_remove]:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def get(self, source_code: str) -> Optional[Any]:
        """الحصول على AST من التخزين المؤقت"""
        with self.lock:
            code_hash = self._generate_hash(source_code)
            
            if code_hash in self.cache:
                ast, timestamp = self.cache[code_hash]
                
                # فحص انتهاء الصلاحية
                if self._is_expired(timestamp):
                    del self.cache[code_hash]
                    if code_hash in self.access_times:
                        del self.access_times[code_hash]
                    self.miss_count += 1
                    return None
                
                # تحديث وقت الوصول
                self.access_times[code_hash] = time.time()
                self.hit_count += 1
                return ast
            
            self.miss_count += 1
            return None
    
    def put(self, source_code: str, ast: Any):
        """إضافة AST إلى التخزين المؤقت"""
        with self.lock:
            code_hash = self._generate_hash(source_code)
            current_time = time.time()
            
            # تنظيف العناصر منتهية الصلاحية
            self._evict_expired()
            
            # إضافة العنصر الجديد
            self.cache[code_hash] = (ast, current_time)
            self.access_times[code_hash] = current_time
            
            # إزالة العناصر الزائدة
            self._evict_lru()
    
    def clear(self):
        """مسح التخزين المؤقت"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_count = 0
            self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات التخزين المؤقت"""
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "cache_size": len(self.cache),
                "max_size": self.max_size,
                "hit_count": self.hit_count,
                "miss_count": self.miss_count,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }
    
    def get_stats_report(self, language: str = "arabic") -> str:
        """تقرير إحصائيات التخزين المؤقت"""
        stats = self.get_stats()
        
        if language == "arabic":
            return f"""
📊 إحصائيات التخزين المؤقت للـ AST:
   📦 حجم التخزين: {stats['cache_size']}/{stats['max_size']}
   ✅ إصابات: {stats['hit_count']}
   ❌ إخفاقات: {stats['miss_count']}
   📈 معدل الإصابة: {stats['hit_rate']:.1f}%
   🔢 إجمالي الطلبات: {stats['total_requests']}
"""
        else:
            return f"""
📊 AST Cache Statistics:
   📦 Cache size: {stats['cache_size']}/{stats['max_size']}
   ✅ Hits: {stats['hit_count']}
   ❌ Misses: {stats['miss_count']}
   📈 Hit rate: {stats['hit_rate']:.1f}%
   🔢 Total requests: {stats['total_requests']}
"""

class FunctionCallCache:
    """تخزين مؤقت لاستدعاءات الدوال"""
    
    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
        self.lock = threading.RLock()
    
    def _generate_key(self, func_name: str, args: tuple) -> str:
        """إنشاء مفتاح للدالة والمعاملات"""
        # تحويل المعاملات إلى string قابل للـ hash
        args_str = str(args)
        return f"{func_name}:{hashlib.md5(args_str.encode()).hexdigest()[:8]}"
    
    def get(self, func_name: str, args: tuple) -> Optional[Any]:
        """الحصول على نتيجة الدالة من التخزين المؤقت"""
        with self.lock:
            key = self._generate_key(func_name, args)
            
            if key in self.cache:
                # نقل إلى نهاية القائمة (الأحدث استخداماً)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            
            return None
    
    def put(self, func_name: str, args: tuple, result: Any):
        """إضافة نتيجة الدالة إلى التخزين المؤقت"""
        with self.lock:
            key = self._generate_key(func_name, args)
            
            # إزالة العنصر إذا كان موجوداً
            if key in self.cache:
                self.access_order.remove(key)
            
            # إضافة العنصر الجديد
            self.cache[key] = result
            self.access_order.append(key)
            
            # إزالة العناصر الزائدة
            while len(self.cache) > self.max_size:
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
    
    def clear(self):
        """مسح التخزين المؤقت"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()

# مثيلات عامة للتخزين المؤقت
ast_cache = ASTCache(max_size=1000, ttl_seconds=3600)
function_cache = FunctionCallCache(max_size=500)

def cached_ast_parse(parser_func):
    """ديكوريتر للتخزين المؤقت لتحليل AST"""
    @functools.wraps(parser_func)
    def wrapper(source_code: str, *args, **kwargs):
        # محاولة الحصول من التخزين المؤقت
        cached_ast = ast_cache.get(source_code)
        if cached_ast is not None:
            return cached_ast
        
        # تحليل جديد وحفظ في التخزين المؤقت
        ast = parser_func(source_code, *args, **kwargs)
        ast_cache.put(source_code, ast)
        return ast
    
    return wrapper

def cached_function_call(func):
    """ديكوريتر للتخزين المؤقت لاستدعاءات الدوال"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # تحويل kwargs إلى tuple للتخزين المؤقت
        cache_key = (args, tuple(sorted(kwargs.items())))
        
        # محاولة الحصول من التخزين المؤقت
        cached_result = function_cache.get(func.__name__, cache_key)
        if cached_result is not None:
            return cached_result
        
        # تنفيذ الدالة وحفظ النتيجة
        result = func(*args, **kwargs)
        function_cache.put(func.__name__, cache_key, result)
        return result
    
    return wrapper

def get_cache_stats() -> str:
    """الحصول على إحصائيات جميع أنواع التخزين المؤقت"""
    return ast_cache.get_stats_report() + "\n" + "📊 Function Cache: " + str(len(function_cache.cache)) + " items"

def clear_all_caches():
    """مسح جميع أنواع التخزين المؤقت"""
    ast_cache.clear()
    function_cache.clear()
