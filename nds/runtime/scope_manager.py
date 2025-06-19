"""
ND-Script Scope Manager
Handles function scoping, parameter passing, and call stack management
"""

from typing import Any, Dict, List, Optional, Union
from .environment import Environment
from .errors import NDScriptRuntimeError


class CallFrame:
    """Represents a single function call frame"""
    
    def __init__(self, function_name: str, parameters: Dict[str, Any], environment: Environment):
        self.function_name = function_name
        self.parameters = parameters
        self.environment = environment
        self.return_value: Any = None
    
    def __repr__(self):
        return f"CallFrame(function='{self.function_name}', params={list(self.parameters.keys())})"


class ScopeManager:
    """Manages function scopes and call stack for ND-Script"""
    
    def __init__(self, global_environment: Environment):
        self.global_environment = global_environment
        self.call_stack: List[CallFrame] = []
        self.max_call_depth = 1000  # Prevent infinite recursion
    
    def enter_function(self, function_name: str, parameters: List[str], arguments: List[Any]) -> Environment:
        """Enter a new function scope"""
        if len(self.call_stack) >= self.max_call_depth:
            raise NDScriptRuntimeError(f"Maximum recursion depth exceeded in function '{function_name}'")
        
        if len(parameters) != len(arguments):
            raise NDScriptRuntimeError(
                f"Function '{function_name}' expects {len(parameters)} arguments, got {len(arguments)}"
            )
        
        # Create new environment for function scope
        function_env = self.global_environment.create_child()
        
        # Bind parameters to arguments
        param_dict = {}
        for param, arg in zip(parameters, arguments):
            function_env.define(param, arg)
            param_dict[param] = arg
        
        # Create and push call frame
        frame = CallFrame(function_name, param_dict, function_env)
        self.call_stack.append(frame)
        
        return function_env
    
    def exit_function(self, return_value: Any = None) -> Any:
        """Exit current function scope"""
        if not self.call_stack:
            raise NDScriptRuntimeError("Cannot exit function: no active function call")
        
        frame = self.call_stack.pop()
        frame.return_value = return_value
        return return_value
    
    def current_function(self) -> Optional[str]:
        """Get name of currently executing function"""
        if self.call_stack:
            return self.call_stack[-1].function_name
        return None
    
    def current_environment(self) -> Environment:
        """Get current environment (function scope or global)"""
        if self.call_stack:
            return self.call_stack[-1].environment
        return self.global_environment
    
    def get_call_stack_trace(self) -> List[str]:
        """Get call stack trace for error reporting"""
        trace = []
        for frame in reversed(self.call_stack):
            trace.append(f"  في الدالة '{frame.function_name}' - in function '{frame.function_name}'")
        return trace
    
    def is_in_function(self) -> bool:
        """Check if currently inside a function"""
        return len(self.call_stack) > 0
    
    def clear_stack(self):
        """Clear the call stack (for error recovery)"""
        self.call_stack.clear()
    
    def __repr__(self):
        return f"ScopeManager(stack_depth={len(self.call_stack)}, current={self.current_function()})"


class FunctionRegistry:
    """Registry for user-defined functions"""
    
    def __init__(self):
        self.functions: Dict[str, 'FunctionDef'] = {}
    
    def register_function(self, function_def: 'FunctionDef'):
        """Register a user-defined function"""
        self.functions[function_def.name] = function_def
    
    def get_function(self, name: str) -> Optional['FunctionDef']:
        """Get function definition by name"""
        return self.functions.get(name)
    
    def has_function(self, name: str) -> bool:
        """Check if function exists"""
        return name in self.functions
    
    def list_functions(self) -> List[str]:
        """Get list of all registered function names"""
        return list(self.functions.keys())
    
    def clear(self):
        """Clear all registered functions"""
        self.functions.clear()
    
    def __repr__(self):
        return f"FunctionRegistry(functions={list(self.functions.keys())})"
