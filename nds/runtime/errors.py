"""
ND-Script Error Handling
Custom exception classes for ND-Script interpreter
"""

from typing import Optional, Any


class NDScriptError(Exception):
    """Base exception for all ND-Script errors"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format error message with location information"""
        if self.line is not None:
            if self.column is not None:
                return f"Line {self.line}, Column {self.column}: {self.message}"
            else:
                return f"Line {self.line}: {self.message}"
        return self.message


class NDScriptSyntaxError(NDScriptError):
    """Syntax error in ND-Script code"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        super().__init__(f"Syntax Error: {message}", line, column)


class NDScriptRuntimeError(NDScriptError):
    """Runtime error during ND-Script execution"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        super().__init__(f"Runtime Error: {message}", line, column)


class NDScriptTypeError(NDScriptRuntimeError):
    """Type-related error"""
    
    def __init__(self, expected_type: str, actual_type: str, line: Optional[int] = None, column: Optional[int] = None):
        message = f"Expected {expected_type}, got {actual_type}"
        super().__init__(f"Type Error: {message}", line, column)


class NDScriptNameError(NDScriptRuntimeError):
    """Name/variable not found error"""
    
    def __init__(self, name: str, line: Optional[int] = None, column: Optional[int] = None):
        super().__init__(f"Name Error: '{name}' is not defined", line, column)


class NDScriptValueError(NDScriptRuntimeError):
    """Invalid value error"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        super().__init__(f"Value Error: {message}", line, column)


class NDScriptIOError(NDScriptError):
    """Input/Output error"""
    
    def __init__(self, message: str, filename: Optional[str] = None):
        if filename:
            message = f"File '{filename}': {message}"
        super().__init__(f"IO Error: {message}")


class NDScriptUniverseError(NDScriptRuntimeError):
    """Universe-related error"""
    
    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        super().__init__(f"Universe Error: {message}", line, column)


def format_error_context(source_lines: list, line: int, column: int, context_lines: int = 2) -> str:
    """Format error with source code context"""
    if not source_lines or line < 1 or line > len(source_lines):
        return ""
    
    start_line = max(1, line - context_lines)
    end_line = min(len(source_lines), line + context_lines)
    
    context = []
    for i in range(start_line, end_line + 1):
        line_num = str(i).rjust(4)
        source_line = source_lines[i - 1].rstrip()
        
        if i == line:
            # Highlight the error line
            context.append(f"{line_num} > {source_line}")
            if column > 0:
                # Add pointer to error column
                pointer = " " * (len(line_num) + 2 + column - 1) + "^"
                context.append(pointer)
        else:
            context.append(f"{line_num}   {source_line}")
    
    return "\n".join(context)


class ErrorReporter:
    """Error reporting utility"""
    
    def __init__(self, source: str = "", filename: str = ""):
        self.source = source
        self.filename = filename
        self.source_lines = source.splitlines() if source else []
    
    def report_error(self, error: NDScriptError) -> str:
        """Generate detailed error report"""
        report = []
        
        # Error header
        if self.filename:
            report.append(f"Error in {self.filename}:")
        
        # Error message
        report.append(str(error))
        
        # Source context
        if self.source_lines and error.line:
            report.append("")
            report.append("Source context:")
            context = format_error_context(
                self.source_lines, 
                error.line, 
                error.column or 0
            )
            report.append(context)
        
        return "\n".join(report)
    
    def report_syntax_error(self, message: str, line: int, column: int) -> str:
        """Report syntax error with context"""
        error = NDScriptSyntaxError(message, line, column)
        return self.report_error(error)
    
    def report_runtime_error(self, message: str, line: int = None, column: int = None) -> str:
        """Report runtime error with context"""
        error = NDScriptRuntimeError(message, line, column)
        return self.report_error(error)
