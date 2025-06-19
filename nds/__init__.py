"""
ND-Script: Domain-Specific Language for Quantum Fractal Universe Simulation

A powerful DSL that combines Arabic and English syntax for intuitive
quantum fractal universe simulation and control.
"""

__version__ = "1.0.0"
__author__ = "ND-Script Development Team"
__email__ = "dev@nd-script.org"

from .runtime.interpreter import NDScriptInterpreter
from .runtime.errors import (
    NDScriptError,
    NDScriptSyntaxError,
    NDScriptRuntimeError,
    NDScriptTypeError,
    NDScriptNameError,
    NDScriptValueError,
    NDScriptIOError,
    NDScriptUniverseError
)

__all__ = [
    'NDScriptInterpreter',
    'NDScriptError',
    'NDScriptSyntaxError',
    'NDScriptRuntimeError',
    'NDScriptTypeError',
    'NDScriptNameError',
    'NDScriptValueError',
    'NDScriptIOError',
    'NDScriptUniverseError'
]
