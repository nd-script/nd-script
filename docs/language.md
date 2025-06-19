# ND-Script Language Specification

## Overview

ND-Script is a domain-specific language (DSL) designed for quantum fractal universe simulation. It provides an intuitive interface for controlling complex physics simulations with support for both Arabic and English syntax.

## Language Features

- **Bilingual Support**: Commands available in both Arabic and English
- **Physics-Focused**: Built-in support for quantum and fractal physics parameters
- **Real-time Visualization**: Integrated plotting and analysis tools
- **Variable Management**: Dynamic variable storage and mathematical expressions
- **Control Flow**: Conditional statements and loops
- **File Operations**: Save and load simulation states

## Syntax Overview

### Comments

```ndscript
// Single-line comment
/* Multi-line
   comment */
```

### Basic Commands

#### Initialization
```ndscript
تهيئة                    // Initialize with defaults
init                     // English equivalent

تهيئة حجم=100            // Initialize with size
init size=100

تهيئة عمق=50 حجم=200     // Multiple parameters
init depth=50 size=200
```

#### Evolution
```ndscript
تطور                     // Evolve 1 step
evolve                   // English equivalent

تطور 10                  // Evolve 10 steps
evolve 10

تطور خطوات=100 سرعة=0.5  // With parameters
evolve steps=100 speed=0.5
```

#### Display and Visualization
```ndscript
عرض كثافة                // Show density
show density

عرض طاقة                 // Show energy
show energy

عرض حالة                 // Show state
show state

عرض إحصائيات             // Show statistics
show stats

عرض رسم                  // Show plot
show plot

عرض تحليل                // Show analysis
show analysis
```

#### Parameter Setting
```ndscript
ضبط جاذبية=0.5           // Set gravity
set gravity=0.5

ضبط عدم_انتظام=0.1       // Set irregularity
set irregularity=0.1

ضبط عتبة_انهيار=0.9      // Set collapse threshold
set collapse_threshold=0.9

ضبط كتلة=1.0             // Set mass
set mass=1.0

ضبط طاقة_كمية=0.8        // Set quantum energy
set quantum_energy=0.8
```

#### File Operations
```ndscript
حفظ "simulation.nds"     // Save state
save "simulation.nds"

تحميل "simulation.nds"   // Load state
load "simulation.nds"
```

#### Program Control
```ndscript
خروج                     // Exit program
exit
```

### Variables and Expressions

#### Variable Assignment
```ndscript
x = 10                   // Integer
y = 3.14159             // Float
name = "simulation"      // String
```

#### Mathematical Expressions
```ndscript
result = x + y * 2
area = π * r * r
energy = m * c * c
ratio = φ                // Golden ratio
```

#### Built-in Constants
- `π`, `pi` - Pi (3.14159...)
- `e` - Euler's number (2.71828...)
- `φ`, `phi` - Golden ratio (1.61803...)
- `c` - Speed of light
- `h` - Planck constant
- `ħ`, `hbar` - Reduced Planck constant

#### Built-in Functions
```ndscript
// Mathematical functions
sqrt(x), جذر(x)           // Square root
sin(x), cos(x), tan(x)   // Trigonometric
log(x), لوغ(x)           // Natural logarithm
exp(x), أس(x)            // Exponential
abs(x), مطلق(x)          // Absolute value
min(a,b), أدنى(a,b)      // Minimum
max(a,b), أعلى(a,b)      // Maximum
```

### Control Flow

#### Conditional Statements
```ndscript
إذا x > 10:              // If statement (Arabic)
    عرض "x is large"
وإلا:                    // Else
    عرض "x is small"

if energy > threshold:   // If statement (English)
    show "Critical level"
else:
    evolve 1
```

#### Loops
```ndscript
// For loop (Arabic)
كرر i في (1, 100):
    تطور 1
    إذا i % 10 == 0:
        عرض إحصائيات

// For loop (English)
for step in (1, 1000):
    evolve 1
    if step % 100 == 0:
        show stats

// While loop
بينما energy < max_energy:
    تطور 1
    energy = energy + 0.1

while condition:
    evolve 1
```

## Data Types

### Numbers
- **Integers**: `42`, `-17`, `0`
- **Floats**: `3.14159`, `-0.001`, `1.0`

### Strings
- **Double quotes**: `"Hello World"`
- **Single quotes**: `'simulation_name'`

### Booleans
- **True/False**: Used in conditions and comparisons

## Operators

### Arithmetic
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

### Comparison
- `==` Equal
- `!=` Not equal
- `<` Less than
- `>` Greater than
- `<=` Less than or equal
- `>=` Greater than or equal

### Assignment
- `=` Assignment

## Error Handling

ND-Script provides detailed error messages with line numbers and context:

```
Syntax Error: Line 5: Expected expression after '='
Runtime Error: Line 12: Universe not initialized. Use 'تهيئة' or 'init' first.
```

## Best Practices

1. **Initialize First**: Always initialize the universe before evolution
2. **Parameter Validation**: Check parameter ranges for physics accuracy
3. **Regular Monitoring**: Use `show stats` to monitor simulation health
4. **Save States**: Regularly save important simulation states
5. **Comments**: Document complex physics calculations
6. **Error Handling**: Check for critical conditions before continuing

## Example Programs

### Basic Simulation
```ndscript
// Initialize universe
تهيئة حجم=100

// Set physics parameters
ضبط جاذبية=0.5
ضبط عدم_انتظام=0.1

// Run simulation
تطور 50

// Display results
عرض كثافة
عرض إحصائيات

// Save results
حفظ "basic_sim.nds"
```

### Advanced Physics Study
```ndscript
// Golden ratio simulation
init size=161
set irregularity=φ/10
set gravity=1/φ

// Time evolution with monitoring
for step in (1, 1000):
    evolve 1
    
    current_energy = step * 0.001
    if current_energy > 0.9:
        show "Approaching critical energy"
        show analysis
        break
    
    if step % 100 == 0:
        show stats
        save "checkpoint_" + step + ".nds"

show "Simulation complete"
```

## Integration with Quantum Fractal Universe

ND-Script integrates seamlessly with the existing `QuantumFractalUniverse` class, providing:

- Direct parameter control
- Real-time visualization
- State management
- Physics analysis tools
- Performance monitoring

## File Extensions

- `.ndx` - ND-Script executable files
- `.nds` - ND-Script data/state files
