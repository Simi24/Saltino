# Tail-Recursive Transformer

## Overview

The module `tail_recursive_transformer.py` implements an automatic transformer that converts non-tail-recursive functions into optimized tail-recursive form. The transformer inspects the program's Abstract Syntax Tree (AST), identifies specific recursive patterns and rewrites them using helper functions with accumulators to enable tail-call optimization (TCO).

## How it works

### Transformer architecture

The transformer follows a two-phase approach:

1. Pattern matching phase: examine each function to identify transformable recursive patterns.
2. AST rewrite phase: when a compatible pattern is found, generate:
   - a tail-recursive helper function with an accumulator
   - a wrapper function that preserves the original signature

### Generated function structure

For each transformed recursive function the system produces:

```
original_function(param) -> original_function_tc_helper(param, acc)
                         -> original_function(param) [wrapper]
```

Example — factorial:

```saltino
factorial(n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```

Is transformed into:

```saltino
factorial_tc_helper_1(n, acc) {
    if (n <= 1) {
        return acc;
    } else {
        return factorial_tc_helper_1(n - 1, acc * n);
    }
}

factorial(n) {
    return factorial_tc_helper_1(n, 1);
}
```

## Recognized and transformable patterns

### Supported base pattern

The transformer recognizes functions following this scheme:

```saltino
function_name(param1 [, param2]) {
    if (param1 == base_value) {
        return initial_value;
    } else {
        return param1 operator function_name(modified_param1 [, modified_param2]);
    }
}
```

### Validation criteria

A function is transformable only if it meets all of these criteria:

1. Number of parameters: exactly 1 or 2
2. Body structure: a single statement (typically an if-statement)
3. Base case: comparison with a constant value
4. Base return value: a literal constant (integer, boolean, or identifier)
5. Recursive case: a binary expression containing the recursive call
6. Supported operator: any operator except `::` (list construction)
7. Recursive call position: one of the two operands of the binary expression
8. Call arguments: valid transformations of the original parameters

### Examples of transformable patterns

1) Single-parameter arithmetic functions

Factorial:

```saltino
factorial(n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```
- Operator: `*` (multiplication)
- Initial accumulator: `1`
- Transformation: `acc * n` on each iteration

Sum from 1 to n:

```saltino
sum(n) {
    if (n <= 0) {
        return 0;
    } else {
        return n + sum(n - 1);
    }
}
```
- Operator: `+`
- Initial accumulator: `0`
- Transformation: `acc + n`

2) Single-parameter list functions

Length of a list:

```saltino
length(lst) {
    if (lst == []) {
        return 0;
    } else {
        return 1 + length(tail(lst));
    }
}
```
- Operator: `+`
- Initial accumulator: `0`
- Transformation: `acc + 1`

Sum of list elements:

```saltino
sum_list(lst) {
    if (lst == []) {
        return 0;
    } else {
        return head(lst) + sum_list(tail(lst));
    }
}
```
- Operator: `+`
- Initial accumulator: `0`
- Transformation: `acc + head(lst)`

3) Two-parameter functions

Dot product:

```saltino
dot_product(xs, ys) {
    if (xs == []) {
        return 0;
    } else {
        return head(xs) * head(ys) + dot_product(tail(xs), tail(ys));
    }
}
```
- Operator: `+`
- Initial accumulator: `0`
- Transformation: `acc + (head(xs) * head(ys))`

### Patterns that are NOT transformable

1) List construction using the `::` operator

Reason: functions that build lists with `::` cannot be safely transformed with a simple accumulator without changing semantics.

Problematic example:

```saltino
append(xs, ys) {
    if (xs == []) {
        return ys;
    } else {
        return head(xs) :: append(tail(xs), ys);
    }
}
```

Issue: a naive accumulator-based transformation would reverse element order:
- `append([1,2], [3,4])` should return `[1,2,3,4]`
- A naive tail-recursive version would return `[2,1,3,4]`

Future solution: these patterns require advanced techniques such as continuation-passing style.

2) Other unsupported patterns

- Functions with more than 2 parameters
- Functions with complex bodies (multiple statements)
- Functions with multiple recursive calls
- Recursive calls in non-operand positions

## Benefits of the transformation

### Performance improvements
- Avoids stack overflow: tail-recursive functions can be optimized by the runtime.
- Constant memory usage: O(1) instead of O(n) for recursion depth.
- Better performance: reduced function-call overhead.

### Safety and robustness
- Conservative pattern matching: only semantically safe transformations are applied.
- Signature preservation: public interfaces remain unchanged.
- Backwards compatible: existing code continues to work as before.

## Current limitations

1) Limited pattern coverage
- Only simple recursive patterns with a single recursive call are handled.
- Complex list constructions are excluded.
- Limited to functions with 1 or 2 parameters.

2) Excluded operators
- The `::` operator is excluded (needs continuation-passing style).
- Patterns that update data non-cumulatively are not supported.

3) Static analysis
- No advanced control-flow analysis is performed.
- No inter-procedural optimizations are applied.

## Usage examples

Programmatic transformation

```python
from tail_recursive_transformer import TailCallTransformer

# Create transformer instance
transformer = TailCallTransformer()

# Transform a program AST
transformed_program = transformer.transform_program(original_program)

# The transformed program contains the original functions
# (now wrappers) plus the generated helper functions.
```

Function analysis

```python
from tail_recursive_transformer import analyze_function_pattern

# Analyze whether a function can be transformed
analysis = analyze_function_pattern(function_ast)
print(f"Transformable: {analysis['can_transform']}")
if not analysis['can_transform']:
    print(f"Reason: {analysis['reason']}")
```

## Testing and validation

### Test suite

The transformer is accompanied by a test suite (`test_tail_call_transformer.py`) that covers:

- Pattern recognition tests (factorial, sum, list length, sum_list, product_list, dot_product).
- Transformation tests (helper generation, wrapper preservation, semantic correctness).
- Rejection tests (non-recursive functions, too many parameters, unsupported patterns).

### Pattern analysis

`analyze_function_pattern()` provides diagnostic information:

```python
from tail_recursive_transformer import analyze_function_pattern
analysis = analyze_function_pattern(function_ast)
print(f"Transformable: {analysis['can_transform']}")
if analysis['can_transform']:
    print(f"Pattern: {analysis['pattern_info']}")
else:
    print(f"Exclusion reason: {analysis['reason']}")
```

### Current test status

All 24 tests in the suite pass, covering:
- 7 pattern recognition tests
- 6 AST transformation tests
- 4 rejection tests for unsupported patterns
- 7 diagnostic analysis tests

## Conclusion

The tail-recursive transformer offers a pragmatic approach to automatically optimizing recursive code. Despite current limitations, it provides meaningful performance improvements for a useful class of recursive functions while preserving semantic correctness and API compatibility.

Its modular and extensible design allows future extensions to support more complex patterns and advanced optimization techniques.
