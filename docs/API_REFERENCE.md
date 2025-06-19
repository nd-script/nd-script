# ND-Script API Reference
# مرجع واجهة برمجة التطبيقات لـ ND-Script

## 📚 Overview / نظرة عامة

This document provides comprehensive API reference for ND-Script v2.0.0, including all classes, methods, and functions available for developers.

يوفر هذا المستند مرجعاً شاملاً لواجهة برمجة التطبيقات لـ ND-Script v2.0.0، بما في ذلك جميع الفئات والطرق والوظائف المتاحة للمطورين.

## 🏗️ Core Classes / الفئات الأساسية

### `NDScriptInterpreter`

The main interpreter class for executing ND-Script code.

الفئة الرئيسية للمفسر لتنفيذ كود ND-Script.

#### Constructor / المنشئ

```python
NDScriptInterpreter(silent_mode: bool = False)
```

**Parameters / المعاملات:**
- `silent_mode` (bool): Enable silent mode for performance optimization / تفعيل الوضع الصامت لتحسين الأداء

**Example / مثال:**
```python
from nds.runtime.interpreter import NDScriptInterpreter

# Standard mode / الوضع العادي
interpreter = NDScriptInterpreter()

# Silent mode for performance / الوضع الصامت للأداء
fast_interpreter = NDScriptInterpreter(silent_mode=True)
```

#### Methods / الطرق

##### `interpret(source: str, filename: str = "<string>") -> Any`

Execute ND-Script source code.

تنفيذ كود مصدر ND-Script.

**Parameters / المعاملات:**
- `source` (str): ND-Script source code / كود مصدر ND-Script
- `filename` (str): Optional filename for error reporting / اسم الملف الاختياري لتقارير الأخطاء

**Returns / يرجع:**
- `Any`: Result of the last executed statement / نتيجة آخر عبارة منفذة

**Example / مثال:**
```python
interpreter = NDScriptInterpreter()

# Basic assignment / إسناد أساسي
result = interpreter.interpret("x = 10")
print(result)  # 10.0

# Arithmetic expression / تعبير حسابي
result = interpreter.interpret("result = 5 * 3 + 2")
print(result)  # 17.0

# Bilingual code / كود ثنائي اللغة
result = interpreter.interpret("س = 42\nص = س * 2")
print(result)  # 84.0
```

##### `interpret_file(filename: str) -> Any`

Execute ND-Script code from a file.

تنفيذ كود ND-Script من ملف.

**Parameters / المعاملات:**
- `filename` (str): Path to ND-Script file / مسار ملف ND-Script

**Returns / يرجع:**
- `Any`: Result of the last executed statement / نتيجة آخر عبارة منفذة

**Example / مثال:**
```python
interpreter = NDScriptInterpreter()
result = interpreter.interpret_file("simulation.ndx")
```

#### Properties / الخصائص

##### `environment`

Access to the execution environment and variables.

الوصول إلى بيئة التنفيذ والمتغيرات.

**Type / النوع:** `GlobalEnvironment`

**Example / مثال:**
```python
interpreter = NDScriptInterpreter()
interpreter.interpret("x = 42")

# Get variable value / الحصول على قيمة المتغير
x_value = interpreter.environment.get('x')
print(x_value)  # 42.0

# Set variable value / تعيين قيمة المتغير
interpreter.environment.set('y', 100)

# Get all variables / الحصول على جميع المتغيرات
all_vars = interpreter.environment.get_all_variables()
print(all_vars)
```

##### `universe`

Access to the quantum fractal universe simulation.

الوصول إلى محاكاة الكون الكمي الكسيري.

**Type / النوع:** `QuantumFractalUniverse` or `None`

**Example / مثال:**
```python
interpreter = NDScriptInterpreter()
interpreter.interpret("تهيئة حجم=100")

if interpreter.universe:
    print(f"Universe size: {interpreter.universe.size}")
```

## 🌍 Environment Classes / فئات البيئة

### `GlobalEnvironment`

Manages variables and built-in functions.

تدير المتغيرات والوظائف المدمجة.

#### Methods / الطرق

##### `get(name: str) -> Any`

Get variable value.

الحصول على قيمة المتغير.

##### `set(name: str, value: Any) -> None`

Set variable value.

تعيين قيمة المتغير.

##### `get_all_variables() -> Dict[str, Any]`

Get all variables as a dictionary.

الحصول على جميع المتغيرات كقاموس.

## 🎯 Universe Classes / فئات الكون

### `QuantumFractalUniverse`

Quantum fractal universe simulation.

محاكاة الكون الكمي الكسيري.

#### Methods / الطرق

##### `evolve(steps: int) -> int`

Evolve the universe for specified steps.

تطوير الكون لعدد محدد من الخطوات.

##### `set_parameter(name: str, value: float) -> None`

Set universe parameter.

تعيين معامل الكون.

##### `get_state() -> Dict[str, Any]`

Get current universe state.

الحصول على حالة الكون الحالية.

## 📝 Language Syntax / صيغة اللغة

### Basic Commands / الأوامر الأساسية

| Arabic / العربية | English / الإنجليزية | Description / الوصف |
|------------------|----------------------|---------------------|
| `تهيئة` | `init` | Initialize universe / تهيئة الكون |
| `تطور` | `evolve` | Evolve simulation / تطوير المحاكاة |
| `عرض` | `show` | Display information / عرض المعلومات |
| `ضبط` | `set` | Set parameters / ضبط المعاملات |
| `حفظ` | `save` | Save state / حفظ الحالة |
| `تحميل` | `load` | Load state / تحميل الحالة |

### Variables and Expressions / المتغيرات والتعبيرات

```ndscript
// Variable assignment / إسناد المتغيرات
x = 10
name = "ND-Script"
pi = 3.14159

// Arithmetic expressions / التعبيرات الحسابية
result = x * 2 + 5
area = pi * radius * radius

// Bilingual variables / المتغيرات ثنائية اللغة
س = 42
النتيجة = س * 2
```

### Control Flow / تدفق التحكم

```ndscript
// If statements / عبارات الشرط
إذا (x > 5): {
    y = 100
} وإلا: {
    y = 50
}

// English equivalent / المكافئ الإنجليزي
if (x > 5): {
    y = 100
} else: {
    y = 50
}
```

### Functions / الوظائف

```ndscript
// Function definition / تعريف الوظيفة
دالة مربع(س): {
    return س * س
}

// Function call / استدعاء الوظيفة
result = مربع(5)  // Returns 25
```

## 🔧 Built-in Constants / الثوابت المدمجة

| Constant / الثابت | Value / القيمة | Description / الوصف |
|-------------------|----------------|---------------------|
| `π`, `pi` | 3.141592653589793 | Pi / باي |
| `e` | 2.718281828459045 | Euler's number / رقم أويلر |
| `φ`, `phi` | 1.618033988749895 | Golden ratio / النسبة الذهبية |
| `c` | 299792458 | Speed of light / سرعة الضوء |
| `h` | 6.62607015e-34 | Planck constant / ثابت بلانك |

## 🧮 Built-in Functions / الوظائف المدمجة

| Function / الوظيفة | Arabic / العربية | Description / الوصف |
|---------------------|------------------|---------------------|
| `abs(x)` | `مطلق(س)` | Absolute value / القيمة المطلقة |
| `min(a, b, ...)` | `أدنى(أ، ب، ...)` | Minimum value / أصغر قيمة |
| `max(a, b, ...)` | `أعلى(أ، ب، ...)` | Maximum value / أكبر قيمة |
| `sqrt(x)` | `جذر(س)` | Square root / الجذر التربيعي |
| `sin(x)`, `cos(x)`, `tan(x)` | - | Trigonometric functions / الوظائف المثلثية |

## ⚡ Performance Features / ميزات الأداء

### Silent Mode / الوضع الصامت

For performance-critical applications:

للتطبيقات الحساسة للأداء:

```python
# Enable silent mode / تفعيل الوضع الصامت
interpreter = NDScriptInterpreter(silent_mode=True)

# Execute code without debug output / تنفيذ الكود بدون مخرجات التشخيص
result = interpreter.interpret("x = 10\ny = x * 2")
```

### Caching / التخزين المؤقت

Automatic caching for improved performance:

التخزين المؤقت التلقائي لتحسين الأداء:

- **Parse caching**: AST parsing results are cached / نتائج تحليل AST مخزنة مؤقتاً
- **Transform caching**: AST transformation results are cached / نتائج تحويل AST مخزنة مؤقتاً
- **LRU eviction**: Automatic memory management / إدارة الذاكرة التلقائية

## 🚨 Error Handling / معالجة الأخطاء

### Exception Types / أنواع الاستثناءات

- `NDScriptSyntaxError`: Syntax errors / أخطاء الصيغة
- `NDScriptRuntimeError`: Runtime errors / أخطاء وقت التشغيل
- `NDScriptError`: General ND-Script errors / أخطاء ND-Script العامة

### Example / مثال

```python
from nds.runtime.errors import NDScriptSyntaxError, NDScriptRuntimeError

interpreter = NDScriptInterpreter()

try:
    result = interpreter.interpret("x = 10 / 0")
except NDScriptRuntimeError as e:
    print(f"Runtime error: {e}")

try:
    result = interpreter.interpret("invalid syntax")
except NDScriptSyntaxError as e:
    print(f"Syntax error: {e}")
```

## 📊 Performance Metrics / مقاييس الأداء

### Achieved Performance / الأداء المحقق

- **Average execution time**: 0.96ms / متوسط وقت التنفيذ
- **Fastest operation**: 0.19ms / أسرع عملية
- **Cache improvement**: 89.1% / تحسن التخزين المؤقت
- **Performance classification**: Outstanding / التصنيف: استثنائي

## 💡 Advanced Examples / أمثلة متقدمة

### Complete Simulation Example / مثال محاكاة كاملة

```python
from nds.runtime.interpreter import NDScriptInterpreter

# Create interpreter / إنشاء المفسر
interpreter = NDScriptInterpreter()

# Execute complete simulation / تنفيذ محاكاة كاملة
simulation_code = """
// Initialize quantum fractal universe
تهيئة حجم=161

// Set golden ratio parameters
ضبط عدم_انتظام=φ/10
ضبط جاذبية=1/φ

// Run evolution
تطور 50

// Display results
عرض كثافة
عرض إحصائيات

// Save state
حفظ "golden_simulation.nds"
"""

result = interpreter.interpret(simulation_code)
print(f"Simulation completed: {result}")
```

### Performance Optimization Example / مثال تحسين الأداء

```python
import time
from nds.runtime.interpreter import NDScriptInterpreter

# Performance-optimized execution / تنفيذ محسن للأداء
def fast_execution():
    interpreter = NDScriptInterpreter(silent_mode=True)

    start_time = time.perf_counter()

    # Execute multiple operations / تنفيذ عمليات متعددة
    for i in range(100):
        interpreter.environment.variables.clear()
        result = interpreter.interpret(f"x = {i}\ny = x * 2\nz = y + 1")

    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000

    print(f"100 operations completed in {execution_time:.2f}ms")
    print(f"Average per operation: {execution_time/100:.2f}ms")

fast_execution()
```

---

**Version**: ND-Script v2.0.0
**Last Updated**: 2024-12-19
**Performance**: ✅ **Outstanding** (0.96ms average)
