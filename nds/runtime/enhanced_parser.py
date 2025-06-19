#!/usr/bin/env python3
"""
محلل نحوي محسن لـ ND-Script مع دعم وضع التساهل
Enhanced Parser for ND-Script with Lenient Mode Support
"""

import re
from typing import Optional, List, Dict, Tuple
from lark import Lark, UnexpectedToken, UnexpectedCharacters
from .interpreter import NDScriptInterpreter

class EnhancedParser:
    """محلل نحوي محسن مع ميزات متقدمة"""
    
    def __init__(self, lenient_mode: bool = False, auto_fix: bool = True):
        self.lenient_mode = lenient_mode
        self.auto_fix = auto_fix
        self.warnings: List[str] = []
        self.fixes_applied: List[str] = []
        self.interpreter = NDScriptInterpreter()
    
    def normalize_commas(self, code: str) -> str:
        """تطبيع الفواصل - تحويل جميع أنواع الفواصل إلى فاصلة عادية"""
        if not self.auto_fix:
            return code
        
        # قائمة بجميع أنواع الفواصل المحتملة
        comma_variants = [
            '،',      # فاصلة عربية (U+060C)
            '‚',      # فاصلة سفلية (U+201A)
            '„',      # فاصلة مزدوجة سفلية (U+201E)
            '，',     # فاصلة صينية (U+FF0C)
            '︐',     # فاصلة عمودية (U+FE10)
        ]
        
        original_code = code
        fixes_count = 0
        
        for variant in comma_variants:
            if variant in code:
                # فحص السياق - هل الفاصلة في قائمة معاملات؟
                pattern = rf'([a-zA-Z_\u0600-\u06FF][a-zA-Z0-9_\u0600-\u06FF]*)\s*{re.escape(variant)}\s*([a-zA-Z_\u0600-\u06FF][a-zA-Z0-9_\u0600-\u06FF]*)'
                matches = re.findall(pattern, code)
                
                if matches:
                    code = code.replace(variant, ',')
                    fixes_count += len(matches)
        
        if fixes_count > 0:
            self.fixes_applied.append(f"تم تطبيع {fixes_count} فاصلة إلى الشكل المعياري")
        
        return code
    
    def detect_syntax_issues(self, code: str) -> List[Dict[str, any]]:
        """اكتشاف مشاكل النحو المحتملة"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # فحص الفواصل المختلطة
            if '،' in line and ',' in line:
                issues.append({
                    "type": "mixed_commas",
                    "line": line_num,
                    "message": "استخدام فواصل مختلطة في نفس السطر",
                    "suggestion": "استخدم نوع واحد من الفواصل (، أو ,)",
                    "severity": "warning"
                })
            
            # فحص الأقواس غير المتطابقة
            open_parens = line.count('(')
            close_parens = line.count(')')
            if open_parens != close_parens:
                issues.append({
                    "type": "unmatched_parentheses",
                    "line": line_num,
                    "message": "أقواس غير متطابقة",
                    "suggestion": "تأكد من إغلاق جميع الأقواس",
                    "severity": "error"
                })
            
            # فحص الأقواس المجعدة غير المتطابقة
            open_braces = line.count('{')
            close_braces = line.count('}')
            if open_braces != close_braces:
                issues.append({
                    "type": "unmatched_braces",
                    "line": line_num,
                    "message": "أقواس مجعدة غير متطابقة",
                    "suggestion": "تأكد من إغلاق جميع الأقواس المجعدة",
                    "severity": "error"
                })
            
            # فحص الكلمات المفتاحية المحتملة الخاطئة
            potential_keywords = {
                'دالة': ['دالة', 'function'],
                'ماكرو': ['ماكرو', 'macro'],
                'استيراد': ['استيراد', 'import'],
                'تهيئة': ['تهيئة', 'init'],
                'تطور': ['تطور', 'evolve']
            }
            
            for correct_keyword, variants in potential_keywords.items():
                for variant in variants:
                    # فحص الكلمات المشابهة
                    pattern = rf'\b{re.escape(variant[:-1])}\w*\b'
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if match not in variants and self._is_similar(match, variant):
                            issues.append({
                                "type": "similar_keyword",
                                "line": line_num,
                                "message": f"كلمة مشابهة للكلمة المفتاحية: {match}",
                                "suggestion": f"هل تقصد '{variant}'؟",
                                "severity": "warning"
                            })
        
        return issues
    
    def _is_similar(self, word1: str, word2: str, threshold: float = 0.8) -> bool:
        """فحص التشابه بين كلمتين"""
        if len(word1) == 0 or len(word2) == 0:
            return False
        
        # حساب مسافة Levenshtein المبسطة
        max_len = max(len(word1), len(word2))
        min_len = min(len(word1), len(word2))
        
        if max_len - min_len > 2:  # فرق كبير في الطول
            return False
        
        common_chars = sum(1 for c1, c2 in zip(word1, word2) if c1 == c2)
        similarity = common_chars / max_len
        
        return similarity >= threshold
    
    def generate_error_suggestions(self, error: Exception, code: str) -> List[str]:
        """توليد اقتراحات لإصلاح الأخطاء"""
        suggestions = []
        error_str = str(error)
        
        if "Unexpected token" in error_str or "UnexpectedToken" in str(type(error)):
            suggestions.extend([
                "تحقق من صحة الكلمات المفتاحية المستخدمة",
                "تأكد من استخدام الفواصل الصحيحة (، أو ,)",
                "فحص الأقواس والأقواس المجعدة"
            ])
        
        if "COMMA" in error_str:
            suggestions.extend([
                "استخدم الفاصلة العربية (،) أو الإنجليزية (,)",
                "تأكد من وجود فراغات حول الفواصل",
                "فحص قائمة المعاملات في تعريف الدالة"
            ])
        
        if "IDENTIFIER" in error_str:
            suggestions.extend([
                "تأكد من صحة أسماء المتغيرات والدوال",
                "الأسماء يجب أن تبدأ بحرف أو _",
                "تجنب استخدام الكلمات المحجوزة"
            ])
        
        # اقتراحات خاصة بالأخطاء الشائعة
        if "function" in code.lower() or "دالة" in code:
            suggestions.append("تحقق من صيغة تعريف الدالة: دالة اسم_الدالة(معامل1، معامل2): { ... }")
        
        if "import" in code.lower() or "استيراد" in code:
            suggestions.append("تحقق من صيغة الاستيراد: استيراد \"اسم_الملف.ndx\"")
        
        return suggestions
    
    def parse_with_recovery(self, code: str) -> Tuple[Optional[any], List[Dict[str, any]]]:
        """تحليل الكود مع استرداد الأخطاء"""
        issues = []
        
        # تطبيع الكود أولاً
        normalized_code = self.normalize_commas(code)
        
        # اكتشاف المشاكل المحتملة
        syntax_issues = self.detect_syntax_issues(normalized_code)
        issues.extend(syntax_issues)
        
        try:
            # محاولة التحليل العادي
            result = self.interpreter.interpret(normalized_code)
            return result, issues
            
        except (UnexpectedToken, UnexpectedCharacters) as e:
            if self.lenient_mode:
                # في وضع التساهل، حاول إصلاح الأخطاء
                suggestions = self.generate_error_suggestions(e, normalized_code)
                
                issues.append({
                    "type": "parse_error",
                    "message": f"خطأ في التحليل النحوي: {str(e)}",
                    "suggestions": suggestions,
                    "severity": "error",
                    "recoverable": True
                })
                
                # محاولة إصلاح بسيط
                fixed_code = self._attempt_simple_fixes(normalized_code, e)
                if fixed_code != normalized_code:
                    try:
                        result = self.interpreter.interpret(fixed_code)
                        issues.append({
                            "type": "auto_fix",
                            "message": "تم إصلاح الكود تلقائياً",
                            "severity": "info"
                        })
                        return result, issues
                    except:
                        pass
                
                return None, issues
            else:
                # في الوضع العادي، ارفع الخطأ
                raise e
        
        except Exception as e:
            issues.append({
                "type": "runtime_error",
                "message": f"خطأ في التنفيذ: {str(e)}",
                "suggestions": self.generate_error_suggestions(e, normalized_code),
                "severity": "error",
                "recoverable": False
            })
            
            if self.lenient_mode:
                return None, issues
            else:
                raise e
    
    def _attempt_simple_fixes(self, code: str, error: Exception) -> str:
        """محاولة إصلاحات بسيطة للكود"""
        fixed_code = code
        
        # إصلاح الفواصل المفقودة
        if "COMMA" in str(error):
            # إضافة فواصل مفقودة في قوائم المعاملات
            pattern = r'(\w+)\s+(\w+)\s*\)'
            fixed_code = re.sub(pattern, r'\1, \2)', fixed_code)
        
        # إصلاح الأقواس المفقودة
        if "(" in str(error) or ")" in str(error):
            # محاولة إضافة أقواس مفقودة
            lines = fixed_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith(('دالة', 'function', 'ماكرو', 'macro')):
                    if '(' not in line:
                        # إضافة أقواس فارغة
                        lines[i] = line.replace(':', '(): {')
            fixed_code = '\n'.join(lines)
        
        return fixed_code
    
    def get_parsing_report(self) -> Dict[str, any]:
        """الحصول على تقرير التحليل"""
        return {
            "lenient_mode": self.lenient_mode,
            "auto_fix": self.auto_fix,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
            "total_warnings": len(self.warnings),
            "total_fixes": len(self.fixes_applied)
        }

# دالة مساعدة للاستخدام السريع
def parse_ndscript(code: str, lenient: bool = False, auto_fix: bool = True) -> Tuple[Optional[any], Dict[str, any]]:
    """تحليل كود ND-Script مع خيارات متقدمة"""
    parser = EnhancedParser(lenient_mode=lenient, auto_fix=auto_fix)
    result, issues = parser.parse_with_recovery(code)
    
    report = parser.get_parsing_report()
    report["issues"] = issues
    
    return result, report
