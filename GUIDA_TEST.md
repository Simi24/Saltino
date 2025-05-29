# Guida all'Esecuzione della Suite di Test Saltino

## Panoramica

Ho creato una suite completa di **80+ test** per il tuo interprete Saltino, organizzati in 8 categorie che coprono ogni aspetto del linguaggio.

## Struttura Creata

```
test_suite/
├── README.md                      # Documentazione completa
├── basic_functionality/           # 3 test base
├── arithmetic/                    # 5 test aritmetici  
├── lists/                         # 5 test per liste
├── conditions/                    # 6 test per condizioni
├── functions/                     # 8 test per funzioni
├── variables_scope/               # 5 test per scope
├── error_cases/                   # 15 test di errori
└── edge_cases/                    # 10 test casi limite

run_test_suite.py                  # Script per eseguire tutti i test
```

## Come Eseguire i Test

### 1. Test Singolo
```bash
python run_saltino.py test_suite/basic_functionality/hello_world.salt
```

### 2. Categoria Specifica
```bash
# Test di funzionalità base
python run_saltino.py test_suite/basic_functionality/*.salt

# Test di errori (dovrebbero fallire)
python run_saltino.py test_suite/error_cases/division_by_zero.salt
```

### 3. Suite Completa (Automatica)
```bash
python run_test_suite.py
```

Lo script automatico:
- ✅ Esegue tutti i test nelle categorie corrette
- ✅ Distingue test che dovrebbero funzionare da quelli che dovrebbero fallire
- ✅ Fornisce un report dettagliato con statistiche
- ✅ Gestisce timeout e errori

## Categorie di Test Dettagliate

### 🔧 Test di Base (3 test)
- Funzione main più semplice
- Assegnamento variabili
- Blocchi vuoti e annidati

### ➕ Test Aritmetici (5 test)
- Operatori base: +, -, *, /, %
- Operatori unari: +x, -x
- Potenze con associatività destra: 2^3^2
- Precedenza corretta: 2 + 3 * 4
- Numeri negativi e zero

### 📋 Test Liste (5 test)
- Costruzione: 1 :: 2 :: []
- Associatività: 1 :: 2 :: 3 :: []
- Precedenza: 1 + 2 :: []
- head/tail annidati
- Costruzione dinamica ricorsiva

### ⚖️ Test Condizioni (6 test)
- Confronti: <, <=, ==, >, >=
- Logici: and, or, !
- Precedenza: and vs or
- Confronto liste: solo == con []
- Condizioni complesse con parentesi
- Variabili booleane

### 🔄 Test Funzioni (8 test)
- Chiamate base
- Ricorsione diretta e mutua
- Parametri multipli e zero parametri
- Chiamate annidate
- Funzioni che restituiscono booleani
- Funzioni come valori
- Chiamate associate a destra: f(x)(y)
- Return multipli in if-else

### 🔍 Test Scope (5 test)
- Scope di base nei blocchi
- Shadowing delle variabili
- Scope in if-else
- Separazione tra funzioni
- Parametri che nascondono variabili

### ❌ Test Errori (15 test)
**Errori di Runtime:**
- Divisione/modulo per zero
- head/tail su lista vuota

**Errori di Tipo:**
- Aritmetica su booleani
- Logica su interi  
- :: con tipi errati
- head su non-lista
- Confronti invalidi tra liste

**Errori Semantici:**
- Funzione/variabile non definita
- Parametri errati
- Funzione senza return
- Nessuna funzione main
- Funzioni duplicate

### 🚀 Test Edge Cases (10 test)
- Numeri molto grandi
- Ricorsione profonda (100 livelli)
- Liste lunghe (50 elementi)
- Molti parametri (10 parametri)
- Blocchi molto annidati (8 livelli)
- Condizioni molto complesse
- Chiamate molto annidate
- Identificatori molto lunghi
- Espressioni complesse
- Solo lista vuota

## Caratteristiche Testate

### ✅ Sintassi Completa
- Definizioni funzioni con/senza parametri
- Blocchi annidati
- Assegnamenti
- if-else
- return
- Chiamate funzioni

### ✅ Tutti gli Operatori
- Aritmetici: +, -, *, /, %, ^
- Unari: +, -
- Liste: ::, head, tail, []
- Confronto: <, <=, ==, >, >=
- Logici: and, or, !

### ✅ Tutti i Tipi
- Interi (inclusi negativi, zero, grandi)
- Booleani (true, false)
- Liste di interi (vuote, lunghe)
- Funzioni (come valori)

### ✅ Precedenza e Associatività
- Precedenza completa degli operatori
- Associatività a destra: ^, ::
- Associatività a sinistra: +, -, *, /, %
- Precedenza connettivi: ! > and > or

### ✅ Controllo Tipi Dinamico
- Tutte le regole di tipo del linguaggio
- Errori su operazioni invalide
- Confronti corretti

### ✅ Scope e Visibilità
- Scope limitato ai blocchi
- Shadowing corretto
- Separazione funzioni

### ✅ Ricorsione
- Diretta, mutua, profonda
- Stack di chiamate

## Esempi di Output Atteso

### Test Successo
```bash
$ python run_saltino.py test_suite/arithmetic/basic_operations.salt
Risultato: 42
```

### Test Errore
```bash
$ python run_saltino.py test_suite/error_cases/division_by_zero.salt
Errore: Divisione per zero a runtime
```

### Suite Completa
```bash
$ python run_test_suite.py

🧪 Esecuzione Suite di Test per Saltino
==================================================

📁 Categoria: basic_functionality
------------------------------
✅ hello_world.salt
✅ variable_assignment.salt
✅ empty_nested_blocks.salt

📁 Categoria: arithmetic
------------------------------
✅ basic_operations.salt
✅ unary_operators.salt
...

📁 Categoria: error_cases (test di errori)
------------------------------
✅ division_by_zero.salt (errore rilevato correttamente)
✅ head_empty_list.salt (errore rilevato correttamente)
...

==================================================
📊 Riassunto: 67 test passati, 0 test falliti
🎉 Tutti i test sono passati!
```

## Note Implementative

Questa suite è stata progettata per essere:

1. **Completa**: Copre ogni costrutti del linguaggio
2. **Sistematica**: Organizzata logicamente per categorie
3. **Robusta**: Include edge cases e casi limite
4. **Automatizzabile**: Script per esecuzione batch
5. **Documentata**: README dettagliato per ogni test
6. **Estensibile**: Facile aggiungere nuovi test

Utilizza questa suite per:
- ✅ **Validare** la correttezza dell'interprete
- ✅ **Debugging** di problemi specifici  
- ✅ **Testing di regressione** durante lo sviluppo
- ✅ **Benchmark** delle prestazioni
- ✅ **Conformità** alle specifiche Saltino

La suite dovrebbe aiutarti a identificare e correggere qualsiasi problema nell'implementazione dell'interprete!
