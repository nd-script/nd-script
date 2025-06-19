#!/usr/bin/env python3
"""
Python API لـ ND-Script
Clean Python API for embedding ND-Script in external applications
"""

from .ndscript_api import (
    NDScript,
    NDScriptSession,
    NDScriptError,
    create_session,
    execute_code,
    execute_file,
    get_version,
    list_functions,
    get_function_signature,
    validate_syntax,
    format_code,
    get_performance_stats
)

from .jupyter_integration import (
    NDScriptMagics,
    load_ipython_extension,
    unload_ipython_extension
)

__version__ = "2.0.0"
__author__ = "ND-Script Development Team"
__description__ = "Bilingual Domain-Specific Language for Quantum Fractal Universe Simulation"

# تصدير الواجهات الرئيسية
__all__ = [
    # Core API
    "NDScript",
    "NDScriptSession", 
    "NDScriptError",
    "create_session",
    "execute_code",
    "execute_file",
    
    # Utility functions
    "get_version",
    "list_functions",
    "get_function_signature",
    "validate_syntax",
    "format_code",
    "get_performance_stats",
    
    # Jupyter integration
    "NDScriptMagics",
    "load_ipython_extension",
    "unload_ipython_extension",
    
    # Version info
    "__version__",
    "__author__",
    "__description__"
]
