"""
ND-Script Macro Processor
Handles macro definition, expansion, and preprocessing
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from .errors import NDScriptRuntimeError


class MacroExpansion:
    """Represents a macro expansion result"""
    
    def __init__(self, expanded_code: str, original_call: str):
        self.expanded_code = expanded_code
        self.original_call = original_call
    
    def __repr__(self):
        return f"MacroExpansion(original='{self.original_call}', expanded_len={len(self.expanded_code)})"


class MacroProcessor:
    """Processes macros in ND-Script source code"""
    
    def __init__(self):
        self.macros: Dict[str, 'MacroDef'] = {}
        self.expansion_depth = 0
        self.max_expansion_depth = 50  # Prevent infinite macro expansion
        self.debug_expansions = False
    
    def register_macro(self, macro_def: 'MacroDef'):
        """Register a macro definition"""
        self.macros[macro_def.name] = macro_def
        if self.debug_expansions:
            print(f"Registered macro: {macro_def.name}({', '.join(macro_def.parameters)})")
    
    def has_macro(self, name: str) -> bool:
        """Check if macro exists"""
        return name in self.macros
    
    def preprocess(self, source_code: str) -> str:
        """Preprocess source code by expanding all macros"""
        self.expansion_depth = 0

        # First pass: extract macro definitions (simplified)
        lines = source_code.split('\n')
        processed_lines = []

        for line in lines:
            line = line.strip()
            # Skip macro definitions in preprocessing (they'll be handled by the parser)
            if line.startswith(('ماكرو ', 'macro ')):
                processed_lines.append(line)  # Keep macro definitions
            else:
                processed_lines.append(line)

        # For now, return the original source code
        # Macro expansion will be handled differently
        return source_code
    
    def _expand_macros_recursive(self, source_code: str) -> str:
        """Recursively expand macros in source code"""
        if self.expansion_depth >= self.max_expansion_depth:
            raise NDScriptRuntimeError("Maximum macro expansion depth exceeded")
        
        self.expansion_depth += 1
        
        try:
            # Find all macro calls in the source code
            macro_calls = self._find_macro_calls(source_code)
            
            if not macro_calls:
                return source_code  # No more macros to expand
            
            # Expand each macro call
            expanded_code = source_code
            for call_info in reversed(macro_calls):  # Process from end to preserve positions
                expansion = self._expand_macro_call(call_info)
                expanded_code = (
                    expanded_code[:call_info['start']] + 
                    expansion.expanded_code + 
                    expanded_code[call_info['end']:]
                )
            
            # Recursively expand any macros in the expanded code
            return self._expand_macros_recursive(expanded_code)
        
        finally:
            self.expansion_depth -= 1
    
    def _find_macro_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """Find all macro calls in source code"""
        macro_calls = []
        
        # Pattern to match function calls: identifier(args)
        pattern = r'([a-zA-Z_\u0600-\u06FF][a-zA-Z0-9_\u0600-\u06FF]*)\s*\(\s*([^)]*)\s*\)'
        
        for match in re.finditer(pattern, source_code):
            macro_name = match.group(1)
            args_str = match.group(2).strip()
            
            if self.has_macro(macro_name):
                # Parse arguments
                args = self._parse_arguments(args_str) if args_str else []
                
                macro_calls.append({
                    'name': macro_name,
                    'args': args,
                    'start': match.start(),
                    'end': match.end(),
                    'full_match': match.group(0)
                })
        
        return macro_calls
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse comma-separated arguments"""
        if not args_str.strip():
            return []
        
        # Simple argument parsing (handles strings and basic expressions)
        args = []
        current_arg = ""
        paren_depth = 0
        in_string = False
        
        for char in args_str:
            if char == '"' and (not current_arg or current_arg[-1] != '\\'):
                in_string = not in_string
                current_arg += char
            elif in_string:
                current_arg += char
            elif char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        return args
    
    def _expand_macro_call(self, call_info: Dict[str, Any]) -> MacroExpansion:
        """Expand a single macro call"""
        macro_name = call_info['name']
        args = call_info['args']
        
        if macro_name not in self.macros:
            raise NDScriptRuntimeError(f"Undefined macro: {macro_name}")
        
        macro_def = self.macros[macro_name]
        
        if len(args) != len(macro_def.parameters):
            raise NDScriptRuntimeError(
                f"Macro '{macro_name}' expects {len(macro_def.parameters)} arguments, got {len(args)}"
            )
        
        # Create parameter substitution map
        substitutions = dict(zip(macro_def.parameters, args))
        
        # Convert macro body to source code
        macro_body = self._ast_to_source(macro_def.body)
        
        # Substitute parameters
        expanded_code = self._substitute_parameters(macro_body, substitutions)
        
        if self.debug_expansions:
            print(f"Expanded macro {macro_name}: {call_info['full_match']} -> {expanded_code}")
        
        return MacroExpansion(expanded_code, call_info['full_match'])
    
    def _substitute_parameters(self, code: str, substitutions: Dict[str, str]) -> str:
        """Substitute macro parameters in code"""
        result = code
        
        for param, value in substitutions.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(param) + r'\b'
            result = re.sub(pattern, value, result)
        
        return result
    
    def _ast_to_source(self, statements: List['ASTNode']) -> str:
        """Convert AST nodes back to source code (simplified)"""
        # This is a simplified implementation
        # In a full implementation, you'd have a proper AST-to-source converter
        lines = []
        for stmt in statements:
            lines.append(self._node_to_source(stmt))
        return '\n'.join(lines)
    
    def _node_to_source(self, node: 'ASTNode') -> str:
        """Convert single AST node to source code (simplified)"""
        # This is a placeholder - in practice, you'd implement proper source generation
        return str(node)
    
    def clear_macros(self):
        """Clear all registered macros"""
        self.macros.clear()
    
    def list_macros(self) -> List[str]:
        """Get list of all registered macro names"""
        return list(self.macros.keys())
    
    def enable_debug(self, enabled: bool = True):
        """Enable/disable debug output for macro expansions"""
        self.debug_expansions = enabled
    
    def __repr__(self):
        return f"MacroProcessor(macros={list(self.macros.keys())}, depth={self.expansion_depth})"
