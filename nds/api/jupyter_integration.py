#!/usr/bin/env python3
"""
تكامل Jupyter Notebook لـ ND-Script
Jupyter Notebook Integration for ND-Script
"""

try:
    from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
    from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
    from IPython.display import display, HTML, JSON
    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False
    # إنشاء decorators وهمية للحالات التي لا يتوفر فيها Jupyter
    def magics_class(cls):
        return cls
    def line_magic(name):
        def decorator(func):
            return func
        return decorator
    def cell_magic(name):
        def decorator(func):
            return func
        return decorator
    def magic_arguments(func):
        return func
    def argument(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from .ndscript_api import create_session, NDScriptSession, ExecutionResult
import json
import time

if JUPYTER_AVAILABLE:
    @magics_class
    class NDScriptMagics(Magics):
        """ND-Script Magic Commands for Jupyter"""
        
        def __init__(self, shell):
            super().__init__(shell)
            self.session = create_session(enable_parallel=True, enable_bytecode=True)
            self.execution_count = 0
        
        @line_magic
        def ndscript_version(self, line):
            """عرض إصدار ND-Script"""
            from .ndscript_api import get_version
            version = get_version()
            display(HTML(f"""
            <div style="padding: 10px; background-color: #f0f8ff; border-left: 4px solid #4CAF50;">
                <h3>🚀 ND-Script Version</h3>
                <p><strong>Version:</strong> {version}</p>
                <p><strong>Description:</strong> Bilingual Domain-Specific Language for Quantum Fractal Universe Simulation</p>
            </div>
            """))
        
        @magic_arguments()
        @argument('--parallel', action='store_true', help='Enable parallel processing')
        @argument('--no-bytecode', action='store_true', help='Disable bytecode compilation')
        @argument('--profile', action='store_true', help='Show performance profiling')
        @argument('--arabic', action='store_true', help='Display output in Arabic')
        @cell_magic
        def ndscript(self, line, cell):
            """تنفيذ كود ND-Script في خلية Jupyter"""
            
            # تحليل المعاملات
            args = parse_argstring(self.ndscript, line) if line else None
            
            # إعداد الجلسة حسب المعاملات
            if args:
                if args.no_bytecode:
                    self.session.interpreter.disable_bytecode()
                else:
                    self.session.interpreter.enable_bytecode()
            
            # تنفيذ الكود
            start_time = time.perf_counter()
            result = self.session.execute(cell, f"<jupyter-cell-{self.execution_count}>")
            end_time = time.perf_counter()
            
            self.execution_count += 1
            
            # عرض النتائج
            self._display_execution_result(result, args)
            
            # عرض الإحصائيات إذا طُلب ذلك
            if args and args.profile:
                self._display_performance_stats()
            
            return result.result if result.success else None
        
        @line_magic
        def ndscript_vars(self, line):
            """عرض المتغيرات المعرفة"""
            variables = self.session.get_variables()
            
            if not variables:
                display(HTML("""
                <div style="padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <p>📝 No variables defined</p>
                </div>
                """))
                return
            
            # إنشاء جدول HTML للمتغيرات
            html = """
            <div style="padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff;">
                <h4>📊 ND-Script Variables</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e9ecef;">
                        <th style="padding: 8px; border: 1px solid #dee2e6;">Variable</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6;">Type</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6;">Value</th>
                    </tr>
            """
            
            for name, value in variables.items():
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{name}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{type(value).__name__}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{value_str}</td>
                    </tr>
                """
            
            html += """
                </table>
            </div>
            """
            
            display(HTML(html))
        
        @line_magic
        def ndscript_functions(self, line):
            """عرض الدوال المعرفة"""
            functions = self.session.get_functions()
            
            if not functions:
                display(HTML("""
                <div style="padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <p>🔧 No functions defined</p>
                </div>
                """))
                return
            
            # إنشاء جدول HTML للدوال
            html = """
            <div style="padding: 10px; background-color: #f8f9fa; border-left: 4px solid #28a745;">
                <h4>🔧 ND-Script Functions</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e9ecef;">
                        <th style="padding: 8px; border: 1px solid #dee2e6;">Function</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6;">Parameters</th>
                        <th style="padding: 8px; border: 1px solid #dee2e6;">Body Length</th>
                    </tr>
            """
            
            for name, info in functions.items():
                params = ", ".join(info.get("parameters", []))
                html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><code>{name}</code></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{params}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{info.get('body_length', 0)} statements</td>
                    </tr>
                """
            
            html += """
                </table>
            </div>
            """
            
            display(HTML(html))
        
        @line_magic
        def ndscript_stats(self, line):
            """عرض إحصائيات الجلسة"""
            self._display_performance_stats()
        
        @line_magic
        def ndscript_clear(self, line):
            """مسح الجلسة"""
            self.session.clear_session()
            self.execution_count = 0
            display(HTML("""
            <div style="padding: 10px; background-color: #d4edda; border-left: 4px solid #28a745;">
                <p>✅ ND-Script session cleared successfully</p>
            </div>
            """))
        
        def _display_execution_result(self, result: ExecutionResult, args=None):
            """عرض نتيجة التنفيذ"""
            if result.success:
                # نجح التنفيذ
                html = f"""
                <div style="padding: 10px; background-color: #d4edda; border-left: 4px solid #28a745;">
                    <p>✅ <strong>Execution successful</strong></p>
                    <p>⏱️ <strong>Time:</strong> {result.execution_time*1000:.2f}ms</p>
                """
                
                if result.result is not None:
                    html += f"<p>📤 <strong>Result:</strong> <code>{result.result}</code></p>"
                
                if result.memory_usage > 0:
                    html += f"<p>💾 <strong>Memory:</strong> {result.memory_usage:.2f}MB</p>"
                
                html += "</div>"
                display(HTML(html))
                
            else:
                # فشل التنفيذ
                html = f"""
                <div style="padding: 10px; background-color: #f8d7da; border-left: 4px solid #dc3545;">
                    <p>❌ <strong>Execution failed</strong></p>
                    <p>⏱️ <strong>Time:</strong> {result.execution_time*1000:.2f}ms</p>
                    <p>🚫 <strong>Error:</strong> <code>{result.error}</code></p>
                </div>
                """
                display(HTML(html))
        
        def _display_performance_stats(self):
            """عرض إحصائيات الأداء"""
            from .ndscript_api import get_performance_stats
            
            try:
                stats = get_performance_stats(self.session)
                
                html = f"""
                <div style="padding: 10px; background-color: #e2e3e5; border-left: 4px solid #6c757d;">
                    <h4>📊 Performance Statistics</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 8px; border: 1px solid #dee2e6;">Metric</th>
                            <th style="padding: 8px; border: 1px solid #dee2e6;">Value</th>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">Total Executions</td>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">{stats.get('executions', 0)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">Success Rate</td>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">{stats.get('success_rate', 0):.1f}%</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">Average Execution Time</td>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">{stats.get('average_execution_time', 0)*1000:.2f}ms</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">Total Execution Time</td>
                            <td style="padding: 8px; border: 1px solid #dee2e6;">{stats.get('total_execution_time', 0)*1000:.2f}ms</td>
                        </tr>
                    </table>
                </div>
                """
                
                display(HTML(html))
                
            except Exception as e:
                display(HTML(f"""
                <div style="padding: 10px; background-color: #f8d7da; border-left: 4px solid #dc3545;">
                    <p>❌ Error getting performance stats: {e}</p>
                </div>
                """))

else:
    # إنشاء فئة وهمية عندما لا يكون Jupyter متاحاً
    class NDScriptMagics:
        def __init__(self, shell=None):
            print("Jupyter not available. NDScript magics disabled.")

def load_ipython_extension(ipython):
    """تحميل امتداد ND-Script في IPython/Jupyter"""
    if JUPYTER_AVAILABLE:
        ipython.register_magic_function(NDScriptMagics(ipython).ndscript, 'cell')
        ipython.register_magic_function(NDScriptMagics(ipython).ndscript_version, 'line')
        ipython.register_magic_function(NDScriptMagics(ipython).ndscript_vars, 'line')
        ipython.register_magic_function(NDScriptMagics(ipython).ndscript_functions, 'line')
        ipython.register_magic_function(NDScriptMagics(ipython).ndscript_stats, 'line')
        ipython.register_magic_function(NDScriptMagics(ipython).ndscript_clear, 'line')
        
        print("✅ ND-Script Jupyter extension loaded successfully!")
        print("Available magics:")
        print("  %%ndscript - Execute ND-Script code in cell")
        print("  %ndscript_version - Show ND-Script version")
        print("  %ndscript_vars - Show defined variables")
        print("  %ndscript_functions - Show defined functions")
        print("  %ndscript_stats - Show performance statistics")
        print("  %ndscript_clear - Clear session")
    else:
        print("❌ Jupyter not available. Cannot load ND-Script extension.")

def unload_ipython_extension(ipython):
    """إلغاء تحميل امتداد ND-Script"""
    print("ND-Script Jupyter extension unloaded.")
