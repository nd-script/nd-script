"""
ND-Script Environment Management
Handles variable scoping and storage
"""

from typing import Any, Dict, Optional, List


class Environment:
    """Environment for variable storage and scoping - Performance Optimized"""

    __slots__ = ['parent', 'variables', '_var_cache', '_cache_hits', '_cache_misses', '_flattened_vars']

    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        # تخزين مؤقت للمتغيرات المستخدمة بكثرة
        self._var_cache: Dict[str, Any] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        # متغيرات مسطحة للوصول السريع
        self._flattened_vars: Optional[Dict[str, Any]] = None
    
    def define(self, name: str, value: Any) -> None:
        """Define a new variable in current scope"""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Get variable value with caching optimization"""
        # فحص التخزين المؤقت أولاً
        if name in self._var_cache:
            self._cache_hits += 1
            return self._var_cache[name]

        # البحث في النطاق الحالي
        if name in self.variables:
            value = self.variables[name]
            # إضافة إلى التخزين المؤقت
            self._var_cache[name] = value
            self._cache_misses += 1
            return value

        # البحث في النطاقات الأب
        if self.parent:
            try:
                value = self.parent.get(name)
                # إضافة إلى التخزين المؤقت
                self._var_cache[name] = value
                return value
            except NameError:
                pass

        raise NameError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: Any) -> None:
        """Set variable value with cache invalidation"""
        # إبطال التخزين المؤقت للمتغير
        if name in self._var_cache:
            del self._var_cache[name]

        # إبطال المتغيرات المسطحة
        self._flattened_vars = None

        # Try to update existing variable in current or parent scope
        if name in self.variables:
            self.variables[name] = value
            return

        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return

        # Create new variable in current scope
        self.variables[name] = value
    
    def has(self, name: str) -> bool:
        """Check if variable exists in current or parent scopes"""
        if name in self.variables:
            return True
        
        if self.parent:
            return self.parent.has(name)
        
        return False
    
    def create_child(self) -> 'Environment':
        """Create a child environment for new scope"""
        return Environment(parent=self)
    
    def get_all_variables(self) -> Dict[str, Any]:
        """Get all variables from current and parent scopes with caching"""
        if self._flattened_vars is not None:
            return self._flattened_vars.copy()

        all_vars = {}

        # Start with parent variables
        if self.parent:
            all_vars.update(self.parent.get_all_variables())

        # Override with current scope variables
        all_vars.update(self.variables)

        # تخزين مؤقت للمتغيرات المسطحة
        self._flattened_vars = all_vars.copy()

        return all_vars

    def get_fast(self, name: str, default: Any = None) -> Any:
        """وصول سريع للمتغيرات مع قيمة افتراضية"""
        try:
            return self.get(name)
        except NameError:
            return default

    def bulk_get(self, names: List[str]) -> Dict[str, Any]:
        """الحصول على عدة متغيرات دفعة واحدة"""
        result = {}
        for name in names:
            try:
                result[name] = self.get(name)
            except NameError:
                pass
        return result

    def get_cache_stats(self) -> Dict[str, int]:
        """إحصائيات التخزين المؤقت"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self._var_cache)
        }
    
    def clear(self) -> None:
        """Clear all variables in current scope"""
        self.variables.clear()
        self._var_cache.clear()
        self._flattened_vars = None
        self._cache_hits = 0
        self._cache_misses = 0
    
    def __str__(self) -> str:
        """String representation of environment"""
        return f"Environment({self.variables})"
    
    def __repr__(self) -> str:
        return self.__str__()


class GlobalEnvironment(Environment):
    """Global environment with built-in functions and constants"""
    
    def __init__(self):
        super().__init__()
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in functions and constants"""
        # Mathematical constants
        self.define("π", 3.141592653589793)
        self.define("pi", 3.141592653589793)
        self.define("e", 2.718281828459045)
        self.define("φ", 1.618033988749895)  # Golden ratio
        self.define("phi", 1.618033988749895)
        
        # Physical constants (in appropriate units)
        self.define("c", 299792458)  # Speed of light (m/s)
        self.define("h", 6.62607015e-34)  # Planck constant
        self.define("ħ", 1.0545718176461565e-34)  # Reduced Planck constant
        self.define("hbar", 1.0545718176461565e-34)
        
        # Built-in functions
        self.define("abs", abs)
        self.define("min", min)
        self.define("max", max)
        self.define("round", round)
        self.define("len", len)
        
        # Mathematical functions
        import math
        self.define("sin", math.sin)
        self.define("cos", math.cos)
        self.define("tan", math.tan)
        self.define("sqrt", math.sqrt)
        self.define("log", math.log)
        self.define("exp", math.exp)
        self.define("pow", pow)
        
        # Arabic aliases for common functions
        self.define("جذر", math.sqrt)  # sqrt
        self.define("لوغ", math.log)   # log
        self.define("أس", math.exp)    # exp
        self.define("قوة", pow)        # power
        self.define("مطلق", abs)       # absolute
        self.define("أدنى", min)       # minimum
        self.define("أعلى", max)       # maximum
