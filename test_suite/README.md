# Suite di Test Completa per l'Interprete Saltino

Questa directory contiene una suite completa di test per validare l'interprete del linguaggio Saltino. I test sono organizzati in categorie che coprono tutti gli aspetti del linguaggio, inclusi casi di errore ed edge cases.

## Struttura della Suite di Test

### 1. **basic_functionality/** - Test di Funzionalità Base
- `hello_world.salt`: Test più semplice possibile
- `variable_assignment.salt`: Test di assegnamento base
- `empty_nested_blocks.salt`: Test di blocchi vuoti e annidati

### 2. **arithmetic/** - Test di Operazioni Aritmetiche
- `basic_operations.salt`: Operatori +, -, *, /, %
- `unary_operators.salt`: Operatori unari + e -
- `power_operations.salt`: Operatore ^ (associativo a destra)
- `precedence_test.salt`: Test di precedenza degli operatori
- `negative_zero_numbers.salt`: Test con numeri negativi e zero

### 3. **lists/** - Test di Liste
- `basic_list_operations.salt`: Costruzione base e head/tail
- `cons_associativity.salt`: Test associatività dell'operatore ::
- `cons_precedence.salt`: Test precedenza :: vs operatori aritmetici
- `nested_head_tail.salt`: Operazioni head/tail annidate
- `dynamic_list_construction.salt`: Costruzione dinamica di liste

### 4. **conditions/** - Test di Condizioni
- `comparison_operators.salt`: Operatori <, <=, ==, >, >=
- `logical_operators.salt`: Operatori and, or, !
- `logical_precedence.salt`: Precedenza dei connettivi logici
- `list_comparison.salt`: Confronto liste (solo == con [])
- `complex_conditions.salt`: Condizioni complesse con parentesi

### 5. **functions/** - Test di Funzioni
- `basic_function_calls.salt`: Chiamate di funzioni base
- `recursion_direct.salt`: Ricorsione diretta
- `recursion_mutual.salt`: Ricorsione mutua
- `multiple_parameters.salt`: Funzioni con parametri multipli
- `no_parameters.salt`: Funzioni senza parametri
- `nested_calls.salt`: Chiamate annidate
- `returning_conditions.salt`: Funzioni che restituiscono condizioni
- **Tail Recursion Tests** (Ottimizzazione delle Tail Call):
  - `tail_recursion_factorial.salt`: Factorial implementato con tail recursion
  - `tail_recursion_fibonacci.salt`: Fibonacci con tail recursion e accumulatore
  - `tail_recursion_sum.salt`: Somma di numeri naturali con tail recursion
  - `tail_recursion_power.salt`: Potenza/esponenziazione con tail recursion
  - `tail_recursion_countdown.salt`: Countdown semplice (test caso base)
  - `tail_recursion_gcd.salt`: Greatest Common Divisor con algoritmo di Euclide
  - `tail_recursion_mutual.salt`: Tail recursion mutua (even/odd test)
  - `tail_recursion_list_length.salt`: Calcolo lunghezza lista simulata
  - `tail_recursion_reverse.salt`: Reverse di numero (simula lista)
  - `tail_recursion_deep.salt`: Test di ricorsione profonda (1000 livelli)
  - `tail_vs_non_tail_comparison.salt`: Confronto tra tail e non-tail recursion
  - `tail_recursion_complex.salt`: Multiple tail calls in branches diverse
  - `tail_recursion_edge_cases.salt`: Edge cases (zero, negativi, caso base)

### 6. **variables_scope/** - Test di Scope delle Variabili
- `basic_scope.salt`: Scope di base
- `variable_shadowing.salt`: Shadowing delle variabili
- `scope_in_conditions.salt`: Scope nei blocchi if-else
- `scope_between_functions.salt`: Scope tra funzioni diverse
- `parameter_shadowing.salt`: Parametri che nascondono variabili

### 7. **error_cases/** - Test di Casi di Errore
- `division_by_zero.salt`: Divisione per zero
- `modulo_by_zero.salt`: Modulo per zero
- `arithmetic_on_booleans.salt`: Operatori aritmetici su booleani
- `logical_on_integers.salt`: Operatori logici su interi
- `cons_wrong_type.salt`: Operatore :: con tipi errati
- `head_empty_list.salt`: head su lista vuota
- `tail_empty_list.salt`: tail su lista vuota
- `head_on_non_list.salt`: head su tipo non lista
- `invalid_list_comparison.salt`: Confronti invalidi tra liste
- `undefined_function.salt`: Chiamata a funzione inesistente
- `undefined_variable.salt`: Uso di variabile non definita
- `wrong_parameter_count.salt`: Numero errato di parametri
- `missing_return.salt`: Funzione senza return

### 8. **edge_cases/** - Test di Edge Cases
- `large_numbers.salt`: Numeri molto grandi
- `deep_recursion.salt`: Ricorsione molto profonda
- `long_list.salt`: Liste molto lunghe
- `many_parameters.salt`: Funzioni con molti parametri
- `deeply_nested_blocks.salt`: Blocchi molto annidati
- `complex_nested_conditions.salt`: Condizioni molto complesse
- `deeply_nested_calls.salt`: Chiamate molto annidate
- `long_identifiers.salt`: Identificatori molto lunghi
- `complex_expressions.salt`: Espressioni molto complesse

## Come Utilizzare i Test

### Test che Dovrebbero Funzionare Correttamente
Tutti i test nelle directory `basic_functionality`, `arithmetic`, `lists`, `conditions`, `functions`, `variables_scope` e `edge_cases` dovrebbero essere eseguiti senza errori dall'interprete.

### Test che Dovrebbero Generare Errori
Tutti i test nella directory `error_cases` dovrebbero generare errori specifici:
- **Errori di runtime**: divisione/modulo per zero, head/tail su lista vuota
- **Errori di tipo**: operazioni su tipi incompatibili
- **Errori semantici**: variabili/funzioni non definite, parametri errati, funzioni senza return

## Caratteristiche Testate

### Sintassi
- ✅ Definizioni di funzioni con parametri
- ✅ Blocchi annidati
- ✅ Assegnamenti di variabili
- ✅ Istruzioni if-else
- ✅ Istruzioni return
- ✅ Chiamate di funzioni

### Operatori
- ✅ Aritmetici: +, -, *, /, %, ^
- ✅ Unari: +, -
- ✅ Liste: ::, head, tail
- ✅ Confronto: <, <=, ==, >, >=
- ✅ Logici: and, or, !

### Tipi
- ✅ Interi
- ✅ Booleani (true, false)
- ✅ Liste di interi
- ✅ Funzioni

### Precedenza e Associatività
- ✅ Precedenza corretta degli operatori
- ✅ Associatività a destra per ^ e ::
- ✅ Associatività a sinistra per +, -, *, /, %
- ✅ Precedenza dei connettivi logici

### Controllo dei Tipi Dinamico
- ✅ Verifica tipi in operazioni aritmetiche
- ✅ Verifica tipi in operazioni logiche
- ✅ Verifica tipi in operazioni su liste
- ✅ Verifica tipi nei confronti

### Scope e Visibilità
- ✅ Scope limitato ai blocchi
- ✅ Shadowing delle variabili
- ✅ Separazione scope tra funzioni

### Ricorsione
- ✅ Ricorsione diretta
- ✅ Ricorsione mutua
- ✅ Gestione stack di chiamate

## Note Implementative

Questi test sono progettati per essere esaustivi e coprire:
1. **Tutti i costrutti sintattici** del linguaggio
2. **Tutte le regole semantiche** specificate
3. **Tutti i possibili errori** di runtime e di tipo
4. **Edge cases** che potrebbero rivelare bug nascosti
5. **Casi limite** per stress-testing dell'interprete

La suite può essere utilizzata per:
- **Testing di regressione** durante lo sviluppo
- **Validazione della conformità** alle specifiche del linguaggio
- **Benchmark delle prestazioni** dell'interprete
- **Debugging** di problemi specifici
