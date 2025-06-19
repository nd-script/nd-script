#!/usr/bin/env python3
"""
استثناءات التحكم في التدفق لـ ND-Script
Control Flow Exceptions for ND-Script
"""

class ControlFlowException(Exception):
    """استثناء أساسي للتحكم في التدفق"""
    pass

class BreakException(ControlFlowException):
    """استثناء للخروج من الحلقة (break)"""
    def __init__(self, message="Break statement executed"):
        self.message = message
        super().__init__(self.message)

class ContinueException(ControlFlowException):
    """استثناء لمتابعة الحلقة (continue)"""
    def __init__(self, message="Continue statement executed"):
        self.message = message
        super().__init__(self.message)

class ReturnException(ControlFlowException):
    """استثناء للعودة من الدالة (return)"""
    def __init__(self, value=None, message="Return statement executed"):
        self.value = value
        self.message = message
        super().__init__(self.message)

class DebugBreakException(ControlFlowException):
    """استثناء لنقطة التوقف التشخيصية"""
    def __init__(self, message="Debug breakpoint reached"):
        self.message = message
        super().__init__(self.message)
