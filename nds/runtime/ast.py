"""
ND-Script Abstract Syntax Tree (AST) Node Definitions
Defines all AST node types for the ND-Script language
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Union, Dict, Tuple


class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern"""
        pass


@dataclass
class Program(ASTNode):
    """Root node representing the entire program"""
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_program(self)


# Command Nodes
@dataclass
class InitCommand(ASTNode):
    """Initialize universe command"""
    depth: Optional[int] = None
    size: Optional[int] = None
    dimensions: Optional[int] = None
    
    def accept(self, visitor):
        return visitor.visit_init_command(self)


@dataclass
class EvolveCommand(ASTNode):
    """Evolve universe command"""
    steps: Optional[int] = None
    speed: Optional[float] = None
    time: Optional[float] = None
    
    def accept(self, visitor):
        return visitor.visit_evolve_command(self)


@dataclass
class ShowCommand(ASTNode):
    """Display/visualization command"""
    target: str  # density, energy, state, stats, plot, analysis
    
    def accept(self, visitor):
        return visitor.visit_show_command(self)


@dataclass
class SetCommand(ASTNode):
    """Set parameter command"""
    parameter: str
    value: 'Expression'
    
    def accept(self, visitor):
        return visitor.visit_set_command(self)


@dataclass
class SaveCommand(ASTNode):
    """Save state command"""
    filename: str
    
    def accept(self, visitor):
        return visitor.visit_save_command(self)


@dataclass
class LoadCommand(ASTNode):
    """Load state command"""
    filename: str
    
    def accept(self, visitor):
        return visitor.visit_load_command(self)


@dataclass
class ExitCommand(ASTNode):
    """Exit program command"""
    
    def accept(self, visitor):
        return visitor.visit_exit_command(self)


# Assignment and Variables
@dataclass
class Assignment(ASTNode):
    """Variable assignment with optional type annotation"""
    identifier: str
    value: 'Expression'
    declared_type: Optional[str] = None

    def accept(self, visitor):
        return visitor.visit_assignment(self)

    def __repr__(self):
        type_info = f": {self.declared_type}" if self.declared_type else ""
        return f"Assignment({self.identifier}{type_info} = {self.value})"


@dataclass
class Identifier(ASTNode):
    """Variable identifier"""
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)


# Control Flow
@dataclass
class IfStatement(ASTNode):
    """If-else conditional statement"""
    condition: 'Expression'
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None
    
    def accept(self, visitor):
        return visitor.visit_if_statement(self)


@dataclass
class ForLoop(ASTNode):
    """For loop statement"""
    variable: str
    start: int
    end: int
    step: Optional[int] = None
    body: List[ASTNode] = None
    
    def accept(self, visitor):
        return visitor.visit_for_loop(self)


@dataclass
class WhileLoop(ASTNode):
    """While loop statement"""
    condition: 'Expression'
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_while_loop(self)


# Expressions
@dataclass
class Expression(ASTNode):
    """Base class for expressions"""
    pass


@dataclass
class BinaryOperation(Expression):
    """Binary operation expression"""
    left: Expression
    operator: str  # +, -, *, /, %, ==, !=, <, >, <=, >=
    right: Expression
    
    def accept(self, visitor):
        return visitor.visit_binary_operation(self)


@dataclass
class UnaryOperation(Expression):
    """Unary operation expression"""
    operator: str  # -, +
    operand: Expression
    
    def accept(self, visitor):
        return visitor.visit_unary_operation(self)


@dataclass
class Number(Expression):
    """Numeric literal"""
    value: Union[int, float]
    
    def accept(self, visitor):
        return visitor.visit_number(self)


@dataclass
class String(Expression):
    """String literal"""
    value: str
    
    def accept(self, visitor):
        return visitor.visit_string(self)


@dataclass
class FunctionCall(Expression):
    """Function call expression"""
    name: str
    arguments: List[Expression]
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)


@dataclass
class Comment(ASTNode):
    """Comment node"""
    text: str

    def accept(self, visitor):
        return visitor.visit_comment(self)


# Advanced Constructs
@dataclass
class FunctionDef(ASTNode):
    """Function definition with optional type annotations"""
    name: str
    parameters: List[str]
    body: List[ASTNode]
    parameter_types: Optional[Dict[str, str]] = None
    return_type: Optional[str] = None

    def accept(self, visitor):
        return visitor.visit_function_def(self)

    def __repr__(self):
        return f"FunctionDef(name='{self.name}', params={self.parameters}, return_type={self.return_type}, body_len={len(self.body)})"


@dataclass
class ImportStatement(ASTNode):
    """Simple import statement"""
    filename: str

    def accept(self, visitor):
        return visitor.visit_import_statement(self)

    def __repr__(self):
        return f"ImportStatement(filename='{self.filename}')"

@dataclass
class NamespaceImport(ASTNode):
    """Namespace import statement (import "file.ndx" as namespace)"""
    filename: str
    namespace: str

    def accept(self, visitor):
        return visitor.visit_namespace_import(self)

    def __repr__(self):
        return f"NamespaceImport(filename='{self.filename}', namespace='{self.namespace}')"

@dataclass
class SelectiveImport(ASTNode):
    """Selective import statement (from "file.ndx" import func1, func2)"""
    filename: str
    symbols: list

    def accept(self, visitor):
        return visitor.visit_selective_import(self)

    def __repr__(self):
        return f"SelectiveImport(filename='{self.filename}', symbols={self.symbols})"

# Control Flow AST Nodes
@dataclass
class IfStatement(ASTNode):
    """If statement with optional elif and else blocks"""
    condition: 'Expression'
    then_block: List['ASTNode']
    elif_blocks: List[Tuple['Expression', List['ASTNode']]]
    else_block: Optional[List['ASTNode']]

    def accept(self, visitor):
        return visitor.visit_if_statement(self)

    def __repr__(self):
        return f"IfStatement(condition={self.condition}, then_block={len(self.then_block)} stmts)"

@dataclass
class WhileStatement(ASTNode):
    """While loop statement"""
    condition: 'Expression'
    body: List['ASTNode']

    def accept(self, visitor):
        return visitor.visit_while_statement(self)

    def __repr__(self):
        return f"WhileStatement(condition={self.condition}, body={len(self.body)} stmts)"

@dataclass
class ForStatement(ASTNode):
    """For loop statement with range iteration"""
    variable: str
    start_expr: 'Expression'
    end_expr: 'Expression'
    step_expr: Optional['Expression']
    body: List['ASTNode']

    def accept(self, visitor):
        return visitor.visit_for_statement(self)

    def __repr__(self):
        return f"ForStatement(var={self.variable}, range=({self.start_expr}, {self.end_expr}), body={len(self.body)} stmts)"

@dataclass
class ParallelForStatement(ASTNode):
    """Parallel for loop statement with concurrent execution"""
    variable: str
    start_expr: 'Expression'
    end_expr: 'Expression'
    step_expr: Optional['Expression']
    body: List['ASTNode']

    def accept(self, visitor):
        return visitor.visit_parallel_for_statement(self)

    def __repr__(self):
        return f"ParallelForStatement(var={self.variable}, range=({self.start_expr}, {self.end_expr}), body={len(self.body)} stmts)"

@dataclass
class BreakStatement(ASTNode):
    """Break statement for loop control"""

    def accept(self, visitor):
        return visitor.visit_break_statement(self)

    def __repr__(self):
        return "BreakStatement()"

@dataclass
class ContinueStatement(ASTNode):
    """Continue statement for loop control"""

    def accept(self, visitor):
        return visitor.visit_continue_statement(self)

    def __repr__(self):
        return "ContinueStatement()"

@dataclass
class ReturnStatement(ASTNode):
    """Return statement for function control"""
    value: Optional['Expression'] = None

    def accept(self, visitor):
        return visitor.visit_return_statement(self)

    def __repr__(self):
        return f"ReturnStatement(value={self.value})"

# Debug and Profiling AST Nodes
@dataclass
class DebugStatement(ASTNode):
    """Debug statement for interactive debugging"""
    message: Optional[str]

    def accept(self, visitor):
        return visitor.visit_debug_statement(self)

    def __repr__(self):
        return f"DebugStatement(message={self.message})"

@dataclass
class ProfileBlock(ASTNode):
    """Profile block for performance analysis"""
    body: List['ASTNode']

    def accept(self, visitor):
        return visitor.visit_profile_block(self)

    def __repr__(self):
        return f"ProfileBlock(body={len(self.body)} stmts)"

# Comparison Expression
@dataclass
class ComparisonExpression(ASTNode):
    """Comparison expression for conditions"""
    left: 'Expression'
    operator: str
    right: 'Expression'

    def accept(self, visitor):
        return visitor.visit_comparison_expression(self)

    def __repr__(self):
        return f"ComparisonExpression({self.left} {self.operator} {self.right})"


@dataclass
class MacroDef(ASTNode):
    """Macro definition"""
    name: str
    parameters: List[str]
    body: List[ASTNode]

    def accept(self, visitor):
        return visitor.visit_macro_def(self)

    def __repr__(self):
        return f"MacroDef(name='{self.name}', params={self.parameters}, body_len={len(self.body)})"


# Visitor Interface
class ASTVisitor(ABC):
    """Abstract visitor for AST traversal"""
    
    @abstractmethod
    def visit_program(self, node: Program):
        pass
    
    @abstractmethod
    def visit_init_command(self, node: InitCommand):
        pass
    
    @abstractmethod
    def visit_evolve_command(self, node: EvolveCommand):
        pass
    
    @abstractmethod
    def visit_show_command(self, node: ShowCommand):
        pass
    
    @abstractmethod
    def visit_set_command(self, node: SetCommand):
        pass
    
    @abstractmethod
    def visit_save_command(self, node: SaveCommand):
        pass
    
    @abstractmethod
    def visit_load_command(self, node: LoadCommand):
        pass
    
    @abstractmethod
    def visit_exit_command(self, node: ExitCommand):
        pass
    
    @abstractmethod
    def visit_assignment(self, node: Assignment):
        pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier):
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatement):
        pass
    
    @abstractmethod
    def visit_for_loop(self, node: ForLoop):
        pass
    
    @abstractmethod
    def visit_while_loop(self, node: WhileLoop):
        pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation):
        pass
    
    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation):
        pass
    
    @abstractmethod
    def visit_number(self, node: Number):
        pass
    
    @abstractmethod
    def visit_string(self, node: String):
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall):
        pass
    
    @abstractmethod
    def visit_comment(self, node: Comment):
        pass

    @abstractmethod
    def visit_function_def(self, node: FunctionDef):
        pass

    @abstractmethod
    def visit_import_statement(self, node: ImportStatement):
        pass

    @abstractmethod
    def visit_macro_def(self, node: MacroDef):
        pass
