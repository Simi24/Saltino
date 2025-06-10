# LET25 Petta Paolo Simone

## Scelte progettuali

Come da email del 30 maggio:

* utilizzo del linguaggio Python;
* uso diretto di ANTLR per la generazione del parser;
* parser di tipo iterativo;
* ottimizzazione della ricorsione di coda tramite manipolazione esplicita dello stack nell’interprete, evitando quindi la crescita non necessaria dello stack di chiamate;
* gestione approfondita degli errori, con segnalazione precisa e contestuale di ogni condizione anomala;
* implementazione di un modulo che riconosce alcuni pattern ricorsivi trasformabili in chiamate in coda (tail-recursive), e li riscrive automaticamente in una forma ottimizzata, riducendo così l'overhead e prevenendo stack overflow nei casi ricorsivi profondi.

Iscritto all'appello del 23/06/2025.

## Architettura del Sistema

Il sistema è organizzato in componenti modulari con responsabilità specifiche:

### Componenti Principali

**1. Parser e Grammatica (`saltino_parser.py`, `Grammatica/`)**
- Utilizza ANTLR4 per generare lexer, parser e visitor dalla grammatica `Saltino.g4`
- Gestisce il parsing del codice sorgente con error listener personalizzati
- Costruisce l'AST attraverso il pattern Visitor implementato in `ASTVisitor.py`

**2. Abstract Syntax Tree (`AST/`)**
- `ASTNodes.py`: definisce la gerarchia dei nodi AST con pattern Visitor
- `ASTsymbol_table.py`: implementa la symbol table con nomi univoci per gestire gli scope
- `semantic_analyzer.py`: esegue l'analisi semantica decorando l'AST con informazioni sui tipi e scope e possibile chiamata tail-recursive

**3. Trasformatore Tail-Call (`tail_recursive_transformer.py`)**
- Analizza l'AST per identificare pattern ricorsivi non tail-recursive
- Trasforma automaticamente funzioni ricorsive in forme tail-recursive con accumulatori
- Genera funzioni helper per mantenere la compatibilità dell'interfaccia originale

**4. Interprete Iterativo (`interpreter.py`)**
- Classe principale `IterativeSaltinoInterpreter` che elimina la ricorsione attraverso uno stack esplicito
- Utilizza frame di esecuzione (`ExecutionFrame`) per gestire lo stato di ogni operazione
- Implementa dispatch table per gestori specializzati per ogni tipo di frame

**5. Sistema di Frame di Esecuzione (`execution_frames.py`, `execution_handlers.py`)**
- `FrameType`: definisce i tipi di frame (FUNCTION_CALL, BLOCK, EXPRESSION, CONDITION, IF_STATEMENT, ASSIGNMENT, RETURN)
- Ogni frame mantiene stato specifico e ambiente di esecuzione associato
- Handler specializzati gestiscono la logica di esecuzione per ogni tipo di frame

**6. Ambiente di Esecuzione (`execution_environment.py`)**
- Gestisce variabili e funzioni utilizzando nomi univoci dalla symbol table
- Supporta scope nidificati con catena di parent environments
- Integrazione con il semantic analyzer per risoluzione dei nomi

## Documentazione del Tail Call Transformer

Il sistema include un sofisticato trasformatore per l'ottimizzazione della ricorsione di coda:

### Documentazione Completa
- **[`tail_recursive_transformer.md`](tail_recursive_transformer.md)**: Documentazione dettagliata in italiano del modulo di trasformazione

### Caratteristiche Principali
- **Pattern Recognition**: Riconosce automaticamente pattern ricorsivi trasformabili
- **Sicurezza**: Rifiuta pattern che potrebbero alterare la semantica (es. costruzione liste con `::`)
- **Preservazione Interfaccia**: Mantiene la signature originale delle funzioni
- **Test Completi**: Suite di 24 test per validare tutti i pattern supportati

### Pattern Supportati
- Fattoriale: `n * factorial(n-1)`
- Somma numerica: `n + sum(n-1)`
- Operazioni su liste: `1 + length(tail(lst))`
- Dot product: `head(xs)*head(ys) + dot_product(tail(xs), tail(ys))`

### Flusso di Esecuzione

**Fase 1: Parsing e Analisi**
1. Il file sorgente viene analizzato dal parser ANTLR generando un parse tree
2. L'`ASTVisitor` trasforma il parse tree in AST
3. Il `TailCallTransformer` ottimizza le funzioni ricorsive identificando pattern specifici
4. Il `SemanticAnalyzer` analizza l'AST, costruisce la symbol table e decora i nodi con informazioni semantiche

**Fase 2: Esecuzione Iterativa**
1. L'interprete registra tutte le funzioni nell'ambiente globale
2. Viene cercata e invocata la funzione `main` con eventuali argomenti da input utente
3. L'esecuzione procede attraverso un loop iterativo che gestisce uno stack di `ExecutionFrame`
4. Ogni frame rappresenta un'operazione in corso (chiamata di funzione, blocco, espressione, etc.)
5. Gli handler specializzati processano ogni frame secondo la sua tipologia
6. I risultati vengono propagati attraverso lo stack fino al completamento

**Gestione dello Stack**
- Ogni operazione viene rappresentata da un frame nello stack di esecuzione
- I frame mantengono stato specifico e puntano all'ambiente di esecuzione corrente
- La gestione iterativa evita l'overflow dello stack di chiamate Python
- Il sistema traccia statistiche di esecuzione (profondità massima, chiamate totali, tail call ottimizzate)

**Ottimizzazione Tail-Call**
- Le chiamate tail-recursive vengono riconosciute durante l'esecuzione
- Invece di creare nuovi frame, viene riutilizzato il frame corrente aggiornando parametri e ambiente
- Questo previene la crescita dello stack per ricorsioni profonde
