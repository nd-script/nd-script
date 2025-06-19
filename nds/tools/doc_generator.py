#!/usr/bin/env python3
"""
مولد التوثيق التلقائي لـ ND-Script
Automatic Documentation Generator for ND-Script
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

# إضافة مسار nds للاستيراد
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.interpreter import NDScriptInterpreter
from runtime.type_system import create_type_checker
from api.ndscript_api import create_session

@dataclass
class FunctionDoc:
    """توثيق الدالة"""
    name: str
    parameters: List[str]
    parameter_types: Dict[str, str]
    return_type: Optional[str]
    description: str
    examples: List[str]
    language: str  # "arabic" or "english" or "mixed"

@dataclass
class ModuleDoc:
    """توثيق الوحدة"""
    name: str
    description: str
    functions: List[FunctionDoc]
    variables: Dict[str, Any]
    examples: List[str]

class NDScriptDocGenerator:
    """مولد التوثيق لـ ND-Script"""
    
    def __init__(self):
        self.session = create_session()
        self.type_checker = create_type_checker()
        self.docs = []
        
        # قوالب التوثيق
        self.templates = {
            "html": self._get_html_template(),
            "markdown": self._get_markdown_template(),
            "json": self._get_json_template()
        }
    
    def analyze_code(self, code: str, filename: str = "unknown") -> ModuleDoc:
        """تحليل الكود واستخراج التوثيق"""
        
        # تنفيذ الكود لاستخراج المعلومات
        result = self.session.execute(code, filename)
        
        if not result.success:
            print(f"Warning: Failed to execute {filename}: {result.error}")
            return ModuleDoc(filename, "Failed to analyze", [], {}, [])
        
        # استخراج الدوال
        functions = self._extract_functions(code)
        
        # استخراج المتغيرات
        variables = self.session.get_variables()
        
        # استخراج الأمثلة
        examples = self._extract_examples(code)
        
        # تحديد الوصف
        description = self._extract_module_description(code)
        
        return ModuleDoc(
            name=filename,
            description=description,
            functions=functions,
            variables=variables,
            examples=examples
        )
    
    def _extract_functions(self, code: str) -> List[FunctionDoc]:
        """استخراج الدوال من الكود"""
        functions = []
        
        # البحث عن تعريفات الدوال
        function_patterns = [
            r'دالة\s+(\w+)\s*\([^)]*\)\s*:?\s*\{',  # عربي مع أو بدون :
            r'function\s+(\w+)\s*\([^)]*\)\s*:?\s*\{',  # إنجليزي مع أو بدون :
            r'دالة\s+(\w+)\s*\([^)]*\)',  # عربي بدون أقواس
            r'function\s+(\w+)\s*\([^)]*\)'  # إنجليزي بدون أقواس
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                func_name = match.group(1)
                func_doc = self._analyze_function(func_name, code, match.start())
                if func_doc:
                    functions.append(func_doc)
        
        return functions
    
    def _analyze_function(self, func_name: str, code: str, start_pos: int) -> Optional[FunctionDoc]:
        """تحليل دالة محددة"""
        
        # استخراج تعريف الدالة
        lines = code[start_pos:].split('\n')
        func_def_line = lines[0] if lines else ""
        
        # استخراج المعاملات
        params_match = re.search(r'\(([^)]*)\)', func_def_line)
        parameters = []
        parameter_types = {}
        
        if params_match:
            params_str = params_match.group(1).strip()
            if params_str:
                # تحليل المعاملات مع الأنواع
                param_parts = [p.strip() for p in params_str.split(',')]
                for param in param_parts:
                    if ':' in param:
                        name, type_name = param.split(':', 1)
                        parameters.append(name.strip())
                        parameter_types[name.strip()] = type_name.strip()
                    else:
                        parameters.append(param)
        
        # استخراج نوع الإرجاع
        return_type = None
        return_match = re.search(r'\)\s*:\s*(\w+)\s*:', func_def_line)
        if return_match:
            return_type = return_match.group(1)
        
        # استخراج الوصف من التعليقات
        description = self._extract_function_description(lines)
        
        # استخراج الأمثلة
        examples = self._extract_function_examples(func_name, code)
        
        # تحديد اللغة
        language = "arabic" if "دالة" in func_def_line else "english"
        
        return FunctionDoc(
            name=func_name,
            parameters=parameters,
            parameter_types=parameter_types,
            return_type=return_type,
            description=description,
            examples=examples,
            language=language
        )
    
    def _extract_function_description(self, lines: List[str]) -> str:
        """استخراج وصف الدالة من التعليقات"""
        description = ""
        
        for line in lines[1:6]:  # البحث في أول 5 أسطر
            line = line.strip()
            if line.startswith('//'):
                desc_text = line[2:].strip()
                if desc_text:
                    description += desc_text + " "
            elif line.startswith('{'):
                break
        
        return description.strip() or "No description available"
    
    def _extract_function_examples(self, func_name: str, code: str) -> List[str]:
        """استخراج أمثلة استخدام الدالة"""
        examples = []
        
        # البحث عن استدعاءات الدالة
        call_pattern = rf'{func_name}\s*\([^)]*\)'
        matches = re.finditer(call_pattern, code)
        
        for match in matches:
            example = match.group(0)
            if example not in examples:
                examples.append(example)
        
        return examples[:3]  # أول 3 أمثلة
    
    def _extract_module_description(self, code: str) -> str:
        """استخراج وصف الوحدة"""
        lines = code.split('\n')
        
        for line in lines[:10]:  # البحث في أول 10 أسطر
            line = line.strip()
            if line.startswith('//') and len(line) > 10:
                return line[2:].strip()
        
        return "ND-Script module"
    
    def _extract_examples(self, code: str) -> List[str]:
        """استخراج أمثلة عامة من الكود"""
        examples = []
        
        # استخراج الإسنادات البسيطة
        assignment_pattern = r'^\s*\w+\s*=\s*[^=\n]+$'
        matches = re.finditer(assignment_pattern, code, re.MULTILINE)
        
        for match in matches:
            example = match.group(0).strip()
            if len(example) < 50:  # أمثلة قصيرة فقط
                examples.append(example)
        
        return examples[:5]  # أول 5 أمثلة
    
    def generate_html_doc(self, module_doc: ModuleDoc) -> str:
        """توليد توثيق HTML"""
        
        functions_html = ""
        for func in module_doc.functions:
            params_str = ", ".join([
                f"{p}: {func.parameter_types.get(p, 'any')}"
                for p in func.parameters
            ])
            
            examples_html = ""
            for example in func.examples:
                examples_html += f"<code>{example}</code><br>"
            
            functions_html += f"""
            <div class="function">
                <h3>🔧 {func.name}</h3>
                <p><strong>Parameters:</strong> {params_str}</p>
                <p><strong>Return Type:</strong> {func.return_type or 'void'}</p>
                <p><strong>Language:</strong> {func.language}</p>
                <p><strong>Description:</strong> {func.description}</p>
                <div class="examples">
                    <strong>Examples:</strong><br>
                    {examples_html}
                </div>
            </div>
            """
        
        variables_html = ""
        for name, value in module_doc.variables.items():
            variables_html += f"<li><code>{name}</code>: {type(value).__name__} = {value}</li>"
        
        examples_html = ""
        for example in module_doc.examples:
            examples_html += f"<li><code>{example}</code></li>"
        
        return self.templates["html"].format(
            module_name=module_doc.name,
            description=module_doc.description,
            functions=functions_html,
            variables=variables_html,
            examples=examples_html
        )
    
    def generate_markdown_doc(self, module_doc: ModuleDoc) -> str:
        """توليد توثيق Markdown"""
        
        functions_md = ""
        for func in module_doc.functions:
            params_str = ", ".join([
                f"{p}: {func.parameter_types.get(p, 'any')}" 
                for p in func.parameters
            ])
            
            examples_md = ""
            for example in func.examples:
                examples_md += f"- `{example}`\n"
            
            functions_md += f"""
### 🔧 {func.name}

**Parameters:** {params_str}
**Return Type:** {func.return_type or 'void'}
**Language:** {func.language}
**Description:** {func.description}

**Examples:**
{examples_md}

---

"""
        
        variables_md = ""
        for name, value in module_doc.variables.items():
            variables_md += f"- `{name}`: {type(value).__name__} = {value}\n"
        
        examples_md = ""
        for example in module_doc.examples:
            examples_md += f"- `{example}`\n"
        
        return self.templates["markdown"].format(
            module_name=module_doc.name,
            description=module_doc.description,
            functions=functions_md,
            variables=variables_md,
            examples=examples_md
        )
    
    def _get_html_template(self) -> str:
        """قالب HTML"""
        return """
<!DOCTYPE html>
<html dir="auto">
<head>
    <meta charset="UTF-8">
    <title>ND-Script Documentation - {module_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .function {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; border-radius: 5px; }}
        .examples {{ background: #e9ecef; padding: 10px; margin-top: 10px; border-radius: 3px; }}
        code {{ background: #f1f3f4; padding: 2px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 ND-Script Documentation</h1>
        <h2>{module_name}</h2>
        <p>{description}</p>
    </div>
    
    <h2>🔧 Functions</h2>
    {functions}
    
    <h2>📊 Variables</h2>
    <ul>{variables}</ul>
    
    <h2>💡 Examples</h2>
    <ul>{examples}</ul>
</body>
</html>
        """
    
    def _get_markdown_template(self) -> str:
        """قالب Markdown"""
        return """
# 📚 ND-Script Documentation

## {module_name}

{description}

## 🔧 Functions

{functions}

## 📊 Variables

{variables}

## 💡 Examples

{examples}

---
*Generated by ND-Script Documentation Generator*
        """
    
    def _get_json_template(self) -> str:
        """قالب JSON"""
        return "{}"  # سيتم استخدام json.dumps

def generate_documentation(source_files: List[str], output_dir: str = "docs", format: str = "html"):
    """توليد التوثيق لملفات متعددة"""
    
    generator = NDScriptDocGenerator()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"🔄 Generating {format.upper()} documentation...")
    
    for source_file in source_files:
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            module_doc = generator.analyze_code(code, Path(source_file).stem)
            
            if format == "html":
                doc_content = generator.generate_html_doc(module_doc)
                output_file = output_path / f"{module_doc.name}.html"
            elif format == "markdown":
                doc_content = generator.generate_markdown_doc(module_doc)
                output_file = output_path / f"{module_doc.name}.md"
            else:  # json
                doc_content = json.dumps(module_doc.__dict__, indent=2, ensure_ascii=False)
                output_file = output_path / f"{module_doc.name}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            print(f"✅ Generated: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {source_file}: {e}")
    
    print(f"🎉 Documentation generation complete! Output: {output_path}")

if __name__ == "__main__":
    # مثال للاستخدام
    sample_files = ["examples/sample.nds"]  # ملفات المثال
    generate_documentation(sample_files, "docs", "html")
