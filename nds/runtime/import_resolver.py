"""
ND-Script Import Resolver
Handles file imports, circular dependency detection, and module caching
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from .errors import NDScriptError, NDScriptRuntimeError


class ImportedModule:
    """Represents an imported ND-Script module"""
    
    def __init__(self, filename: str, content: str, ast: Any = None):
        self.filename = filename
        self.content = content
        self.ast = ast
        self.functions: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.macros: Dict[str, Any] = {}
    
    def __repr__(self):
        return f"ImportedModule(file='{self.filename}', funcs={len(self.functions)}, vars={len(self.variables)})"


class ImportResolver:
    """Resolves and manages ND-Script file imports"""
    
    def __init__(self, interpreter=None):
        self.interpreter = interpreter
        self.imported_modules: Dict[str, ImportedModule] = {}
        self.import_stack: List[str] = []  # For circular dependency detection
        self.search_paths: List[str] = ['.']  # Default search path
    
    def add_search_path(self, path: str):
        """Add a directory to the import search path"""
        if path not in self.search_paths:
            self.search_paths.append(path)
    
    def resolve_import(self, filename: str, current_file: Optional[str] = None) -> ImportedModule:
        """Resolve and import an ND-Script file"""
        # Resolve the full path
        full_path = self._resolve_file_path(filename, current_file)
        
        # Check for circular imports
        if full_path in self.import_stack:
            cycle = ' -> '.join(self.import_stack + [full_path])
            raise NDScriptRuntimeError(f"Circular import detected: {cycle}")
        
        # Return cached module if already imported
        if full_path in self.imported_modules:
            return self.imported_modules[full_path]
        
        # Load and parse the file
        try:
            self.import_stack.append(full_path)
            module = self._load_module(full_path)
            self.imported_modules[full_path] = module
            return module
        
        finally:
            if full_path in self.import_stack:
                self.import_stack.remove(full_path)
    
    def _resolve_file_path(self, filename: str, current_file: Optional[str] = None) -> str:
        """Resolve the full path of an import file"""
        # Remove quotes if present
        filename = filename.strip('"\'')
        
        # Add extension if not present
        if not filename.endswith(('.ndx', '.nds')):
            filename += '.ndx'
        
        # Try different search strategies
        candidates = []
        
        # 1. Relative to current file
        if current_file:
            current_dir = os.path.dirname(os.path.abspath(current_file))
            candidates.append(os.path.join(current_dir, filename))
        
        # 2. Relative to search paths
        for search_path in self.search_paths:
            candidates.append(os.path.join(search_path, filename))
        
        # 3. Absolute path
        if os.path.isabs(filename):
            candidates.append(filename)
        
        # Find the first existing file
        for candidate in candidates:
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)
        
        # File not found
        raise NDScriptError(f"Import file not found: {filename}\nSearched in: {candidates}")
    
    def _load_module(self, filepath: str) -> ImportedModule:
        """Load and parse an ND-Script module"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            raise NDScriptError(f"Cannot read import file '{filepath}': {e}")
        
        # Create module object
        module = ImportedModule(filepath, content)
        
        # Parse the module if interpreter is available
        if self.interpreter:
            try:
                # Parse the content
                parse_tree = self.interpreter.parser.parse(content)
                ast = self.interpreter.transformer.transform(parse_tree)
                module.ast = ast
                
                # Extract functions, variables, and macros
                self._extract_module_symbols(module, ast)
                
            except Exception as e:
                raise NDScriptError(f"Error parsing import file '{filepath}': {e}")
        
        return module
    
    def _extract_module_symbols(self, module: ImportedModule, ast: Any):
        """Extract functions, variables, and macros from module AST"""
        if hasattr(ast, 'statements'):
            for stmt in ast.statements:
                if hasattr(stmt, '__class__'):
                    stmt_type = stmt.__class__.__name__
                    
                    if stmt_type == 'FunctionDef':
                        module.functions[stmt.name] = stmt
                    elif stmt_type == 'MacroDef':
                        module.macros[stmt.name] = stmt
                    elif stmt_type == 'Assignment':
                        # For assignments, we'd need to evaluate them
                        # This is simplified - in practice, you'd run the assignment
                        module.variables[stmt.identifier] = None
    
    def merge_module_into_scope(self, module: ImportedModule, target_scope: Any):
        """Merge imported module symbols into target scope"""
        # Merge functions
        if hasattr(target_scope, 'functions'):
            target_scope.functions.update(module.functions)
        
        # Merge macros
        if hasattr(target_scope, 'macros'):
            target_scope.macros.update(module.macros)
        
        # Merge variables into environment
        if hasattr(target_scope, 'environment'):
            for name, value in module.variables.items():
                if value is not None:
                    target_scope.environment.define(name, value)
    
    def get_imported_files(self) -> List[str]:
        """Get list of all imported file paths"""
        return list(self.imported_modules.keys())
    
    def clear_cache(self):
        """Clear the import cache"""
        self.imported_modules.clear()
        self.import_stack.clear()
    
    def is_imported(self, filepath: str) -> bool:
        """Check if a file has been imported"""
        return filepath in self.imported_modules
    
    def get_module_info(self, filepath: str) -> Optional[ImportedModule]:
        """Get information about an imported module"""
        return self.imported_modules.get(filepath)
    
    def validate_imports(self) -> List[str]:
        """Validate all imported modules and return any errors"""
        errors = []
        
        for filepath, module in self.imported_modules.items():
            if not os.path.isfile(filepath):
                errors.append(f"Imported file no longer exists: {filepath}")
        
        return errors
    
    def __repr__(self):
        return f"ImportResolver(modules={len(self.imported_modules)}, stack_depth={len(self.import_stack)})"
