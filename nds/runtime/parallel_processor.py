#!/usr/bin/env python3
"""
معالج المعالجة المتوازية لـ ND-Script
Parallel Processing Engine for ND-Script
"""

import concurrent.futures
import threading
import multiprocessing
import time
from typing import List, Any, Callable, Dict, Optional
from dataclasses import dataclass

@dataclass
class ParallelConfig:
    """إعدادات المعالجة المتوازية"""
    max_workers: Optional[int] = None
    chunk_size: int = 10
    use_threads: bool = True  # True للخيوط، False للعمليات
    timeout: Optional[float] = None

class ParallelProcessor:
    """معالج المعالجة المتوازية"""
    
    def __init__(self, config: ParallelConfig = None):
        self.config = config or ParallelConfig()
        self.stats = {
            "parallel_executions": 0,
            "sequential_executions": 0,
            "total_time_parallel": 0.0,
            "total_time_sequential": 0.0,
            "threads_used": 0,
            "processes_used": 0
        }
        
        # تحديد عدد العمال الافتراضي
        if self.config.max_workers is None:
            self.config.max_workers = min(32, (multiprocessing.cpu_count() or 1) + 4)
    
    def execute_parallel_for(self, start: int, end: int, step: int,
                           body_func: Callable[[int], Any],
                           variable_name: str = "i") -> List[Any]:
        """تنفيذ حلقة for بالتوازي مع اكتشاف العمل التلقائي"""

        # إنشاء قائمة القيم
        values = list(range(start, end, step))

        # اكتشاف نوع العمل تلقائياً
        workload_complexity = self._detect_workload_complexity(body_func, values[:min(3, len(values))])

        # تحديد إذا كانت المعالجة المتوازية مفيدة
        should_parallelize = self._should_use_parallel_execution(values, workload_complexity)

        if not should_parallelize:
            return self._execute_sequential(values, body_func)

        start_time = time.perf_counter()

        try:
            # تحسين الإعدادات حسب العمل
            optimized_config = self.optimize_config_for_workload(len(values), workload_complexity)
            original_config = self.config
            self.config = optimized_config

            if self.config.use_threads:
                results = self._execute_with_threads(values, body_func)
                self.stats["threads_used"] += self.config.max_workers
            else:
                results = self._execute_with_processes(values, body_func)
                self.stats["processes_used"] += self.config.max_workers

            # استعادة الإعدادات الأصلية
            self.config = original_config

            end_time = time.perf_counter()
            self.stats["parallel_executions"] += 1
            self.stats["total_time_parallel"] += (end_time - start_time)

            return results

        except Exception as e:
            print(f"Parallel execution failed, falling back to sequential: {e}")
            # استعادة الإعدادات الأصلية في حالة الخطأ
            self.config = original_config
            return self._execute_sequential(values, body_func)
    
    def _execute_with_threads(self, values: List[int], body_func: Callable[[int], Any]) -> List[Any]:
        """تنفيذ باستخدام الخيوط"""
        results = [None] * len(values)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # إرسال المهام
            future_to_index = {
                executor.submit(self._safe_execute, body_func, value): i 
                for i, value in enumerate(values)
            }
            
            # جمع النتائج
            for future in concurrent.futures.as_completed(future_to_index, timeout=self.config.timeout):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    print(f"Thread execution error for index {index}: {e}")
                    results[index] = None
        
        return results
    
    def _execute_with_processes(self, values: List[int], body_func: Callable[[int], Any]) -> List[Any]:
        """تنفيذ باستخدام العمليات"""
        results = [None] * len(values)
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # إرسال المهام
            future_to_index = {
                executor.submit(self._safe_execute, body_func, value): i 
                for i, value in enumerate(values)
            }
            
            # جمع النتائج
            for future in concurrent.futures.as_completed(future_to_index, timeout=self.config.timeout):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    print(f"Process execution error for index {index}: {e}")
                    results[index] = None
        
        return results
    
    def _execute_sequential(self, values: List[int], body_func: Callable[[int], Any]) -> List[Any]:
        """تنفيذ تسلسلي للمقارنة"""
        start_time = time.perf_counter()
        
        results = []
        for value in values:
            try:
                result = self._safe_execute(body_func, value)
                results.append(result)
            except Exception as e:
                print(f"Sequential execution error for value {value}: {e}")
                results.append(None)
        
        end_time = time.perf_counter()
        self.stats["sequential_executions"] += 1
        self.stats["total_time_sequential"] += (end_time - start_time)
        
        return results
    
    def _safe_execute(self, func: Callable[[int], Any], value: int) -> Any:
        """تنفيذ آمن للدالة"""
        try:
            return func(value)
        except Exception as e:
            print(f"Execution error for value {value}: {e}")
            return None
    
    def benchmark_parallel_vs_sequential(self, start: int, end: int, step: int, 
                                       body_func: Callable[[int], Any], 
                                       iterations: int = 3) -> Dict[str, Any]:
        """مقارنة الأداء بين المعالجة المتوازية والتسلسلية"""
        
        values = list(range(start, end, step))
        
        # اختبار التنفيذ التسلسلي
        sequential_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            self._execute_sequential(values, body_func)
            end_time = time.perf_counter()
            sequential_times.append(end_time - start_time)
        
        # اختبار التنفيذ المتوازي
        parallel_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            if self.config.use_threads:
                self._execute_with_threads(values, body_func)
            else:
                self._execute_with_processes(values, body_func)
            end_time = time.perf_counter()
            parallel_times.append(end_time - start_time)
        
        # حساب الإحصائيات
        avg_sequential = sum(sequential_times) / len(sequential_times)
        avg_parallel = sum(parallel_times) / len(parallel_times)
        speedup = avg_sequential / avg_parallel if avg_parallel > 0 else 0
        efficiency = speedup / self.config.max_workers * 100
        
        return {
            "sequential_avg": avg_sequential,
            "parallel_avg": avg_parallel,
            "speedup": speedup,
            "efficiency": efficiency,
            "improvement_percent": ((avg_sequential - avg_parallel) / avg_sequential * 100) if avg_sequential > 0 else 0,
            "values_count": len(values),
            "workers": self.config.max_workers,
            "execution_mode": "threads" if self.config.use_threads else "processes"
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الأداء"""
        total_executions = self.stats["parallel_executions"] + self.stats["sequential_executions"]
        
        avg_parallel_time = (self.stats["total_time_parallel"] / self.stats["parallel_executions"]) if self.stats["parallel_executions"] > 0 else 0
        avg_sequential_time = (self.stats["total_time_sequential"] / self.stats["sequential_executions"]) if self.stats["sequential_executions"] > 0 else 0
        
        return {
            **self.stats,
            "total_executions": total_executions,
            "avg_parallel_time": avg_parallel_time,
            "avg_sequential_time": avg_sequential_time,
            "parallel_ratio": (self.stats["parallel_executions"] / total_executions * 100) if total_executions > 0 else 0,
            "config": {
                "max_workers": self.config.max_workers,
                "chunk_size": self.config.chunk_size,
                "use_threads": self.config.use_threads,
                "cpu_count": multiprocessing.cpu_count()
            }
        }
    
    def optimize_config_for_workload(self, workload_size: int, complexity: str = "medium") -> ParallelConfig:
        """تحسين الإعدادات حسب حجم العمل"""
        
        # تحديد حجم القطعة المناسب
        if complexity == "light":
            chunk_size = max(50, workload_size // 20)
        elif complexity == "heavy":
            chunk_size = max(5, workload_size // 100)
        else:  # medium
            chunk_size = max(10, workload_size // 50)
        
        # تحديد نوع المعالجة
        use_threads = complexity in ["light", "medium"]
        
        # تحديد عدد العمال
        if workload_size < 100:
            max_workers = min(4, multiprocessing.cpu_count())
        elif workload_size < 1000:
            max_workers = min(8, multiprocessing.cpu_count())
        else:
            max_workers = multiprocessing.cpu_count()
        
        return ParallelConfig(
            max_workers=max_workers,
            chunk_size=chunk_size,
            use_threads=use_threads,
            timeout=30.0  # 30 ثانية timeout
        )

    def _detect_workload_complexity(self, body_func: Callable[[int], Any], sample_values: List[int]) -> str:
        """اكتشاف تعقيد العمل تلقائياً"""
        if not sample_values:
            return "light"

        # قياس وقت تنفيذ عينة صغيرة
        total_time = 0
        sample_count = 0

        for value in sample_values:
            try:
                start_time = time.perf_counter()
                self._safe_execute(body_func, value)
                end_time = time.perf_counter()

                total_time += (end_time - start_time)
                sample_count += 1
            except Exception:
                continue

        if sample_count == 0:
            return "light"

        avg_time = total_time / sample_count

        # تصنيف التعقيد حسب الوقت
        if avg_time < 0.001:  # أقل من 1ms
            return "light"
        elif avg_time < 0.01:  # أقل من 10ms
            return "medium"
        else:  # أكثر من 10ms
            return "heavy"

    def _should_use_parallel_execution(self, values: List[int], complexity: str) -> bool:
        """تحديد إذا كانت المعالجة المتوازية مفيدة"""

        # العوامل المؤثرة في القرار
        value_count = len(values)

        # قواعد القرار
        if complexity == "light":
            # للأعمال الخفيفة، نحتاج عدد كبير من القيم
            return value_count >= 100
        elif complexity == "medium":
            # للأعمال المتوسطة، نحتاج عدد متوسط
            return value_count >= 20
        else:  # heavy
            # للأعمال الثقيلة، حتى العدد القليل مفيد
            return value_count >= 5

    def get_workload_recommendation(self, values: List[int], body_func: Callable[[int], Any]) -> Dict[str, Any]:
        """الحصول على توصيات للعمل"""

        complexity = self._detect_workload_complexity(body_func, values[:min(5, len(values))])
        should_parallelize = self._should_use_parallel_execution(values, complexity)
        optimized_config = self.optimize_config_for_workload(len(values), complexity)

        return {
            "workload_size": len(values),
            "complexity": complexity,
            "should_parallelize": should_parallelize,
            "recommended_config": {
                "max_workers": optimized_config.max_workers,
                "chunk_size": optimized_config.chunk_size,
                "use_threads": optimized_config.use_threads
            },
            "expected_benefit": self._estimate_parallel_benefit(len(values), complexity)
        }

    def _estimate_parallel_benefit(self, value_count: int, complexity: str) -> str:
        """تقدير الفائدة من المعالجة المتوازية"""

        if complexity == "heavy" and value_count >= 10:
            return "high"
        elif complexity == "medium" and value_count >= 50:
            return "medium"
        elif complexity == "light" and value_count >= 200:
            return "low"
        else:
            return "minimal"

class ThreadSafeUniverseWrapper:
    """غلاف آمن للخيوط للكون الكمي"""
    
    def __init__(self, universe):
        self.universe = universe
        self._lock = threading.RLock()
        self._local_data = threading.local()
    
    def safe_evolve(self, steps: int = 1):
        """تطور آمن للخيوط"""
        with self._lock:
            if hasattr(self.universe, 'evolve'):
                return self.universe.evolve(steps)
            return None
    
    def safe_set_parameter(self, parameter: str, value: Any):
        """ضبط معامل آمن للخيوط"""
        with self._lock:
            if hasattr(self.universe, 'set_parameter'):
                return self.universe.set_parameter(parameter, value)
            return None
    
    def safe_get_state(self):
        """الحصول على الحالة بشكل آمن"""
        with self._lock:
            if hasattr(self.universe, 'get_state'):
                return self.universe.get_state()
            return None
    
    def create_local_copy(self):
        """إنشاء نسخة محلية للخيط"""
        if not hasattr(self._local_data, 'universe_copy'):
            with self._lock:
                # إنشاء نسخة من الكون للخيط الحالي
                if hasattr(self.universe, 'copy'):
                    self._local_data.universe_copy = self.universe.copy()
                else:
                    self._local_data.universe_copy = self.universe
        
        return self._local_data.universe_copy

# دالة مساعدة للاستخدام السريع
def create_parallel_processor(max_workers: int = None, use_threads: bool = True) -> ParallelProcessor:
    """إنشاء معالج متوازي"""
    config = ParallelConfig(max_workers=max_workers, use_threads=use_threads)
    return ParallelProcessor(config)

def create_thread_safe_universe(universe) -> ThreadSafeUniverseWrapper:
    """إنشاء غلاف آمن للخيوط للكون"""
    return ThreadSafeUniverseWrapper(universe)
