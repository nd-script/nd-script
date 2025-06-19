# 🤝 **دليل المساهمة في ND-Script**
## **Contributing Guide to ND-Script**

مرحباً بك في مجتمع ND-Script! نحن نرحب بمساهماتك في تطوير أول لغة برمجة ثنائية اللغة جاهزة للإنتاج في العالم.

Welcome to the ND-Script community! We welcome your contributions to developing the world's first production-ready bilingual programming language.

---

## 📋 **جدول المحتويات | Table of Contents**

- [🌟 كيفية المساهمة | How to Contribute](#-كيفية-المساهمة--how-to-contribute)
- [🔧 إعداد بيئة التطوير | Development Setup](#-إعداد-بيئة-التطوير--development-setup)
- [📝 إرشادات الكود | Code Guidelines](#-إرشادات-الكود--code-guidelines)
- [🧪 الاختبارات | Testing](#-الاختبارات--testing)
- [📚 الوثائق | Documentation](#-الوثائق--documentation)
- [🐛 تقرير المشاكل | Bug Reports](#-تقرير-المشاكل--bug-reports)
- [✨ طلب الميزات | Feature Requests](#-طلب-الميزات--feature-requests)
- [🔄 عملية المراجعة | Review Process](#-عملية-المراجعة--review-process)

---

## 🌟 **كيفية المساهمة | How to Contribute**

### **أنواع المساهمات المرحب بها | Welcome Contributions**

نرحب بجميع أنواع المساهمات:

- 🐛 **إصلاح الأخطاء | Bug Fixes**
- ✨ **ميزات جديدة | New Features**
- 📚 **تحسين الوثائق | Documentation Improvements**
- 🌍 **ترجمات | Translations**
- 🧪 **إضافة اختبارات | Adding Tests**
- ⚡ **تحسين الأداء | Performance Improvements**
- 🎨 **تحسين واجهة المستخدم | UI/UX Improvements**

### **خطوات المساهمة | Contribution Steps**

1. **Fork المستودع | Fork the Repository**
   ```bash
   # انقر على زر Fork في GitHub
   # Click the Fork button on GitHub
   ```

2. **استنساخ المستودع | Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nd-script.git
   cd nd-script
   ```

3. **إنشاء فرع جديد | Create a New Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # أو للإصلاحات | or for bug fixes:
   git checkout -b fix/bug-description
   ```

4. **إجراء التغييرات | Make Your Changes**
   - اتبع إرشادات الكود أدناه
   - أضف اختبارات للميزات الجديدة
   - حدث الوثائق حسب الحاجة

5. **اختبار التغييرات | Test Your Changes**
   ```bash
   # تشغيل جميع الاختبارات | Run all tests
   pytest tests/
   
   # تشغيل اختبارات محددة | Run specific tests
   pytest tests/unit/test_your_feature.py
   ```

6. **إرسال التغييرات | Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add bilingual function support"
   # استخدم التنسيق المحدد أدناه | Use the format specified below
   ```

7. **دفع التغييرات | Push Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **إنشاء Pull Request | Create Pull Request**
   - اذهب إلى GitHub وأنشئ Pull Request
   - اتبع قالب Pull Request المحدد

---

## 🔧 **إعداد بيئة التطوير | Development Setup**

### **المتطلبات | Requirements**

- **Python**: 3.8 أو أحدث | 3.8 or newer
- **Node.js**: 16.x أو أحدث | 16.x or newer (للإضافة | for VS Code extension)
- **Git**: أحدث إصدار | Latest version

### **إعداد البيئة | Environment Setup**

```bash
# 1. استنساخ المستودع | Clone the repository
git clone https://github.com/nd-script/nd-script.git
cd nd-script

# 2. إنشاء بيئة افتراضية | Create virtual environment
python -m venv venv

# 3. تفعيل البيئة الافتراضية | Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. تثبيت التبعيات | Install dependencies
pip install -r requirements.txt
pip install -e .

# 5. إعداد إضافة VS Code | Setup VS Code extension
cd vscode-extension
npm install
npm run compile
cd ..

# 6. تشغيل الاختبارات | Run tests
pytest tests/
```

### **أدوات التطوير المفيدة | Useful Development Tools**

```bash
# تنسيق الكود | Code formatting
black ndscript/
isort ndscript/

# فحص الكود | Code linting
flake8 ndscript/
mypy ndscript/

# تغطية الاختبارات | Test coverage
pytest --cov=ndscript tests/
```

---

## 📝 **إرشادات الكود | Code Guidelines**

### **أسلوب الكود | Code Style**

- **Python**: اتبع PEP 8 مع Black formatting
- **TypeScript**: اتبع معايير TypeScript الرسمية
- **التعليقات**: ثنائية اللغة (عربي/إنجليزي) للميزات الرئيسية

### **تنسيق Commit Messages**

استخدم التنسيق التالي:

```
type(scope): description in English

النوع(النطاق): الوصف بالعربية

Body of the commit message explaining the changes in detail.
نص رسالة الالتزام يشرح التغييرات بالتفصيل.
```

**أنواع Commit:**
- `feat`: ميزة جديدة | new feature
- `fix`: إصلاح خطأ | bug fix
- `docs`: تحديث وثائق | documentation update
- `style`: تنسيق كود | code formatting
- `refactor`: إعادة هيكلة | code refactoring
- `test`: إضافة اختبارات | adding tests
- `chore`: مهام صيانة | maintenance tasks

**مثال:**
```
feat(parser): add support for Arabic comma in function parameters

feat(parser): إضافة دعم الفاصلة العربية في معاملات الدوال

This commit adds support for Arabic comma (،) in function parameter 
lists, allowing developers to write more natural Arabic code.

هذا الالتزام يضيف دعم الفاصلة العربية (،) في قوائم معاملات 
الدوال، مما يسمح للمطورين بكتابة كود عربي أكثر طبيعية.
```

### **تسمية الملفات والمتغيرات | File and Variable Naming**

- **ملفات Python**: `snake_case.py`
- **ملفات TypeScript**: `camelCase.ts`
- **المتغيرات**: `snake_case` في Python، `camelCase` في TypeScript
- **الثوابت**: `UPPER_CASE`
- **الكلاسات**: `PascalCase`

---

## 🧪 **الاختبارات | Testing**

### **كتابة الاختبارات | Writing Tests**

- **اختبارات الوحدة**: لكل دالة ووحدة
- **اختبارات التكامل**: للميزات المعقدة
- **اختبارات الأداء**: للميزات الحرجة
- **اختبارات ثنائية اللغة**: للتأكد من دعم العربية والإنجليزية

### **مثال على اختبار ثنائي اللغة:**

```python
def test_bilingual_function_definition():
    """Test function definition in both Arabic and English"""
    
    # Arabic function test
    arabic_code = '''
    دالة مربع(س: رقم): رقم {
        إرجاع س * س
    }
    '''
    result = execute_ndscript(arabic_code)
    assert result.success
    
    # English function test
    english_code = '''
    function square(x: number): number {
        return x * x
    }
    '''
    result = execute_ndscript(english_code)
    assert result.success
```

### **تشغيل الاختبارات | Running Tests**

```bash
# جميع الاختبارات | All tests
pytest tests/

# اختبارات محددة | Specific tests
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# مع تغطية | With coverage
pytest --cov=ndscript tests/

# اختبارات سريعة فقط | Quick tests only
pytest -m "not slow" tests/
```

---

## 📚 **الوثائق | Documentation**

### **أنواع الوثائق | Documentation Types**

- **API Documentation**: وثائق تلقائية من docstrings
- **User Guides**: أدلة المستخدم ثنائية اللغة
- **Tutorials**: دروس تعليمية بالعربية والإنجليزية
- **Examples**: أمثلة عملية

### **كتابة الوثائق | Writing Documentation**

```python
def bilingual_function(arabic_param: str, english_param: str) -> str:
    """
    A bilingual function example.
    مثال على دالة ثنائية اللغة.
    
    Args:
        arabic_param (str): Arabic parameter description
                           وصف المعامل العربي
        english_param (str): English parameter description
                            وصف المعامل الإنجليزي
    
    Returns:
        str: Combined result | النتيجة المدمجة
        
    Example:
        >>> result = bilingual_function("مرحبا", "Hello")
        >>> print(result)
        مرحبا Hello
    """
    return f"{arabic_param} {english_param}"
```

---

## 🐛 **تقرير المشاكل | Bug Reports**

عند تقرير مشكلة، يرجى تضمين:

1. **وصف المشكلة** بالعربية والإنجليزية
2. **خطوات إعادة الإنتاج**
3. **السلوك المتوقع**
4. **السلوك الفعلي**
5. **معلومات البيئة** (نظام التشغيل، إصدار Python، إلخ)
6. **مثال كود** يوضح المشكلة

### **قالب تقرير المشكلة:**

```markdown
## وصف المشكلة | Bug Description
[وصف واضح للمشكلة بالعربية]
[Clear description of the bug in English]

## خطوات إعادة الإنتاج | Steps to Reproduce
1. [الخطوة الأولى]
2. [الخطوة الثانية]
3. [الخطوة الثالثة]

## السلوك المتوقع | Expected Behavior
[ما كان يجب أن يحدث]

## السلوك الفعلي | Actual Behavior
[ما حدث فعلاً]

## مثال الكود | Code Example
```ndscript
// كود يوضح المشكلة
```

## معلومات البيئة | Environment
- OS: [نظام التشغيل]
- Python Version: [إصدار Python]
- ND-Script Version: [إصدار ND-Script]
```

---

## ✨ **طلب الميزات | Feature Requests**

لطلب ميزة جديدة:

1. **تحقق** من عدم وجود طلب مشابه
2. **اشرح الحاجة** للميزة
3. **قدم أمثلة** على الاستخدام
4. **اقترح التنفيذ** إذا أمكن

---

## 🔄 **عملية المراجعة | Review Process**

1. **المراجعة التلقائية**: CI/CD checks
2. **مراجعة الكود**: من قبل المشرفين
3. **اختبار الميزات**: التأكد من عمل الميزات الجديدة
4. **مراجعة الوثائق**: التأكد من اكتمال الوثائق
5. **الموافقة النهائية**: من قبل المشرفين الرئيسيين

---

## 🎉 **شكراً لك | Thank You**

شكراً لمساهمتك في ND-Script! مساهماتك تساعد في جعل البرمجة ثنائية اللغة حقيقة للمطورين حول العالم.

Thank you for contributing to ND-Script! Your contributions help make bilingual programming a reality for developers worldwide.

---

## 📞 **التواصل | Contact**

- **Discord**: [ND-Script Community](https://discord.gg/ndscript)
- **GitHub Issues**: [تقرير المشاكل](https://github.com/nd-script/nd-script/issues)
- **Email**: contribute@ndscript.org

**مساهمة سعيدة! | Happy Contributing!** 🚀
