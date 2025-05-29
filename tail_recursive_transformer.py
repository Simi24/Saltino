"""
Trasformatore per convertire funzioni ricorsive in forma tail-recursive.

Questo modulo analizza l'AST e trasforma funzioni ricorsive con pattern noti
in forma tail-recursive utilizzando accumulatori, preparando il terreno per
future ottimizzazioni come trampolini o cicli espliciti.

Trasformazioni supportate:
1. Accumulator pattern per funzioni aritmetiche (es. factorial)
2. Accumulator pattern per somme/prodotti su sequenze
"""

from AST.ASTNodes import *
from typing import Dict, List, Optional, Set, Tuple, Any
import copy


class RecursionPattern:
    """Base class per pattern di ricorsione riconosciuti."""

    def __init__(self, function_name: str):
        self.function_name = function_name

    def can_transform(self, function: Function) -> bool:
        """Verifica se la funzione può essere trasformata con questo pattern."""
        raise NotImplementedError

    def transform(self, function: Function) -> List[Function]:
        """Trasforma la funzione in forma tail-recursive. Ritorna una lista di funzioni."""
        raise NotImplementedError


class AccumulatorPattern(RecursionPattern):
    """Pattern per trasformazioni con accumulatore (factorial, sum, product, etc.)."""

    def can_transform(self, function: Function) -> bool:
        """
        Verifica se la funzione segue il pattern:
        f(n) = if base_case then base_value else op(n, f(recursive_call))

        Dove op è una operazione associativa (+, *, etc.)
        """
        if len(function.parameters) != 1:
            return False

        # Deve avere un solo statement
        if len(function.body.statements) != 1:
            return False

        stmt = function.body.statements[0]

        # Può essere direttamente un if-statement o un return con if-statement
        if isinstance(stmt, IfStatement):
            return self._analyze_if_pattern(stmt)
        elif isinstance(stmt, ReturnStatement):
            if isinstance(stmt.value, IfStatement):
                return self._analyze_if_pattern(stmt.value)

        return False

    def _analyze_return_value(self, value) -> bool:
        """Analizza il valore di ritorno per trovare pattern ricorsivi."""
        if isinstance(value, IfStatement):
            return self._analyze_if_pattern(value)
        # Potrebbe essere un'espressione che contiene un if inline
        # Per ora gestiamo solo if-statement espliciti
        return False

    def _analyze_if_pattern(self, if_stmt: IfStatement) -> bool:
        """Analizza se l'if-statement segue il pattern ricorsivo."""
        # Verifica che entrambi i rami abbiano return
        if (len(if_stmt.then_block.statements) != 1 or
                not isinstance(if_stmt.then_block.statements[0], ReturnStatement)):
            return False

        if (if_stmt.else_block is None or
            len(if_stmt.else_block.statements) != 1 or
                not isinstance(if_stmt.else_block.statements[0], ReturnStatement)):
            return False

        # Il ramo else deve contenere ESATTAMENTE UNA chiamata ricorsiva
        else_return = if_stmt.else_block.statements[0]
        recursive_call_count = self._count_recursive_calls(else_return.value)
        
        # Accetta solo funzioni con esattamente una chiamata ricorsiva
        return recursive_call_count == 1

    def _contains_recursive_call(self, expr) -> bool:
        """Verifica se l'espressione contiene una chiamata ricorsiva."""
        return self._count_recursive_calls(expr) > 0

    def _count_recursive_calls(self, expr) -> int:
        """Conta il numero di chiamate ricorsive nell'espressione."""
        count = 0
        
        if isinstance(expr, FunctionCall):
            if isinstance(expr.function, Identifier):
                if expr.function.name == self.function_name:
                    count += 1
        elif isinstance(expr, BinaryExpression):
            count += self._count_recursive_calls(expr.left)
            count += self._count_recursive_calls(expr.right)
        elif isinstance(expr, UnaryExpression):
            count += self._count_recursive_calls(expr.operand)
        
        return count

    def transform(self, function: Function) -> List[Function]:
        """
        Trasforma una funzione in forma tail-recursive con accumulatore.

        Trasforma:
        def f(n) { if base_case then base_value else op(n, f(n-1)) }

        In:
        def f(n) { return f_aux(n, identity_value) }
        def f_aux(n, acc) { if base_case then acc else f_aux(n-1, op(acc, n)) }
        """
        # Estrae il pattern dalla funzione originale
        stmt = function.body.statements[0]
        if_stmt = None

        if isinstance(stmt, IfStatement):
            if_stmt = stmt
        elif isinstance(stmt, ReturnStatement) and isinstance(stmt.value, IfStatement):
            if_stmt = stmt.value

        if if_stmt is None:
            return [function]  # Non può essere trasformata

        # Analizza il pattern
        pattern_info = self._extract_pattern(if_stmt)
        if pattern_info is None:
            return [function]

        # Genera le nuove funzioni
        wrapper_func = self._create_wrapper_function(function, pattern_info)
        aux_func = self._create_auxiliary_function(function, pattern_info)

        return [wrapper_func, aux_func]

    def _extract_pattern(self, if_stmt: IfStatement) -> Optional[Dict[str, Any]]:
        """Estrae le informazioni del pattern dall'if-statement."""
        try:
            # Ramo base (then)
            base_return = if_stmt.then_block.statements[0]
            base_value = base_return.value

            # Ramo ricorsivo (else)
            recursive_return = if_stmt.else_block.statements[0]
            recursive_expr = recursive_return.value

            # Analizza l'espressione ricorsiva
            if isinstance(recursive_expr, BinaryExpression):
                operator = recursive_expr.operator

                # Determina quale operando contiene la chiamata ricorsiva
                if self._contains_recursive_call(recursive_expr.left):
                    current_term = recursive_expr.right
                    recursive_call = recursive_expr.left
                else:
                    current_term = recursive_expr.left
                    recursive_call = recursive_expr.right

                # Estrae gli argomenti della chiamata ricorsiva
                if isinstance(recursive_call, FunctionCall):
                    recursive_args = recursive_call.arguments
                else:
                    return None

                return {
                    'condition': if_stmt.condition,
                    'base_value': base_value,
                    'operator': operator,
                    'current_term': current_term,
                    'recursive_args': recursive_args,
                    'identity_value': self._get_identity_value(operator)
                }

            return None
        except (AttributeError, IndexError):
            return None

    def _get_identity_value(self, operator: str) -> IntegerLiteral:
        """Ritorna il valore identità per l'operatore."""
        if operator == '+':
            return IntegerLiteral(0)
        elif operator == '*':
            return IntegerLiteral(1)
        else:
            return IntegerLiteral(0)  # Default

    def _create_wrapper_function(self, original: Function, pattern_info: Dict[str, Any]) -> Function:
        """Crea la funzione wrapper che chiama quella ausiliaria."""
        # Crea la chiamata alla funzione ausiliaria
        aux_call = FunctionCall(
            function=Identifier(f"{original.name}_aux"),
            arguments=[
                Identifier(original.parameters[0]),  # parametro originale
                pattern_info['identity_value']       # valore identità
            ]
        )

        # Crea il return statement
        return_stmt = ReturnStatement(aux_call)

        # Crea il body
        body = Block([return_stmt])

        # Crea la nuova funzione
        return Function(
            name=original.name,
            parameters=original.parameters,
            body=body,
            position=original.position
        )

    def _create_auxiliary_function(self, original: Function, pattern_info: Dict[str, Any]) -> Function:
        """Crea la funzione ausiliaria tail-recursive."""
        param_name = original.parameters[0]
        acc_name = "acc"

        # Crea la condizione (stessa dell'originale)
        condition = copy.deepcopy(pattern_info['condition'])

        # Ramo base: return acc
        base_return = ReturnStatement(Identifier(acc_name))
        then_block = Block([base_return])

        # Ramo ricorsivo: chiamata tail-recursive
        # Calcola il nuovo accumulatore
        if pattern_info['operator'] == '*':
            new_acc = BinaryExpression(
                left=Identifier(acc_name),
                operator='*',
                right=copy.deepcopy(pattern_info['current_term'])
            )
        else:  # '+' o altri
            new_acc = BinaryExpression(
                left=Identifier(acc_name),
                operator='+',
                right=copy.deepcopy(pattern_info['current_term'])
            )

        # Argomenti per la chiamata ricorsiva
        recursive_args = [copy.deepcopy(arg)
                          for arg in pattern_info['recursive_args']]
        recursive_args.append(new_acc)

        # Chiamata ricorsiva
        recursive_call = FunctionCall(
            function=Identifier(f"{original.name}_aux"),
            arguments=recursive_args
        )

        recursive_return = ReturnStatement(recursive_call)
        else_block = Block([recursive_return])

        # If statement completo
        if_stmt = IfStatement(
            condition=condition,
            then_block=then_block,
            else_block=else_block
        )

        return_if = ReturnStatement(if_stmt)
        body = Block([return_if])

        # Crea la funzione ausiliaria
        return Function(
            name=f"{original.name}_aux",
            parameters=[param_name, acc_name],
            body=body,
            position=original.position
        )


class TailRecursiveTransformer:
    """Trasformatore principale per conversioni tail-recursive."""

    def __init__(self):
        self.patterns = [
            AccumulatorPattern("factorial"),
            AccumulatorPattern("sum"),
            AccumulatorPattern("product")
        ]

    def transform_program(self, program: Program) -> Program:
        """Trasforma tutte le funzioni del programma."""
        new_functions = []

        for function in program.functions:
            transformed = self.transform_function(function)
            new_functions.extend(transformed)

        return Program(new_functions, program.position)

    def transform_function(self, function: Function) -> List[Function]:
        """Trasforma una singola funzione se possibile."""
        # Cerca un pattern applicabile
        for pattern in self.patterns:
            pattern.function_name = function.name
            if pattern.can_transform(function):
                print(
                    f"Trasformando {function.name} con pattern {type(pattern).__name__}")
                return pattern.transform(function)

        # Se non può essere trasformata, ritorna la funzione originale
        return [function]

    def analyze_function(self, function: Function) -> Dict[str, Any]:
        """Analizza una funzione per determinare se può essere trasformata."""
        analysis = {
            'name': function.name,
            'can_transform': False,
            'pattern': None,
            'reason': None
        }

        # Verifica numero parametri
        if len(function.parameters) != 1:
            analysis['reason'] = f"Ha {len(function.parameters)} parametri invece di 1"
            return analysis

        # Verifica complessità del corpo
        if len(function.body.statements) != 1:
            analysis['reason'] = f"Corpo troppo complesso ({len(function.body.statements)} statements)"
            return analysis

        stmt = function.body.statements[0]

        # Verifica tipo di statement
        if not isinstance(stmt, (IfStatement, ReturnStatement)):
            analysis['reason'] = f"Statement principale è {type(stmt).__name__}, non IfStatement o ReturnStatement"
            return analysis

        # Cerca pattern applicabile
        for pattern in self.patterns:
            pattern.function_name = function.name
            if pattern.can_transform(function):
                analysis['can_transform'] = True
                analysis['pattern'] = type(pattern).__name__
                return analysis

        # Se arriviamo qui, è un pattern non riconosciuto
        if isinstance(stmt, IfStatement):
            analysis['reason'] = "IfStatement ma pattern non riconosciuto"
        elif isinstance(stmt, ReturnStatement):
            if isinstance(stmt.value, IfStatement):
                analysis['reason'] = "Return(IfStatement) ma pattern non riconosciuto"
            else:
                analysis['reason'] = f"Return con {type(stmt.value).__name__} invece di IfStatement"

        return analysis


def demo_transformation():
    """Dimostra l'uso del trasformatore."""
    # Crea un AST di esempio per factorial
    factorial_body = Block([
        ReturnStatement(
            IfStatement(
                condition=ComparisonCondition(
                    left=Identifier("n"),
                    operator="<=",
                    right=IntegerLiteral(1)
                ),
                then_block=Block([
                    ReturnStatement(IntegerLiteral(1))
                ]),
                else_block=Block([
                    ReturnStatement(
                        BinaryExpression(
                            left=Identifier("n"),
                            operator="*",
                            right=FunctionCall(
                                function=Identifier("factorial"),
                                arguments=[
                                    BinaryExpression(
                                        left=Identifier("n"),
                                        operator="-",
                                        right=IntegerLiteral(1)
                                    )
                                ]
                            )
                        )
                    )
                ])
            )
        )
    ])

    factorial_func = Function("factorial", ["n"], factorial_body)

    transformer = TailRecursiveTransformer()
    analysis = transformer.analyze_function(factorial_func)
    print("Analisi:", analysis)

    if analysis['can_transform']:
        transformed = transformer.transform_function(factorial_func)
        print(
            f"Trasformazione completata: {len(transformed)} funzioni generate")
        for func in transformed:
            print(f"- {func.name}: {func.parameters}")


if __name__ == "__main__":
    demo_transformation()
