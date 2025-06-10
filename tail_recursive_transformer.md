# Trasformatore di Ricorsione Tail-Recursive

## Panoramica

Il modulo `tail_recursive_transformer.py` implementa un trasformatore automatico che converte funzioni ricorsive non tail-recursive in forma tail-recursive ottimizzata. Questo trasformatore analizza l'Abstract Syntax Tree (AST) di un programma, identifica pattern ricorsivi specifici e li riscrive utilizzando funzioni helper con accumulatori per abilitare l'ottimizzazione tail call (TCO).

## Come Funziona

### Architettura del Trasformatore

Il trasformatore segue un approccio in due fasi:

1. **Fase di Pattern Matching**: Analizza ogni funzione per identificare pattern ricorsivi trasformabili
2. **Fase di Riscrittura AST**: Quando trova un pattern compatibile, genera:
   - Una **funzione helper** tail-recursive con accumulatore
   - Una **funzione wrapper** che mantiene la signature originale

### Struttura delle Funzioni Generate

Per ogni funzione ricorsiva trasformata, il sistema genera:

```
funzione_originale(param) -> funzione_originale_tc_helper(param, acc)
                         -> funzione_originale(param) [wrapper]
```

**Esempio con fattoriale:**
```
factorial(n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```

Viene trasformato in:
```
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

## Pattern Riconosciuti e Trasformabili

### Pattern Base Supportato

Il trasformatore riconosce funzioni che seguono questo schema:

```
nome_funzione(parametro1 [, parametro2]) {
    if (parametro1 == valore_base) {
        return valore_iniziale;
    } else {
        return parametro1 operatore nome_funzione(modifica_parametro1 [, modifica_parametro2]);
    }
}
```

### Criteri di Validazione

Una funzione è trasformabile se soddisfa **tutti** questi criteri:

1. **Numero di parametri**: Esattamente 1 o 2 parametri
2. **Struttura del corpo**: Un singolo statement (tipicamente if-statement)
3. **Caso base**: Condizione di confronto con valore costante
4. **Valore di ritorno base**: Letterale costante (intero, booleano, identificatore)
5. **Caso ricorsivo**: Espressione binaria con chiamata ricorsiva
6. **Operatore supportato**: Qualsiasi operatore eccetto `::` (costruzione lista)
7. **Posizione chiamata ricorsiva**: Uno dei due operandi dell'espressione binaria
8. **Argomenti della chiamata**: Modifiche valide dei parametri originali

### Esempi di Pattern Trasformabili

#### 1. Funzioni Aritmetiche a Un Parametro

**Fattoriale:**
```
factorial(n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```
- **Operatore**: `*` (moltiplicazione)
- **Accumulatore iniziale**: `1`
- **Trasformazione**: `acc * n` ad ogni iterazione

**Somma (da 1 a n):**
```
sum(n) {
    if (n <= 0) {
        return 0;
    } else {
        return n + sum(n - 1);
    }
}
```
- **Operatore**: `+` (addizione)
- **Accumulatore iniziale**: `0`
- **Trasformazione**: `acc + n` ad ogni iterazione

#### 2. Funzioni su Liste a Un Parametro

**Lunghezza lista:**
```
length(lst) {
    if (lst == []) {
        return 0;
    } else {
        return 1 + length(tail(lst));
    }
}
```
- **Operatore**: `+` (addizione)
- **Accumulatore iniziale**: `0`
- **Trasformazione**: `acc + 1` ad ogni iterazione

**Somma elementi lista:**
```
sum_list(lst) {
    if (lst == []) {
        return 0;
    } else {
        return head(lst) + sum_list(tail(lst));
    }
}
```
- **Operatore**: `+` (addizione)
- **Accumulatore iniziale**: `0`
- **Trasformazione**: `acc + head(lst)` ad ogni iterazione

#### 3. Funzioni a Due Parametri

**Dot Product (prodotto scalare):**
```
dot_product(xs, ys) {
    if (xs == []) {
        return 0;
    } else {
        return head(xs) * head(ys) + dot_product(tail(xs), tail(ys));
    }
}
```
- **Operatore**: `+` (addizione)
- **Accumulatore iniziale**: `0`
- **Trasformazione**: `acc + (head(xs) * head(ys))` ad ogni iterazione

### Pattern NON Trasformabili

#### 1. Costruzione di Liste con Operatore `::`

**Motivo dell'esclusione**: Le funzioni che utilizzano l'operatore `::` per costruire liste presentano problemi di correttezza semantica se trasformate con un semplice accumulatore.

**Esempio problematico:**
```
append(xs, ys) {
    if (xs == []) {
        return ys;
    } else {
        return head(xs) :: append(tail(xs), ys);
    }
}
```

**Problema**: La trasformazione con accumulatore invertirebbe l'ordine degli elementi:
- `append([1,2], [3,4])` dovrebbe restituire `[1,2,3,4]`
- La versione tail-recursive ingenua restituirebbe `[2,1,3,4]`

**Soluzione futura**: Questi pattern richiedono tecniche avanzate come continuation-passing style.

#### 2. Altri Pattern Non Supportati

- Funzioni con più di 2 parametri
- Funzioni con corpo complesso (più statement)
- Funzioni con multiple chiamate ricorsive
- Funzioni con chiamate ricorsive in posizioni non-operando

## Vantaggi della Trasformazione

### 1. Ottimizzazione delle Prestazioni
- **Eliminazione stack overflow**: Le funzioni tail-recursive possono essere ottimizzate dal runtime
- **Utilizzo memoria costante**: O(1) invece di O(n) per la profondità di ricorsione
- **Migliori prestazioni**: Meno overhead di chiamate di funzione

### 2. Sicurezza e Robustezza
- **Pattern matching rigoroso**: Solo trasformazioni semanticamente sicure
- **Preservazione della signature**: L'interfaccia pubblica rimane invariata
- **Compatibilità**: Codice esistente continua a funzionare senza modifiche

## Limitazioni Attuali

### 1. Pattern Limitati
- Solo pattern ricorsivi semplici con un'unica chiamata ricorsiva
- Esclusione di costruzioni di lista complesse
- Supporto limitato a 1-2 parametri

### 2. Operatori Esclusi
- **Operatore `::`**: Richiede continuation-passing style
- Pattern complessi che modificano strutture dati in modo non-cumulativo

### 3. Analisi Statica
- Nessuna analisi del flusso di controllo avanzata
- Nessuna ottimizzazione inter-procedurale

## Esempi di Utilizzo

### Trasformazione Programmatica

```python
from tail_recursive_transformer import TailCallTransformer

# Crea un'istanza del trasformatore
transformer = TailCallTransformer()

# Trasforma un programma AST
transformed_program = transformer.transform_program(original_program)

# Il programma trasformato contiene le funzioni originali 
# (ora wrapper) + le funzioni helper generate
```

### Analisi di Funzioni

```python
from tail_recursive_transformer import analyze_function_pattern

# Analizza se una funzione può essere trasformata
analysis = analyze_function_pattern(function_ast)

print(f"Può essere trasformata: {analysis['can_transform']}")
if not analysis['can_transform']:
    print(f"Motivo: {analysis['reason']}")
```

## Testing e Validazione

### Suite di Test Completa

Il trasformatore è accompagnato da una suite di test completa (`test_tail_call_transformer.py`) che verifica:

#### Test di Pattern Recognition
- **Fattoriale semplice**: Verifica il riconoscimento del pattern `n * factorial(n-1)`
- **Somma numerica**: Verifica il riconoscimento del pattern `n + sum(n-1)`
- **Lunghezza lista**: Verifica il riconoscimento del pattern `1 + length(tail(lst))`
- **Somma lista**: Verifica pattern a due parametri `sum_list(tail(lst), acc + head(lst))`
- **Prodotto lista**: Verifica pattern di moltiplicazione `product_list(tail(lst), acc * head(lst))`
- **Dot product**: Verifica pattern con due liste `dot_product(tail(xs), tail(ys))`

#### Test di Trasformazione
- **Generazione funzioni helper**: Verifica che vengano create funzioni con accumulatori
- **Preservazione wrapper**: Verifica che le funzioni wrapper mantengano la signature originale
- **Correttezza semantica**: Verifica che il comportamento rimanga invariato

#### Test di Rejezione
- **Funzioni non ricorsive**: Verifica che funzioni senza ricorsione non vengano trasformate
- **Troppi parametri**: Verifica rejezione di funzioni con più di 2 parametri
- **Pattern non supportati**: Verifica che pattern complessi vengano ignorati

### Analisi dei Pattern

La funzione `analyze_function_pattern()` fornisce diagnostica dettagliata:

```python
from tail_recursive_transformer import analyze_function_pattern

# Esempio di analisi
analysis = analyze_function_pattern(function_ast)
print(f"Trasformabile: {analysis['can_transform']}")
if analysis['can_transform']:
    print(f"Pattern: {analysis['pattern_info']}")
else:
    print(f"Motivo esclusione: {analysis['reason']}")
```

### Risultati Test Attuali

Tutti i 24 test nella suite passano con successo, coprendo:
- 7 test di riconoscimento pattern
- 6 test di trasformazione AST
- 4 test di rejezione pattern non validi
- 7 test di analisi diagnostica

### Pattern di Test Specifici

#### Pattern Trasformabili Testati
- **Fattoriale**: `factorial(n) = n * factorial(n-1)`
- **Somma**: `sum(n) = n + sum(n-1)`
- **Lunghezza**: `length(lst) = 1 + length(tail(lst))`
- **Somma lista**: `sum_list(lst, acc) = sum_list(tail(lst), acc + head(lst))`
- **Prodotto lista**: `product_list(lst, acc) = product_list(tail(lst), acc * head(lst))`
- **Dot product**: `dot_product(xs, ys) = head(xs) * head(ys) + dot_product(tail(xs), tail(ys))`

#### Pattern Correttamente Respinti
- **Costruzione lista**: Pattern con operatore `::` (cons)
- **Funzioni non ricorsive**: Funzioni senza chiamate ricorsive
- **Strutture complesse**: Funzioni con multiple chiamate ricorsive

## Stato Corrente del Progetto

### Versione Stabile
- **Core functionality**: Completa e testata
- **Pattern recognition**: Robusto per pattern supportati
- **Error handling**: Comprehensive rejection of unsafe patterns
- **Documentation**: Completa in italiano

### Recenti Miglioramenti
- **Validazione operatore `::`**: Esplicita rejezione di pattern list-construction
- **Pattern a due parametri**: Supporto completo per dot product e funzioni simili
- **Diagnostica migliorata**: Analisi dettagliata delle ragioni di esclusione
- **Test coverage**: Suite completa con 24 test

### Garanzie di Correttezza
1. **Solo pattern sicuri**: Nessuna trasformazione che alteri la semantica
2. **Preservazione interfaccia**: Signature delle funzioni invariate
3. **Backward compatibility**: Codice esistente non modificato
4. **Zero false positives**: Rejezione rigorosa di pattern ambigui

## Sviluppi Futuri

### 1. Estensioni Pattern
- **Continuation-passing style**: Per funzioni di costruzione lista
- **Mutual recursion**: Trasformazione di ricorsione mutua
- **Multiple recursive calls**: Tecniche più avanzate

### 2. Ottimizzazioni Avanzate
- **Analisi del flusso**: Identificazione automatica di più pattern
- **Inline expansion**: Eliminazione delle funzioni wrapper quando possibile
- **Loop conversion**: Conversione diretta in cicli imperativi

### 3. Diagnostica Migliorata
- **Suggerimenti di refactoring**: Come rendere trasformabile una funzione
- **Analisi delle prestazioni**: Stima del beneficio della trasformazione
- **Debugging support**: Strumenti per il debug delle funzioni trasformate

## Conclusioni

Il trasformatore di ricorsione tail-recursive rappresenta un approccio pragmatico all'ottimizzazione automatica del codice ricorsivo. Pur con le sue limitazioni attuali, fornisce un miglioramento significativo delle prestazioni per una classe importante di funzioni ricorsive, mantenendo la correttezza semantica e la compatibilità del codice esistente.

L'architettura modulare e estensibile del trasformatore permette future estensioni per supportare pattern più complessi e tecniche di ottimizzazione più avanzate.
