#!/usr/bin/env python3
"""
ND-Script Command Line Interface
Main entry point for executing ND-Script files and REPL
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.interpreter import NDScriptInterpreter
from runtime.errors import NDScriptError, ErrorReporter


def run_file(filename: str, verbose: bool = False) -> int:
    """Run an ND-Script file"""
    try:
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            return 1
        
        interpreter = NDScriptInterpreter()
        
        if verbose:
            print(f"Executing ND-Script file: {filename}")
        
        result = interpreter.interpret_file(filename)
        
        if verbose:
            print(f"Execution completed successfully")
            if result is not None:
                print(f"Result: {result}")
        
        return 0
        
    except NDScriptError as e:
        # Read source for error reporting
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            reporter = ErrorReporter(source, filename)
            print(reporter.report_error(e), file=sys.stderr)
        except:
            print(f"Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_repl(verbose: bool = False) -> int:
    """Run interactive REPL"""
    print("ND-Script Interactive Shell")
    print("Type 'خروج' or 'exit' to quit, 'مساعدة' or 'help' for help")
    print()
    
    interpreter = NDScriptInterpreter()
    
    while True:
        try:
            # Get input
            try:
                line = input("nds> ")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return 0
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Handle special commands
            if line.strip() in ['خروج', 'exit']:
                print("Goodbye!")
                return 0
            
            if line.strip() in ['مساعدة', 'help']:
                print_help()
                continue
            
            if line.strip() in ['مسح', 'clear']:
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            # Execute the line
            try:
                result = interpreter.interpret(line)
                if result is not None and verbose:
                    print(f"=> {result}")
            except NDScriptError as e:
                reporter = ErrorReporter(line)
                print(reporter.report_error(e))
            except Exception as e:
                print(f"Error: {e}")
                if verbose:
                    import traceback
                    traceback.print_exc()
        
        except KeyboardInterrupt:
            print("\nUse 'خروج' or 'exit' to quit")
            continue


def print_help():
    """Print help information"""
    help_text = """
ND-Script Commands:
==================

Initialization:
  تهيئة / init                    - Initialize universe
  تهيئة حجم=100 / init size=100   - Initialize with specific size

Evolution:
  تطور / evolve                  - Evolve universe (1 step)
  تطور 10 / evolve 10           - Evolve universe (10 steps)

Display:
  عرض كثافة / show density       - Show density visualization
  عرض طاقة / show energy         - Show energy analysis
  عرض حالة / show state          - Show universe state
  عرض إحصائيات / show stats      - Show statistics

Parameters:
  ضبط جاذبية=0.5 / set gravity=0.5  - Set gravity parameter
  ضبط عدم_انتظام=0.1               - Set irregularity constant

File Operations:
  حفظ "file.nds" / save "file.nds"  - Save universe state
  تحميل "file.nds" / load "file.nds" - Load universe state

Variables:
  x = 10                         - Assign variable
  y = x + 5                      - Use variables in expressions

Control Flow:
  إذا x > 5: / if x > 5:         - Conditional statements
  كرر i في (1,10): / for i in (1,10):  - Loops

REPL Commands:
  مساعدة / help                  - Show this help
  مسح / clear                    - Clear screen
  خروج / exit                   - Exit REPL
"""
    print(help_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ND-Script: Domain-Specific Language for Quantum Fractal Universe Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nds script.ndx              # Run script file
  nds -i                      # Start interactive REPL
  nds -v script.ndx           # Run with verbose output
  nds --check script.ndx      # Check syntax only
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='ND-Script file to execute (.ndx extension)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Start interactive REPL'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check syntax only (do not execute)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ND-Script 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.interactive or (not args.file and not args.check):
        return run_repl(args.verbose)
    
    if args.file:
        if args.check:
            # Syntax check only
            try:
                interpreter = NDScriptInterpreter()
                with open(args.file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Parse only, don't execute
                interpreter.parser.parse(source)
                print(f"Syntax OK: {args.file}")
                return 0
            except Exception as e:
                print(f"Syntax Error in {args.file}: {e}", file=sys.stderr)
                return 1
        else:
            return run_file(args.file, args.verbose)
    
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
