# SaltinoInterpreter

## How to run the project
To run the project, follow these steps:

1. Build and open the VS Code devcontainer.
2. Run a `.saltino` program with:
   ```bash
   python main.py <file.saltino>
   ```
3. To see runtime options, run:
   ```bash
   python main.py --help
   ```
4. To run the test suite, use:
   ```bash
   python -m pytest
   ```

## System architecture

The system is organized into modular components with specific responsibilities:

### Main components

1. Parser and grammar (`saltino_parser.py`, `Grammatica/`)
   - Uses ANTLR4 to generate the lexer, parser and visitor from `Saltino.g4`.
   - Parses source code with custom error listeners.
   - Builds the AST using the Visitor pattern implemented in `ASTVisitor.py`.

2. Abstract Syntax Tree (`AST/`)
   - `ASTNodes.py`: defines the AST node hierarchy and the Visitor pattern.
   - `ASTsymbol_table.py`: implements the symbol table with unique names to manage scopes.
   - `semantic_analyzer.py`: performs semantic analysis, annotating the AST with types, scopes and tail-call information.

3. Tail-call transformer (`tail_recursive_transformer.py`)
   - Scans the AST to identify non-tail-recursive patterns that can be transformed.
   - Automatically transforms suitable recursive functions into tail-recursive versions using accumulators.
   - Generates helper functions while preserving the original function signatures.

4. Iterative interpreter (`interpreter.py`)
   - Main class `IterativeSaltinoInterpreter` that eliminates recursion by using an explicit execution stack.
   - Uses execution frames (`ExecutionFrame`) to track the state of each operation.
   - Implements a dispatch table with specialized handlers for each frame type.

5. Execution frame system (`execution_frames.py`, `execution_handlers.py`)
   - `FrameType`: defines frame kinds (FUNCTION_CALL, BLOCK, EXPRESSION, CONDITION, IF_STATEMENT, ASSIGNMENT, RETURN).
   - Each frame holds state and the associated execution environment.
   - Specialized handlers implement the execution logic for each frame kind.

6. Execution environment (`execution_environment.py`)
   - Manages variables and functions using unique names provided by the symbol table.
   - Supports nested scopes with parent environment chaining.
   - Integrates with the semantic analyzer for name resolution.

## Tail Call Transformer documentation

The system includes a transformer for optimizing tail recursion:

### Full documentation
- **`tail_recursive_transformer.md`**: detailed documentation of the transformer module (English translation included in this repo).

### Key features
 - Pattern recognition: automatically detects transformable recursive patterns.
 - Safety: rejects patterns that could change semantics (for example list construction using `::`).
 - Interface preservation: keeps original function signatures.
 - Tests: a test suite verifies behavior and supported patterns.

### Supported patterns
 - Factorial: `n * factorial(n-1)`
 - Numeric sum: `n + sum(n-1)`
 - List operations: `1 + length(tail(lst))`
 - Dot product: `head(xs)*head(ys) + dot_product(tail(xs), tail(ys))`

### Execution flow

Phase 1: Parsing and analysis
1. The source file is parsed by the ANTLR parser and a parse tree is produced.
2. The `ASTVisitor` converts the parse tree into an AST.
3. The `TailCallTransformer` optimizes recursive functions by identifying specific patterns.
4. The `SemanticAnalyzer` inspects the AST, builds the symbol table and annotates nodes with semantic information.

Phase 2: Iterative execution
1. The interpreter registers all functions in the global environment.
2. It locates and invokes the `main` function with any provided input arguments.
3. Execution proceeds via an iterative loop that manages a stack of `ExecutionFrame` objects.
4. Each frame represents an ongoing operation (function call, block, expression, etc.).
5. Specialized handlers process frames according to their type.
6. Results propagate back through the stack until execution completes.

Stack management
 - Each operation is represented by a frame on the execution stack.
 - Frames hold state and reference the current execution environment.
 - The iterative approach prevents Python call-stack overflow.
 - The runtime collects execution statistics (max depth, total calls, tail calls optimized).

Tail-call optimization
 - Tail-recursive calls are detected at runtime.
 - Instead of creating new frames, the interpreter reuses the current frame by updating parameters and environment.
 - This prevents stack growth for deep recursions.
