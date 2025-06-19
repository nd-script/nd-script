#!/usr/bin/env python3
"""
نظام إدارة الإصدارات لـ ND-Script
Version Management System for ND-Script
"""

import re
import os
from typing import Optional, Dict, List, Tuple
from pathlib import Path

class VersionManager:
    """مدير الإصدارات لـ ND-Script"""
    
    # إصدار ND-Script الحالي
    CURRENT_VERSION = "2.0.0"
    
    # الإصدارات المدعومة
    SUPPORTED_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "2.0.0"]
    
    # تغييرات الإصدارات
    VERSION_CHANGES = {
        "2.0.0": {
            "features": [
                "دعم الفاصلة العربية (Arabic comma support)",
                "نظام الدوال المخصصة (User-defined functions)",
                "نظام الماكروز (Macro system)",
                "نظام الاستيراد المتقدم (Advanced import system)",
                "البرمجة ثنائية اللغة (Bilingual programming)"
            ],
            "breaking_changes": [
                "تحسين معالجة الفاصلة العربية (Improved Arabic comma handling)",
                "تحديث صيغة تعريف الدوال (Updated function definition syntax)"
            ],
            "deprecated": []
        },
        "1.2.0": {
            "features": [
                "نظام الاستيراد الأساسي (Basic import system)",
                "تحسينات الأداء (Performance improvements)"
            ],
            "breaking_changes": [],
            "deprecated": ["الصيغة القديمة للأوامر (Old command syntax)"]
        },
        "1.1.0": {
            "features": [
                "دعم التعليقات العربية (Arabic comments support)",
                "تحسين رسائل الخطأ (Improved error messages)"
            ],
            "breaking_changes": [],
            "deprecated": []
        },
        "1.0.0": {
            "features": [
                "الأوامر الأساسية (Basic commands)",
                "محاكاة الأكوان الكسرية الكمية (Quantum fractal universe simulation)"
            ],
            "breaking_changes": [],
            "deprecated": []
        }
    }
    
    def __init__(self):
        self.version_cache: Dict[str, str] = {}
    
    @classmethod
    def get_current_version(cls) -> str:
        """الحصول على الإصدار الحالي"""
        return cls.CURRENT_VERSION
    
    @classmethod
    def is_version_supported(cls, version: str) -> bool:
        """التحقق من دعم الإصدار"""
        return version in cls.SUPPORTED_VERSIONS
    
    @classmethod
    def compare_versions(cls, version1: str, version2: str) -> int:
        """مقارنة الإصدارات
        Returns: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        def parse_version(v: str) -> Tuple[int, int, int]:
            parts = v.split('.')
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    def extract_version_from_file(self, filepath: str) -> Optional[str]:
        """استخراج الإصدار من ملف .ndx"""
        if filepath in self.version_cache:
            return self.version_cache[filepath]
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # البحث عن تعليق الإصدار
            # @version 2.0.0
            version_pattern = r'@version\s+(\d+\.\d+\.\d+)'
            match = re.search(version_pattern, content)
            
            if match:
                version = match.group(1)
                self.version_cache[filepath] = version
                return version
            
            # إذا لم يوجد إصدار، افترض الإصدار الحالي
            return self.CURRENT_VERSION
            
        except Exception as e:
            print(f"خطأ في قراءة الملف {filepath}: {e}")
            return None
    
    def check_compatibility(self, file_version: str, current_version: str = None) -> Dict[str, any]:
        """فحص التوافق بين الإصدارات"""
        if current_version is None:
            current_version = self.CURRENT_VERSION
        
        result = {
            "compatible": False,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        if not self.is_version_supported(file_version):
            result["errors"].append(f"الإصدار {file_version} غير مدعوم")
            return result
        
        comparison = self.compare_versions(file_version, current_version)
        
        if comparison == 0:
            # نفس الإصدار
            result["compatible"] = True
        elif comparison < 0:
            # إصدار أقدم
            result["compatible"] = True
            result["warnings"].append(f"الملف يستخدم إصدار أقدم ({file_version})")
            
            # فحص التغييرات المهمة
            for version in self.SUPPORTED_VERSIONS:
                if self.compare_versions(file_version, version) < 0 and \
                   self.compare_versions(version, current_version) <= 0:
                    changes = self.VERSION_CHANGES.get(version, {})
                    if changes.get("breaking_changes"):
                        result["warnings"].extend([
                            f"تغييرات مهمة في الإصدار {version}:",
                            *changes["breaking_changes"]
                        ])
                    if changes.get("deprecated"):
                        result["warnings"].extend([
                            f"ميزات مهجورة في الإصدار {version}:",
                            *changes["deprecated"]
                        ])
        else:
            # إصدار أحدث
            result["errors"].append(f"الملف يتطلب إصدار أحدث ({file_version})")
            result["suggestions"].append(f"قم بتحديث ND-Script إلى الإصدار {file_version}")
        
        return result
    
    def get_version_info(self, version: str = None) -> Dict[str, any]:
        """الحصول على معلومات الإصدار"""
        if version is None:
            version = self.CURRENT_VERSION
        
        if version not in self.VERSION_CHANGES:
            return {"error": f"معلومات الإصدار {version} غير متوفرة"}
        
        return {
            "version": version,
            "current": version == self.CURRENT_VERSION,
            "supported": self.is_version_supported(version),
            **self.VERSION_CHANGES[version]
        }
    
    def generate_version_header(self, version: str = None) -> str:
        """توليد رأس الإصدار للملفات الجديدة"""
        if version is None:
            version = self.CURRENT_VERSION
        
        header = f"""// ND-Script File
// @version {version}
// @created {self._get_current_timestamp()}
// @description Quantum Fractal Universe Simulation
// ===============================================

"""
        return header
    
    def _get_current_timestamp(self) -> str:
        """الحصول على الطابع الزمني الحالي"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_file_version(self, filepath: str) -> Dict[str, any]:
        """التحقق من صحة إصدار الملف"""
        file_version = self.extract_version_from_file(filepath)
        
        if file_version is None:
            return {
                "valid": False,
                "error": "لا يمكن قراءة إصدار الملف",
                "suggestion": "أضف تعليق @version في بداية الملف"
            }
        
        compatibility = self.check_compatibility(file_version)
        
        return {
            "valid": compatibility["compatible"],
            "file_version": file_version,
            "current_version": self.CURRENT_VERSION,
            "compatibility": compatibility
        }

# دالة مساعدة للحصول على معلومات الإصدار
def get_version_info() -> str:
    """دالة للحصول على معلومات الإصدار الحالي"""
    vm = VersionManager()
    info = vm.get_version_info()
    
    output = f"""
🌟 ND-Script DSL - نظام محاكاة الأكوان الكسرية الكمية
Version: {info['version']}

📋 الميزات الحالية:
"""
    
    for feature in info.get('features', []):
        output += f"   ✅ {feature}\n"
    
    if info.get('breaking_changes'):
        output += f"\n⚠️ التغييرات المهمة:\n"
        for change in info['breaking_changes']:
            output += f"   🔄 {change}\n"
    
    output += f"""
🚀 حالة الإصدار: {'الحالي' if info['current'] else 'قديم'}
✅ مدعوم: {'نعم' if info['supported'] else 'لا'}

للمزيد من المعلومات، قم بزيارة: https://github.com/ndscript/ndscript
"""
    
    return output

if __name__ == "__main__":
    print(get_version_info())
