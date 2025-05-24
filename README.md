# Saltino Language Interpreter

A simple interpreter for the Saltino programming language, implemented in Python using ANTLR4 for lexing and parsing.

## Project Structure

- `Grammatica/` - Contains the ANTLR4 grammar and generated parser files
- `AST/` - Abstract Syntax Tree implementation
- `programs/` - Example Saltino programs
- `interpreter.py` - Main interpreter implementation

## Usage

To run a Saltino program:

```bash
python3 interpreter.py <program.salt>
```

Example:
```bash
python3 interpreter.py programs/factorial.salt
```

## Modifying the Grammar

If you need to modify the Saltino language grammar:

1. Navigate to the `Grammatica/` directory
2. Edit the `Saltino.g4` file with your grammar changes
3. Follow the instruction in the `Grammatica/README.md` to regenerate the parser files
   ```

This will regenerate all necessary parser files using ANTLR4.