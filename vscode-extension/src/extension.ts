import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    console.log('ND-Script extension is now active!');

    // Register commands
    const runCommand = vscode.commands.registerCommand('ndscript.run', () => {
        runNDScript();
    });

    const checkCommand = vscode.commands.registerCommand('ndscript.check', () => {
        checkSyntax();
    });

    const replCommand = vscode.commands.registerCommand('ndscript.repl', () => {
        startREPL();
    });

    context.subscriptions.push(runCommand, checkCommand, replCommand);

    // Register language features
    const provider = new NDScriptCompletionProvider();
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        'ndscript',
        provider,
        '.'
    );

    context.subscriptions.push(completionProvider);

    // Register hover provider
    const hoverProvider = vscode.languages.registerHoverProvider('ndscript', {
        provideHover(document, position, token) {
            const range = document.getWordRangeAtPosition(position);
            const word = document.getText(range);
            
            const hoverInfo = getHoverInfo(word);
            if (hoverInfo) {
                return new vscode.Hover(hoverInfo);
            }
        }
    });

    context.subscriptions.push(hoverProvider);
}

class NDScriptCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): vscode.ProviderResult<vscode.CompletionItem[] | vscode.CompletionList> {
        
        const completions: vscode.CompletionItem[] = [];

        // Arabic commands
        const arabicCommands = [
            { label: 'تهيئة', detail: 'Initialize universe', insertText: 'تهيئة حجم=${1:100}' },
            { label: 'تطور', detail: 'Evolve universe', insertText: 'تطور ${1:10}' },
            { label: 'عرض', detail: 'Show information', insertText: 'عرض ${1|كثافة,طاقة,حالة,إحصائيات,تحليل|}' },
            { label: 'ضبط', detail: 'Set parameter', insertText: 'ضبط ${1|جاذبية,عدم_انتظام|}=${2:0.5}' },
            { label: 'حفظ', detail: 'Save state', insertText: 'حفظ "${1:filename.nds}"' },
            { label: 'تحميل', detail: 'Load state', insertText: 'تحميل "${1:filename.nds}"' },
            { label: 'دالة', detail: 'Function definition with types', insertText: 'دالة ${1:function_name}(${2:param1}: ${3:رقم}، ${4:param2}: ${5:نص}): ${6:رقم} {\n\t${7:// function body}\n\tإرجاع ${8:result}\n}' },
            { label: 'ماكرو', detail: 'Macro definition', insertText: 'ماكرو ${1:macro_name}(): {\n\t${2:// macro body}\n}' },
            { label: 'استيراد', detail: 'Simple import', insertText: 'استيراد "${1:filename.ndx}"' },
            { label: 'استيراد_كـ', detail: 'Import with alias', insertText: 'استيراد "${1:filename.ndx}" كـ ${2:alias}' },
            { label: 'من_استيراد', detail: 'Selective import', insertText: 'من "${1:filename.ndx}" استيراد ${2:function_name}' },
            { label: 'إذا', detail: 'If statement', insertText: 'إذا (${1:condition}): {\n\t${2:// if body}\n}' },
            { label: 'إذا_وإلا_إذا', detail: 'If-elif-else statement', insertText: 'إذا (${1:condition1}): {\n\t${2:// if body}\n} وإلا_إذا (${3:condition2}): {\n\t${4:// elif body}\n} وإلا: {\n\t${5:// else body}\n}' },
            { label: 'طالما', detail: 'While loop', insertText: 'طالما (${1:condition}): {\n\t${2:// loop body}\n}' },
            { label: 'كرر', detail: 'For loop', insertText: 'كرر ${1:i} في (${2:1}, ${3:10}): {\n\t${4:// loop body}\n}' },
            { label: 'موازي_كرر', detail: 'Parallel for loop', insertText: 'موازي كرر ${1:i} في (${2:1}, ${3:10}): {\n\t${4:// parallel loop body}\n}' },
            { label: 'توقف', detail: 'Break statement', insertText: 'توقف' },
            { label: 'استمر', detail: 'Continue statement', insertText: 'استمر' },
            { label: 'إرجاع', detail: 'Return statement', insertText: 'إرجاع ${1:value}' },
            { label: 'تشخيص', detail: 'Debug statement', insertText: 'تشخيص("${1:debug message}")' },
            { label: 'تحليل_أداء', detail: 'Profile block', insertText: 'تحليل_أداء: {\n\t${1:// code to profile}\n}' }
        ];

        // English commands
        const englishCommands = [
            { label: 'init', detail: 'Initialize universe', insertText: 'init size=${1:100}' },
            { label: 'evolve', detail: 'Evolve universe', insertText: 'evolve ${1:10}' },
            { label: 'show', detail: 'Show information', insertText: 'show ${1|density,energy,state,stats,analysis|}' },
            { label: 'set', detail: 'Set parameter', insertText: 'set ${1|gravity,irregularity|}=${2:0.5}' },
            { label: 'save', detail: 'Save state', insertText: 'save "${1:filename.nds}"' },
            { label: 'load', detail: 'Load state', insertText: 'load "${1:filename.nds}"' },
            { label: 'function', detail: 'Function definition with types', insertText: 'function ${1:function_name}(${2:param1}: ${3:number}, ${4:param2}: ${5:string}): ${6:number} {\n\t${7:// function body}\n\treturn ${8:result}\n}' },
            { label: 'macro', detail: 'Macro definition', insertText: 'macro ${1:macro_name}(): {\n\t${2:// macro body}\n}' },
            { label: 'import', detail: 'Simple import', insertText: 'import "${1:filename.ndx}"' },
            { label: 'import_as', detail: 'Import with alias', insertText: 'import "${1:filename.ndx}" as ${2:alias}' },
            { label: 'from_import', detail: 'Selective import', insertText: 'from "${1:filename.ndx}" import ${2:function_name}' },
            { label: 'if', detail: 'If statement', insertText: 'if (${1:condition}): {\n\t${2:// if body}\n}' },
            { label: 'if_elif_else', detail: 'If-elif-else statement', insertText: 'if (${1:condition1}): {\n\t${2:// if body}\n} elif (${3:condition2}): {\n\t${4:// elif body}\n} else: {\n\t${5:// else body}\n}' },
            { label: 'while', detail: 'While loop', insertText: 'while (${1:condition}): {\n\t${2:// loop body}\n}' },
            { label: 'for', detail: 'For loop', insertText: 'for ${1:i} in (${2:1}, ${3:10}): {\n\t${4:// loop body}\n}' },
            { label: 'parallel_for', detail: 'Parallel for loop', insertText: 'parallel for ${1:i} in (${2:1}, ${3:10}): {\n\t${4:// parallel loop body}\n}' },
            { label: 'break', detail: 'Break statement', insertText: 'break' },
            { label: 'continue', detail: 'Continue statement', insertText: 'continue' },
            { label: 'return', detail: 'Return statement', insertText: 'return ${1:value}' },
            { label: 'debug', detail: 'Debug statement', insertText: 'debug("${1:debug message}")' },
            { label: 'profile', detail: 'Profile block', insertText: 'profile: {\n\t${1:// code to profile}\n}' }
        ];

        // Type system
        const typeSystem = [
            { label: 'رقم', detail: 'Number type (Arabic)', insertText: 'رقم' },
            { label: 'number', detail: 'Number type (English)', insertText: 'number' },
            { label: 'نص', detail: 'String type (Arabic)', insertText: 'نص' },
            { label: 'string', detail: 'String type (English)', insertText: 'string' },
            { label: 'منطق', detail: 'Boolean type (Arabic)', insertText: 'منطق' },
            { label: 'boolean', detail: 'Boolean type (English)', insertText: 'boolean' },
            { label: 'قائمة', detail: 'List type (Arabic)', insertText: 'قائمة[${1:رقم}]' },
            { label: 'list', detail: 'List type (English)', insertText: 'list[${1:number}]' },
            { label: 'كائن', detail: 'Object type (Arabic)', insertText: 'كائن' },
            { label: 'object', detail: 'Object type (English)', insertText: 'object' },
            { label: 'فراغ', detail: 'Void type (Arabic)', insertText: 'فراغ' },
            { label: 'void', detail: 'Void type (English)', insertText: 'void' }
        ];

        // Parameters
        const parameters = [
            { label: 'جاذبية', detail: 'Gravity parameter' },
            { label: 'gravity', detail: 'Gravity parameter' },
            { label: 'عدم_انتظام', detail: 'Irregularity parameter' },
            { label: 'irregularity', detail: 'Irregularity parameter' },
            { label: 'كثافة', detail: 'Density display' },
            { label: 'density', detail: 'Density display' },
            { label: 'طاقة_كمية', detail: 'Quantum energy parameter' },
            { label: 'quantum_energy', detail: 'Quantum energy parameter' },
            { label: 'كتلة', detail: 'Mass parameter' },
            { label: 'mass', detail: 'Mass parameter' }
        ];

        // Mathematical constants
        const mathConstants = [
            { label: 'π', detail: 'Pi constant', insertText: 'π' },
            { label: 'pi', detail: 'Pi constant', insertText: 'pi' },
            { label: 'e', detail: 'Euler\'s number', insertText: 'e' },
            { label: 'φ', detail: 'Golden ratio', insertText: 'φ' },
            { label: 'phi', detail: 'Golden ratio', insertText: 'phi' },
            { label: '∞', detail: 'Infinity', insertText: '∞' },
            { label: 'infinity', detail: 'Infinity', insertText: 'infinity' },
            { label: 'τ', detail: 'Tau constant', insertText: 'τ' },
            { label: 'tau', detail: 'Tau constant', insertText: 'tau' }
        ];

        // Add all completions
        [...arabicCommands, ...englishCommands].forEach(item => {
            const completion = new vscode.CompletionItem(item.label, vscode.CompletionItemKind.Keyword);
            completion.detail = item.detail;
            if (item.insertText) {
                completion.insertText = new vscode.SnippetString(item.insertText);
            }
            completions.push(completion);
        });

        // Add type system completions
        typeSystem.forEach(item => {
            const completion = new vscode.CompletionItem(item.label, vscode.CompletionItemKind.TypeParameter);
            completion.detail = item.detail;
            if (item.insertText) {
                completion.insertText = new vscode.SnippetString(item.insertText);
            }
            completions.push(completion);
        });

        // Add parameters
        parameters.forEach(item => {
            const completion = new vscode.CompletionItem(item.label, vscode.CompletionItemKind.Variable);
            completion.detail = item.detail;
            completions.push(completion);
        });

        // Add mathematical constants
        mathConstants.forEach(item => {
            const completion = new vscode.CompletionItem(item.label, vscode.CompletionItemKind.Constant);
            completion.detail = item.detail;
            if (item.insertText) {
                completion.insertText = new vscode.SnippetString(item.insertText);
            }
            completions.push(completion);
        });

        return completions;
    }
}

function getHoverInfo(word: string): string | undefined {
    const hoverMap: { [key: string]: string } = {
        // Basic commands - Arabic
        'تهيئة': '**Initialize Universe** (تهيئة الكون)\n\nInitializes a new quantum fractal universe.\n\n**Syntax:** `تهيئة حجم=size`\n\n**Example:** `تهيئة حجم=100`',
        'تطور': '**Evolve Universe** (تطوير الكون)\n\nEvolves the universe through time steps.\n\n**Syntax:** `تطور steps`\n\n**Example:** `تطور 50`',
        'عرض': '**Display Information** (عرض المعلومات)\n\nDisplays universe properties and analysis.\n\n**Options:** `كثافة`, `طاقة`, `حالة`, `إحصائيات`, `تحليل`\n\n**Example:** `عرض كثافة`',
        'ضبط': '**Set Parameter** (ضبط المعامل)\n\nSets physics parameters for the universe.\n\n**Syntax:** `ضبط parameter=value`\n\n**Example:** `ضبط جاذبية=0.7`',
        'حفظ': '**Save Universe** (حفظ الكون)\n\nSaves current universe state to file.\n\n**Syntax:** `حفظ "filename.nds"`\n\n**Example:** `حفظ "my_universe.nds"`',
        'تحميل': '**Load Universe** (تحميل الكون)\n\nLoads universe state from file.\n\n**Syntax:** `تحميل "filename.nds"`\n\n**Example:** `تحميل "saved_universe.nds"`',

        // Basic commands - English
        'init': '**Initialize Universe**\n\nInitializes a new quantum fractal universe.\n\n**Syntax:** `init size=value`\n\n**Example:** `init size=100`',
        'evolve': '**Evolve Universe**\n\nEvolves the universe through time steps.\n\n**Syntax:** `evolve steps`\n\n**Example:** `evolve 50`',
        'show': '**Display Information**\n\nDisplays universe properties and analysis.\n\n**Options:** `density`, `energy`, `state`, `stats`, `analysis`\n\n**Example:** `show density`',
        'set': '**Set Parameter**\n\nSets physics parameters for the universe.\n\n**Syntax:** `set parameter=value`\n\n**Example:** `set gravity=0.7`',
        'save': '**Save Universe**\n\nSaves current universe state to file.\n\n**Syntax:** `save "filename.nds"`\n\n**Example:** `save "my_universe.nds"`',
        'load': '**Load Universe**\n\nLoads universe state from file.\n\n**Syntax:** `load "filename.nds"`\n\n**Example:** `load "saved_universe.nds"`',

        // Advanced features - Arabic
        'دالة': '**Function Definition** (تعريف دالة)\n\nDefines a reusable function with optional type annotations.\n\n**Syntax:** `دالة function_name(param1: رقم، param2: نص): رقم { ... }`\n\n**Note:** Supports Arabic comma (،) in parameters and bilingual type annotations\n\n**Example:**\n```ndscript\nدالة حساب_المساحة(الطول: رقم، العرض: رقم): رقم {\n    إرجاع الطول * العرض\n}\n```',
        'ماكرو': '**Macro Definition** (تعريف ماكرو)\n\nDefines a reusable code template.\n\n**Syntax:** `ماكرو macro_name(params): { ... }`\n\n**Example:**\n```ndscript\nماكرو تجربة_سريعة(): {\n    تهيئة حجم=100\n    تطور 20\n    عرض حالة\n}\n```',
        'استيراد': '**Import Statement** (جملة الاستيراد)\n\nImports functions and macros from another file.\n\n**Syntax:** \n- Simple: `استيراد "filename.ndx"`\n- With alias: `استيراد "filename.ndx" كـ alias`\n- Selective: `من "filename.ndx" استيراد function_name`\n\n**Example:** `استيراد "physics_library.ndx"`',
        'من': '**From Import** (استيراد من)\n\nSelectively imports specific functions from a file.\n\n**Syntax:** `من "filename.ndx" استيراد function1، function2`\n\n**Example:** `من "math_lib.ndx" استيراد جذر، قوة`',
        'كـ': '**Import Alias** (استيراد كـ)\n\nImports a file with an alias name.\n\n**Syntax:** `استيراد "filename.ndx" كـ alias_name`\n\n**Example:** `استيراد "physics.ndx" كـ فيزياء`',
        'إرجاع': '**Return Statement** (جملة الإرجاع)\n\nReturns a value from a function.\n\n**Syntax:** `إرجاع value`\n\n**Example:**\n```ndscript\nدالة مربع(س: رقم): رقم {\n    إرجاع س * س\n}\n```',
        'وإلا_إذا': '**Elif Statement** (وإلا إذا)\n\nAdditional condition in if-elif-else chain.\n\n**Syntax:** `إذا (condition1): { ... } وإلا_إذا (condition2): { ... }`\n\n**Example:**\n```ndscript\nإذا (العمر < 18): {\n    print("طفل")\n} وإلا_إذا (العمر < 65): {\n    print("بالغ")\n} وإلا: {\n    print("كبير السن")\n}\n```',
        'موازي': '**Parallel Processing** (معالجة متوازية)\n\nExecutes loops in parallel for better performance.\n\n**Syntax:** `موازي كرر variable في range: { ... }`\n\n**Example:**\n```ndscript\nموازي كرر i في (1, 1000): {\n    // Parallel computation\n    نتيجة[i] = حساب_معقد(i)\n}\n```',

        // Advanced features - English
        'function': '**Function Definition**\n\nDefines a reusable function with optional type annotations.\n\n**Syntax:** `function function_name(param1: number, param2: string): number { ... }`\n\n**Example:**\n```ndscript\nfunction calculate_area(length: number, width: number): number {\n    return length * width\n}\n```',
        'macro': '**Macro Definition**\n\nDefines a reusable code template.\n\n**Syntax:** `macro macro_name(params): { ... }`\n\n**Example:**\n```ndscript\nmacro quick_test(): {\n    init size=100\n    evolve 20\n    show state\n}\n```',
        'import': '**Import Statement**\n\nImports functions and macros from another file.\n\n**Syntax:** \n- Simple: `import "filename.ndx"`\n- With alias: `import "filename.ndx" as alias`\n- Selective: `from "filename.ndx" import function_name`\n\n**Example:** `import "physics_library.ndx"`',
        'from': '**From Import**\n\nSelectively imports specific functions from a file.\n\n**Syntax:** `from "filename.ndx" import function1, function2`\n\n**Example:** `from "math_lib.ndx" import sqrt, pow`',
        'as': '**Import Alias**\n\nImports a file with an alias name.\n\n**Syntax:** `import "filename.ndx" as alias_name`\n\n**Example:** `import "physics.ndx" as physics`',
        'return': '**Return Statement**\n\nReturns a value from a function.\n\n**Syntax:** `return value`\n\n**Example:**\n```ndscript\nfunction square(x: number): number {\n    return x * x\n}\n```',
        'elif': '**Elif Statement**\n\nAdditional condition in if-elif-else chain.\n\n**Syntax:** `if (condition1): { ... } elif (condition2): { ... }`\n\n**Example:**\n```ndscript\nif (age < 18): {\n    print("child")\n} elif (age < 65): {\n    print("adult")\n} else: {\n    print("senior")\n}\n```',
        'parallel': '**Parallel Processing**\n\nExecutes loops in parallel for better performance.\n\n**Syntax:** `parallel for variable in range: { ... }`\n\n**Example:**\n```ndscript\nparallel for i in (1, 1000): {\n    // Parallel computation\n    result[i] = complex_calculation(i)\n}\n```',

        // Type System - Arabic
        'رقم': '**Number Type** (نوع الرقم)\n\nRepresents numeric values (integers and floats).\n\n**Usage:** `متغير: رقم = 42`\n\n**Example:**\n```ndscript\nدالة حساب(س: رقم، ص: رقم): رقم {\n    إرجاع س + ص\n}\n```',
        'نص': '**String Type** (نوع النص)\n\nRepresents text values.\n\n**Usage:** `اسم: نص = "أحمد"`\n\n**Example:**\n```ndscript\nدالة تحية(الاسم: نص): نص {\n    إرجاع "مرحباً " + الاسم\n}\n```',
        'منطق': '**Boolean Type** (نوع منطقي)\n\nRepresents true/false values.\n\n**Usage:** `نشط: منطق = صحيح`\n\n**Values:** `صحيح` (true), `خطأ` (false)',
        'قائمة': '**List Type** (نوع القائمة)\n\nRepresents arrays/lists of values.\n\n**Usage:** `أرقام: قائمة[رقم] = [1, 2, 3]`\n\n**Generic:** Supports type parameters like `قائمة[نص]`',
        'كائن': '**Object Type** (نوع الكائن)\n\nRepresents complex objects.\n\n**Usage:** `بيانات: كائن = {...}`',
        'فراغ': '**Void Type** (نوع الفراغ)\n\nRepresents no return value.\n\n**Usage:** `دالة طباعة(): فراغ { ... }`',

        // Type System - English
        'number': '**Number Type**\n\nRepresents numeric values (integers and floats).\n\n**Usage:** `variable: number = 42`\n\n**Example:**\n```ndscript\nfunction calculate(x: number, y: number): number {\n    return x + y\n}\n```',
        'string': '**String Type**\n\nRepresents text values.\n\n**Usage:** `name: string = "Ahmed"`\n\n**Example:**\n```ndscript\nfunction greet(name: string): string {\n    return "Hello " + name\n}\n```',
        'boolean': '**Boolean Type**\n\nRepresents true/false values.\n\n**Usage:** `active: boolean = true`\n\n**Values:** `true`, `false`',
        'list': '**List Type**\n\nRepresents arrays/lists of values.\n\n**Usage:** `numbers: list[number] = [1, 2, 3]`\n\n**Generic:** Supports type parameters like `list[string]`',
        'object': '**Object Type**\n\nRepresents complex objects.\n\n**Usage:** `data: object = {...}`',
        'void': '**Void Type**\n\nRepresents no return value.\n\n**Usage:** `function print(): void { ... }`',

        // Parameters
        'جاذبية': '**Gravity Parameter** (معامل الجاذبية)\n\nControls gravitational effects in the universe.\n\n**Range:** 0.0 - 1.0\n**Default:** 0.5\n\n**Usage:** `ضبط جاذبية=0.7`',
        'gravity': '**Gravity Parameter**\n\nControls gravitational effects in the universe.\n\n**Range:** 0.0 - 1.0\n**Default:** 0.5\n\n**Usage:** `set gravity=0.7`',
        'عدم_انتظام': '**Irregularity Parameter** (معامل عدم الانتظام)\n\nControls chaos and randomness in the universe.\n\n**Range:** 0.0 - 1.0\n**Default:** 0.1\n\n**Usage:** `ضبط عدم_انتظام=0.3`',
        'irregularity': '**Irregularity Parameter**\n\nControls chaos and randomness in the universe.\n\n**Range:** 0.0 - 1.0\n**Default:** 0.1\n\n**Usage:** `set irregularity=0.3`',
        'طاقة_كمية': '**Quantum Energy Parameter** (معامل الطاقة الكمية)\n\nControls quantum energy levels in the simulation.\n\n**Range:** 0.0 - 10.0\n**Default:** 1.0\n\n**Usage:** `ضبط طاقة_كمية=2.5`',
        'quantum_energy': '**Quantum Energy Parameter**\n\nControls quantum energy levels in the simulation.\n\n**Range:** 0.0 - 10.0\n**Default:** 1.0\n\n**Usage:** `set quantum_energy=2.5`',
        'كتلة': '**Mass Parameter** (معامل الكتلة)\n\nControls mass distribution in the universe.\n\n**Range:** 0.1 - 5.0\n**Default:** 1.0\n\n**Usage:** `ضبط كتلة=1.5`',
        'mass': '**Mass Parameter**\n\nControls mass distribution in the universe.\n\n**Range:** 0.1 - 5.0\n**Default:** 1.0\n\n**Usage:** `set mass=1.5`',

        // Display options
        'كثافة': '**Density Display** (عرض الكثافة)\n\nShows matter density distribution in the universe.\n\n**Usage:** `عرض كثافة`',
        'density': '**Density Display**\n\nShows matter density distribution in the universe.\n\n**Usage:** `show density`',
        'طاقة': '**Energy Display** (عرض الطاقة)\n\nShows energy levels and distribution.\n\n**Usage:** `عرض طاقة`',
        'energy': '**Energy Display**\n\nShows energy levels and distribution.\n\n**Usage:** `show energy`',
        'حالة': '**State Display** (عرض الحالة)\n\nShows current universe state and status.\n\n**Usage:** `عرض حالة`',
        'state': '**State Display**\n\nShows current universe state and status.\n\n**Usage:** `show state`',
        'إحصائيات': '**Statistics Display** (عرض الإحصائيات)\n\nShows detailed statistical analysis.\n\n**Usage:** `عرض إحصائيات`',
        'stats': '**Statistics Display**\n\nShows detailed statistical analysis.\n\n**Usage:** `show stats`',

        // Mathematical Constants
        'π': '**Pi Constant** (ثابت باي)\n\nThe ratio of a circle\'s circumference to its diameter.\n\n**Value:** 3.14159...\n\n**Usage:** `area = π * radius * radius`',
        'pi': '**Pi Constant**\n\nThe ratio of a circle\'s circumference to its diameter.\n\n**Value:** 3.14159...\n\n**Usage:** `area = pi * radius * radius`',
        'e': '**Euler\'s Number** (رقم أويلر)\n\nThe base of natural logarithms.\n\n**Value:** 2.71828...\n\n**Usage:** `result = e^x`',
        'φ': '**Golden Ratio** (النسبة الذهبية)\n\nThe golden ratio constant.\n\n**Value:** 1.61803...\n\n**Usage:** `ratio = φ`',
        'phi': '**Golden Ratio**\n\nThe golden ratio constant.\n\n**Value:** 1.61803...\n\n**Usage:** `ratio = phi`',
        '∞': '**Infinity** (ما لا نهاية)\n\nRepresents mathematical infinity.\n\n**Usage:** `limit = ∞`',
        'infinity': '**Infinity**\n\nRepresents mathematical infinity.\n\n**Usage:** `limit = infinity`',
        'τ': '**Tau Constant** (ثابت تاو)\n\nTwice the value of pi (2π).\n\n**Value:** 6.28318...\n\n**Usage:** `circumference = τ * radius`',
        'tau': '**Tau Constant**\n\nTwice the value of pi (2π).\n\n**Value:** 6.28318...\n\n**Usage:** `circumference = tau * radius`',

        // Boolean Constants
        'صحيح': '**True** (Boolean)\n\nBoolean true value in Arabic.\n\n**Usage:** `نشط: منطق = صحيح`',
        'خطأ': '**False** (Boolean)\n\nBoolean false value in Arabic.\n\n**Usage:** `مكتمل: منطق = خطأ`',
        'true': '**True** (Boolean)\n\nBoolean true value.\n\n**Usage:** `active: boolean = true`',
        'false': '**False** (Boolean)\n\nBoolean false value.\n\n**Usage:** `completed: boolean = false`'
    };

    return hoverMap[word];
}

function runNDScript() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active ND-Script file');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'ndscript') {
        vscode.window.showErrorMessage('Current file is not an ND-Script file');
        return;
    }

    // Save the file first
    document.save().then(() => {
        const terminal = vscode.window.createTerminal('ND-Script');
        terminal.sendText(`python -m nds.cli.nds "${document.fileName}"`);
        terminal.show();
    });
}

function checkSyntax() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active ND-Script file');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'ndscript') {
        vscode.window.showErrorMessage('Current file is not an ND-Script file');
        return;
    }

    document.save().then(() => {
        const terminal = vscode.window.createTerminal('ND-Script Syntax Check');
        terminal.sendText(`python -m nds.cli.nds --check "${document.fileName}"`);
        terminal.show();
    });
}

function startREPL() {
    const terminal = vscode.window.createTerminal('ND-Script REPL');
    terminal.sendText('python -m nds.cli.nds -i');
    terminal.show();
}

export function deactivate() {}
