# 🌍 ND-Script Language Support for VS Code
## **دعم لغة ND-Script في VS Code**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://marketplace.visualstudio.com/items?itemName=nd-script-team.nd-script)
[![VS Code](https://img.shields.io/badge/VS%20Code-1.74.0+-green.svg)](https://code.visualstudio.com/)
[![Languages](https://img.shields.io/badge/languages-Arabic%20%7C%20English-orange.svg)](https://github.com/nd-script/nd-script)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Downloads](https://img.shields.io/badge/downloads-1K+-brightgreen.svg)](https://marketplace.visualstudio.com/items?itemName=nd-script-team.nd-script)

**Complete VS Code language support for ND-Script v2.0.0 - The World's First Production-Ready Bilingual Programming Language**

**دعم كامل للغة ND-Script v2.0.0 في VS Code - أول لغة برمجة ثنائية اللغة جاهزة للإنتاج في العالم**

---

## 📋 Table of Contents | جدول المحتويات

- [🌟 Overview | نظرة عامة](#-overview--نظرة-عامة)
- [⚡ Quick Start | البداية السريعة](#-quick-start--البداية-السريعة)
- [🚀 Installation | التثبيت](#-installation--التثبيت)
- [✨ Features | الميزات](#-features--الميزات)
- [📖 Usage Examples | أمثلة الاستخدام](#-usage-examples--أمثلة-الاستخدام)
- [⌨️ Commands & Shortcuts | الأوامر والاختصارات](#️-commands--shortcuts--الأوامر-والاختصارات)
- [⚙️ Configuration | الإعدادات](#️-configuration--الإعدادات)
- [🔧 Troubleshooting | استكشاف الأخطاء](#-troubleshooting--استكشاف-الأخطاء)
- [🛠️ Development | التطوير](#️-development--التطوير)
- [📚 Version History | تاريخ الإصدارات](#-version-history--تاريخ-الإصدارات)
- [📄 License | الترخيص](#-license--الترخيص)

---

## 🌟 Overview | نظرة عامة

### **English**
ND-Script is the world's first production-ready bilingual programming language that seamlessly supports both Arabic and English syntax within the same program. This VS Code extension provides complete language support for ND-Script v2.0.0, including advanced syntax highlighting, intelligent IntelliSense, comprehensive hover documentation, and full type system integration.

**Key Capabilities:**
- 🌍 **Bilingual Programming**: Write code in Arabic, English, or both
- 🎨 **Advanced Syntax Highlighting**: 40+ keywords with perfect Arabic/English support
- 🧠 **Intelligent IntelliSense**: 70+ completion items with smart suggestions
- 📚 **Comprehensive Documentation**: 60+ hover help entries with bilingual examples
- 🔧 **Type System Integration**: Full support for bilingual type annotations
- ⚡ **Parallel Processing**: Native support for موازي/parallel keywords
- 🔗 **Import System**: Advanced import/export with namespace support

### **العربية**
ND-Script هي أول لغة برمجة ثنائية اللغة جاهزة للإنتاج في العالم تدعم بسلاسة النحو العربي والإنجليزي في نفس البرنامج. توفر هذه الإضافة لـ VS Code دعماً كاملاً للغة ND-Script v2.0.0، بما في ذلك تمييز النحو المتقدم، والإكمال الذكي، والوثائق الشاملة، والتكامل الكامل مع نظام الأنواع.

**القدرات الرئيسية:**
- 🌍 **البرمجة ثنائية اللغة**: اكتب الكود بالعربية أو الإنجليزية أو كليهما
- 🎨 **تمييز النحو المتقدم**: 40+ كلمة مفتاحية مع دعم مثالي للعربية/الإنجليزية
- 🧠 **الإكمال الذكي**: 70+ عنصر إكمال مع اقتراحات ذكية
- 📚 **الوثائق الشاملة**: 60+ مدخل مساعدة مع أمثلة ثنائية اللغة
- 🔧 **تكامل نظام الأنواع**: دعم كامل لتعليقات الأنواع ثنائية اللغة
- ⚡ **المعالجة المتوازية**: دعم أصلي لكلمات موازي/parallel
- 🔗 **نظام الاستيراد**: استيراد/تصدير متقدم مع دعم مساحات الأسماء

---

## ⚡ Quick Start | البداية السريعة

### **1. Install the Extension | تثبيت الإضافة**
```bash
# Method 1: VS Code Marketplace
# Open VS Code → Extensions → Search "ND-Script"

# Method 2: Command Line
code --install-extension nd-script-team.nd-script
```

### **2. Create Your First ND-Script File | إنشاء أول ملف ND-Script**
```ndscript
// Create a new file with .ndx extension
// أنشئ ملف جديد بامتداد .ndx

// Bilingual Hello World | مرحبا بالعالم ثنائي اللغة
دالة مرحبا(الاسم: نص): نص {
    إرجاع "مرحباً " + الاسم
}

function hello(name: string): string {
    return "Hello " + name
}

// Mixed usage | الاستخدام المختلط
arabic_greeting: نص = مرحبا("أحمد")
english_greeting: string = hello("Sarah")

print(arabic_greeting)  // Output: مرحباً أحمد
print(english_greeting) // Output: Hello Sarah
```

### **3. Run Your Code | تشغيل الكود**
- Press **F5** to run the file
- Or use **Ctrl+Shift+P** → "ND-Script: Run"
- اضغط **F5** لتشغيل الملف
- أو استخدم **Ctrl+Shift+P** ← "ND-Script: Run"

---

## 🚀 Installation | التثبيت

### **Method 1: VS Code Marketplace (Recommended)**
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "ND-Script Language Support"
4. Click "Install"

### **Method 2: Manual Installation**
1. Download the latest `.vsix` file from [Releases](https://github.com/nd-script/nd-script/releases)
2. Open VS Code
3. Press `Ctrl+Shift+P` and type "Extensions: Install from VSIX"
4. Select the downloaded `.vsix` file

### **Method 3: Development Installation**
```bash
# Clone the repository
git clone https://github.com/nd-script/nd-script.git
cd nd-script/vscode-extension

# Install dependencies
npm install

# Compile the extension
npm run compile

# Package the extension (optional)
npx vsce package
```

### **System Requirements | متطلبات النظام**
- **VS Code**: 1.74.0 or higher
- **Node.js**: 16.x or higher (for development)
- **Python**: 3.8+ (for ND-Script execution)
- **Operating System**: Windows, macOS, Linux

---

## ✨ Features | الميزات

### 🎨 **Advanced Syntax Highlighting | تمييز النحو المتقدم**

**40+ Bilingual Keywords Supported:**

| Category | Arabic | English | Description |
|----------|--------|---------|-------------|
| **Commands** | تهيئة، تطور، عرض، ضبط | init, evolve, show, set | Universe simulation |
| **Functions** | دالة، ماكرو، إرجاع | function, macro, return | Function definitions |
| **Imports** | استيراد، من، كـ | import, from, as | Module system |
| **Control Flow** | إذا، وإلا، وإلا_إذا، طالما، كرر | if, else, elif, while, for | Program flow |
| **Types** | رقم، نص، منطق، قائمة، كائن، فراغ | number, string, boolean, list, object, void | Type system |
| **Parallel** | موازي | parallel | Concurrent processing |
| **Constants** | π، τ، φ، ∞، e | pi, tau, phi, infinity, e | Mathematical constants |

### 🧠 **Intelligent IntelliSense | الإكمال الذكي**

**70+ Completion Items in 4 Categories:**

#### **1. Commands (42 items)**
```ndscript
// Arabic commands with type annotations
دالة حساب_المساحة(الطول: رقم، العرض: رقم): رقم {
    إرجاع الطول * العرض
}

// English commands with full IntelliSense
function calculate_volume(length: number, width: number, height: number): number {
    return length * width * height
}
```

#### **2. Type System (12 items)**
- **Arabic Types**: رقم، نص، منطق، قائمة، كائن، فراغ
- **English Types**: number, string, boolean, list, object, void
- **Generic Types**: قائمة[رقم], list[string]

#### **3. Mathematical Constants (9 items)**
- **Symbols**: π, τ, φ, ∞, e
- **Names**: pi, tau, phi, infinity, euler

#### **4. Parameters (10 items)**
- **Physics**: جاذبية/gravity, عدم_انتظام/irregularity
- **Advanced**: طاقة_كمية/quantum_energy, كتلة/mass

### 📚 **Comprehensive Hover Documentation | الوثائق الشاملة**

**60+ Bilingual Help Entries:**

```ndscript
// Hover over any keyword for detailed help
دالة مربع(س: رقم): رقم {  // Shows function syntax and examples
    إرجاع س * س           // Shows return statement documentation
}

// English documentation with Arabic translations
function square(x: number): number {  // Complete type system help
    return x * x                      // Usage examples included
}
```

### 🔧 **Type System Integration | تكامل نظام الأنواع**

**Full Bilingual Type Support:**

```ndscript
// Arabic type annotations
عدد: رقم = 42
اسم: نص = "أحمد"
نشط: منطق = صحيح
أرقام: قائمة[رقم] = [1, 2, 3]

// English type annotations
count: number = 100
message: string = "Hello"
enabled: boolean = true
items: list[string] = ["a", "b", "c"]

// Mixed language with full IntelliSense
دالة process_data(data: قائمة[رقم], name: string): نص {
    // Full type checking and completion
    إرجاع name + ": " + data.length
}
```

### 🔗 **Advanced Import System | نظام الاستيراد المتقدم**

**3 Import Types Supported:**

```ndscript
// Simple import | الاستيراد البسيط
استيراد "math_library.ndx"
import "physics_library.ndx"

// Import with alias | الاستيراد مع الاسم المستعار
استيراد "complex_math.ndx" كـ رياضيات
import "advanced_physics.ndx" as physics

// Selective import | الاستيراد الانتقائي
من "utilities.ndx" استيراد helper_function، calculate
from "tools.ndx" import process_data, validate
```

### ⚡ **Parallel Processing Support | دعم المعالجة المتوازية**

```ndscript
// Arabic parallel processing
موازي كرر i في (1, 1000): {
    نتيجة[i] = حساب_معقد(i)
}

// English parallel processing
parallel for j in (1, 500): {
    result[j] = complex_calculation(j)
}
```

---

## 📖 Usage Examples | أمثلة الاستخدام

### **Example 1: Basic Bilingual Program | مثال 1: برنامج ثنائي اللغة أساسي**

```ndscript
// File: hello_world.ndx
// ملف: hello_world.ndx

// Arabic function with type annotations
دالة تحية_شخصية(الاسم: نص، العمر: رقم): نص {
    إذا (العمر < 18): {
        إرجاع "مرحباً " + الاسم + "، أنت صغير السن"
    } وإلا: {
        إرجاع "مرحباً " + الاسم + "، أهلاً وسهلاً"
    }
}

// English function with bilingual integration
function personal_greeting(name: string, age: number): string {
    if (age < 18): {
        return "Hello " + name + ", you are young"
    } else: {
        return "Hello " + name + ", welcome"
    }
}

// Mixed usage | الاستخدام المختلط
arabic_result: نص = تحية_شخصية("فاطمة", 25)
english_result: string = personal_greeting("John", 30)

print(arabic_result)   // مرحباً فاطمة، أهلاً وسهلاً
print(english_result)  // Hello John, welcome
```

### **Example 2: Advanced Features | مثال 2: الميزات المتقدمة**

```ndscript
// File: advanced_features.ndx
// ملف: advanced_features.ndx

// Import libraries | استيراد المكتبات
استيراد "math_utils.ndx" كـ رياضيات
from "data_processing.ndx" import process_array, validate_input

// Complex function with generics | دالة معقدة مع الأنواع العامة
دالة معالجة_البيانات(البيانات: قائمة[رقم], المعامل: رقم): قائمة[رقم] {
    نتيجة: قائمة[رقم] = []

    // Parallel processing for performance | معالجة متوازية للأداء
    موازي كرر i في (0, البيانات.length): {
        processed_value: رقم = البيانات[i] * المعامل * π
        نتيجة.push(processed_value)
    }

    إرجاع نتيجة
}

// English equivalent with type safety
function process_data(data: list[number], factor: number): list[number] {
    result: list[number] = []

    parallel for i in (0, data.length): {
        processed_value: number = data[i] * factor * pi
        result.push(processed_value)
    }

    return result
}

// Usage with full IntelliSense support
input_data: قائمة[رقم] = [1.5, 2.7, 3.14, 4.0]
processed: قائمة[رقم] = معالجة_البيانات(input_data, 2.0)
```

### **Example 3: Universe Simulation | مثال 3: محاكاة الكون**

```ndscript
// File: universe_simulation.ndx
// ملف: universe_simulation.ndx

// Initialize universe with Arabic commands
تهيئة حجم=200
ضبط جاذبية=0.8
ضبط طاقة_كمية=2.5
ضبط كتلة=1.2

// Evolution with English commands
evolve 50
show density
show energy

// Mixed language simulation function
دالة run_simulation(steps: رقم, gravity_value: رقم): منطق {
    set gravity=gravity_value
    تطور steps

    إذا (steps > 100): {
        عرض إحصائيات
        return صحيح
    } وإلا: {
        show state
        return خطأ
    }
}

// Execute simulation | تنفيذ المحاكاة
simulation_result: منطق = run_simulation(150, 0.7)
```

---

## ⌨️ Commands & Shortcuts | الأوامر والاختصارات

### **Keyboard Shortcuts | اختصارات لوحة المفاتيح**

| Shortcut | Command | Description | الوصف |
|----------|---------|-------------|--------|
| **F5** | Run ND-Script | Execute current file | تشغيل الملف الحالي |
| **Ctrl+Shift+C** | Check Syntax | Validate syntax | التحقق من النحو |
| **Ctrl+Shift+P** | Command Palette | Open command menu | فتح قائمة الأوامر |

### **Command Palette Commands | أوامر لوحة الأوامر**

| Command | Description | الوصف |
|---------|-------------|--------|
| `ND-Script: Run` | Execute the current ND-Script file | تشغيل ملف ND-Script الحالي |
| `ND-Script: Check Syntax` | Validate syntax without execution | التحقق من النحو بدون تشغيل |
| `ND-Script: Start REPL` | Open interactive ND-Script session | فتح جلسة ND-Script تفاعلية |

### **Context Menu Options | خيارات القائمة السياقية**

Right-click on any `.ndx` or `.nds` file to access:
- **Run ND-Script** - Execute the file
- **Check Syntax** - Validate syntax

انقر بالزر الأيمن على أي ملف `.ndx` أو `.nds` للوصول إلى:
- **تشغيل ND-Script** - تنفيذ الملف
- **فحص النحو** - التحقق من النحو

---

## ⚙️ Configuration | الإعدادات

### **Extension Settings | إعدادات الإضافة**

Access settings via: `File > Preferences > Settings > Extensions > ND-Script`

| Setting | Type | Default | Description | الوصف |
|---------|------|---------|-------------|--------|
| `ndscript.pythonPath` | string | `"python"` | Path to Python interpreter | مسار مفسر Python |
| `ndscript.enableLinting` | boolean | `true` | Enable syntax checking | تفعيل فحص النحو |
| `ndscript.maxNumberOfProblems` | number | `100` | Maximum problems to report | أقصى عدد مشاكل للإبلاغ |

### **File Associations | ارتباطات الملفات**

The extension automatically associates with:
- `.ndx` files (ND-Script source files)
- `.nds` files (ND-Script data files)

تربط الإضافة تلقائياً مع:
- ملفات `.ndx` (ملفات مصدر ND-Script)
- ملفات `.nds` (ملفات بيانات ND-Script)

### **Custom Configuration Example | مثال على الإعداد المخصص**

```json
{
    "ndscript.pythonPath": "/usr/local/bin/python3",
    "ndscript.enableLinting": true,
    "ndscript.maxNumberOfProblems": 50,
    "files.associations": {
        "*.ndx": "ndscript",
        "*.nds": "ndscript"
    }
}
```

---

## 🔧 Troubleshooting | استكشاف الأخطاء

### **Common Issues | المشاكل الشائعة**

#### **1. Extension Not Loading | الإضافة لا تعمل**

**Problem**: Extension doesn't activate for ND-Script files
**Solution**:
1. Check file extension is `.ndx` or `.nds`
2. Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")
3. Verify extension is enabled in Extensions panel

**المشكلة**: الإضافة لا تنشط لملفات ND-Script
**الحل**:
1. تأكد من أن امتداد الملف `.ndx` أو `.nds`
2. أعد تحميل نافذة VS Code (`Ctrl+Shift+P` ← "Developer: Reload Window")
3. تحقق من تفعيل الإضافة في لوحة الإضافات

#### **2. Python Path Issues | مشاكل مسار Python**

**Problem**: "Python not found" error when running scripts
**Solution**:
1. Install Python 3.8+ from [python.org](https://python.org)
2. Set correct Python path in settings: `ndscript.pythonPath`
3. Verify Python is in system PATH

**المشكلة**: خطأ "Python not found" عند تشغيل النصوص
**الحل**:
1. ثبت Python 3.8+ من [python.org](https://python.org)
2. اضبط مسار Python الصحيح في الإعدادات: `ndscript.pythonPath`
3. تحقق من وجود Python في مسار النظام

#### **3. Syntax Highlighting Issues | مشاكل تمييز النحو**

**Problem**: Arabic text not highlighting correctly
**Solution**:
1. Ensure file encoding is UTF-8
2. Install Arabic language support in VS Code
3. Check language mode is set to "ND-Script"

**المشكلة**: النص العربي لا يظهر بالتمييز الصحيح
**الحل**:
1. تأكد من أن ترميز الملف UTF-8
2. ثبت دعم اللغة العربية في VS Code
3. تحقق من ضبط وضع اللغة على "ND-Script"

#### **4. IntelliSense Not Working | الإكمال الذكي لا يعمل**

**Problem**: Auto-completion suggestions not appearing
**Solution**:
1. Trigger manually with `Ctrl+Space`
2. Check if file is recognized as ND-Script language
3. Restart VS Code if issue persists

**المشكلة**: اقتراحات الإكمال التلقائي لا تظهر
**الحل**:
1. فعل يدوياً بـ `Ctrl+Space`
2. تحقق من التعرف على الملف كلغة ND-Script
3. أعد تشغيل VS Code إذا استمرت المشكلة

### **Performance Optimization | تحسين الأداء**

For better performance with large files:
- Disable unused extensions
- Increase VS Code memory limit
- Use workspace-specific settings

لأداء أفضل مع الملفات الكبيرة:
- عطل الإضافات غير المستخدمة
- زد حد ذاكرة VS Code
- استخدم إعدادات خاصة بمساحة العمل

---

## 🛠️ Development | التطوير

### **Building from Source | البناء من المصدر**

```bash
# Clone the repository | استنساخ المستودع
git clone https://github.com/nd-script/nd-script.git
cd nd-script/vscode-extension

# Install dependencies | تثبيت التبعيات
npm install

# Compile TypeScript | ترجمة TypeScript
npm run compile

# Watch for changes (development) | مراقبة التغييرات (التطوير)
npm run watch

# Package extension | تعبئة الإضافة
npx vsce package
```

### **Project Structure | هيكل المشروع**

```
vscode-extension/
├── src/
│   └── extension.ts          # Main extension code
├── syntaxes/
│   └── nds.tmLanguage.json   # Syntax highlighting grammar
├── out/                      # Compiled JavaScript
├── package.json              # Extension manifest
├── language-configuration.json # Language configuration
└── README.md                 # This file
```

### **Contributing | المساهمة**

We welcome contributions! Please:

1. **Fork the repository** | انسخ المستودع
2. **Create a feature branch** | أنشئ فرع للميزة
3. **Make your changes** | اعمل تغييراتك
4. **Add tests** | أضف الاختبارات
5. **Submit a pull request** | أرسل طلب دمج

**Contribution Guidelines:**
- Follow TypeScript coding standards
- Add bilingual documentation for new features
- Test with both Arabic and English code samples
- Update README.md for new features

**إرشادات المساهمة:**
- اتبع معايير ترميز TypeScript
- أضف وثائق ثنائية اللغة للميزات الجديدة
- اختبر مع عينات كود عربية وإنجليزية
- حدث README.md للميزات الجديدة

### **Testing | الاختبار**

```bash
# Run extension in development mode
# تشغيل الإضافة في وضع التطوير
code --extensionDevelopmentPath=. --new-window

# Test with sample files
# اختبار مع ملفات عينة
code test_v2_features.ndx
```

---

## 📚 Version History | تاريخ الإصدارات

### **v2.0.0 (Current) - December 2024**

**🎉 Major Enhancement Release | إصدار التحسين الرئيسي**

#### **New Features | الميزات الجديدة**
- ✅ **Complete Type System Support** - Full bilingual type annotations
- ✅ **Advanced Import System** - 3 import types (simple, alias, selective)
- ✅ **Enhanced Control Flow** - elif, parallel processing support
- ✅ **Expanded IntelliSense** - 70+ completion items (vs 30 in v1.0.0)
- ✅ **Comprehensive Documentation** - 60+ hover help entries
- ✅ **Mathematical Constants** - π, τ, φ, ∞, e support
- ✅ **Boolean Constants** - صحيح/true, خطأ/false support
- ✅ **Generic Types** - قائمة[T], list[T] support
- ✅ **Parallel Processing** - موازي/parallel keyword support
- ✅ **Enhanced Physics Parameters** - طاقة_كمية, كتلة support

#### **Improvements | التحسينات**
- 🔧 **Syntax Highlighting** - 40+ keywords (vs 25 in v1.0.0)
- 🔧 **Function Definitions** - Type annotations and return types
- 🔧 **Variable Declarations** - Type annotation support
- 🔧 **Import Patterns** - Advanced regex patterns for all import types
- 🔧 **Performance** - Optimized completion provider
- 🔧 **Documentation** - Bilingual examples for all features

#### **Technical Enhancements | التحسينات التقنية**
- Updated package.json metadata for v2.0.0
- Enhanced TextMate grammar with new patterns
- Expanded TypeScript completion provider
- Comprehensive hover documentation system
- Improved Arabic text handling

### **v1.0.0 - Initial Release**

#### **Core Features | الميزات الأساسية**
- ✅ Basic syntax highlighting for ND-Script
- ✅ Simple IntelliSense with 30 completion items
- ✅ Basic hover documentation (20 entries)
- ✅ File association (.ndx, .nds)
- ✅ Command integration (Run, Check, REPL)
- ✅ Keyboard shortcuts (F5, Ctrl+Shift+C)

### **Future Roadmap | خارطة الطريق المستقبلية**

#### **v3.0.0 (Planned) - 2025**
- 🔮 **Advanced Debugging** - Breakpoints and step-through debugging
- 🔮 **Code Refactoring** - Automated code transformation tools
- 🔮 **Project Templates** - Quick project scaffolding
- 🔮 **Performance Profiling** - Built-in performance analysis
- 🔮 **AI Code Completion** - Machine learning-powered suggestions
- 🔮 **Visual Designer** - Drag-and-drop universe design
- 🔮 **Collaborative Editing** - Real-time multi-user editing
- 🔮 **Mobile Support** - VS Code mobile extension

---

## 📄 License | الترخيص

### **MIT License**

```
Copyright (c) 2024 ND-Script Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### **Credits | الاعتمادات**

- **ND-Script Language**: Created by the ND-Script Team
- **VS Code Extension**: Developed with TypeScript and VS Code Extension API
- **Arabic Language Support**: Unicode and RTL text handling
- **Community**: Thanks to all contributors and users

**Special Thanks | شكر خاص**
- Microsoft VS Code team for the excellent extension framework
- The open-source community for inspiration and support
- Arabic programming language pioneers
- Beta testers and early adopters

---

## 🔗 Links | الروابط

- **🌐 Official Website**: [https://ndscript.org](https://ndscript.org)
- **📦 VS Code Marketplace**: [ND-Script Language Support](https://marketplace.visualstudio.com/items?itemName=nd-script-team.nd-script)
- **🐙 GitHub Repository**: [https://github.com/nd-script/nd-script](https://github.com/nd-script/nd-script)
- **📚 Documentation**: [https://docs.ndscript.org](https://docs.ndscript.org)
- **💬 Community Discord**: [https://discord.gg/ndscript](https://discord.gg/ndscript)
- **🐛 Issue Tracker**: [https://github.com/nd-script/nd-script/issues](https://github.com/nd-script/nd-script/issues)

---

## 🎉 **Thank You | شكراً لك**

Thank you for using ND-Script VS Code Extension! We hope it enhances your bilingual programming experience.

شكراً لك لاستخدام إضافة ND-Script لـ VS Code! نأمل أن تحسن تجربة البرمجة ثنائية اللغة لديك.

**Happy Coding! | برمجة سعيدة!** 🚀

---

*Made with ❤️ by the ND-Script Team | صُنع بـ ❤️ من فريق ND-Script*
