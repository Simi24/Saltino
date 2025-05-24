grammar Saltino;

/*
 * Grammatica ANTLR per il linguaggio funzionale Saltino
 * 
 * Caratteristiche implementate:
 * - Tipizzazione dinamica forte
 * - Supporto per interi, booleani, liste di interi e funzioni
 * - Ricorsione e ricorsione di coda
 * - Strutture di controllo: sequenza e selezione (if-then-else)
 */

// ========== REGOLE SINTATTICHE ==========

/**
 * Programma: sequenza non vuota di definizioni di funzioni
 * Deve esistere una funzione 'main' (può avere parametri)
 */
programma: funzione+ EOF;

/**
 * Definizione di funzione con nome, parametri opzionali e corpo
 * Le funzioni devono avere nomi distinti
 */
funzione: 'def' ID '(' parametri? ')' blocco;

// Lista di parametri formali separati da virgole
parametri: ID (',' ID)*;

/**
 * Blocco: sequenza di istruzioni e/o blocchi annidati racchiusa tra graffe
 */
blocco: '{' (istruzione | blocco)* '}';

/**
 * Istruzioni del linguaggio:
 * - Assegnamento di variabile
 * - Condizione if-then-else
 * - Return di valore
 */
istruzione: assegnamento
          | if_stmt
          | return_stmt
          ;

// Assegnamento: variabile = espressione/condizione
assegnamento: ID '=' (espressione | condizione);

// Condizione if-else con condizione tra parentesi
if_stmt: 'if' '(' condizione ')' blocco ('else' blocco)?;

// Return di espressione o condizione
return_stmt: 'return' (espressione | condizione);

/**
 * ESPRESSIONI - Gerarchia di precedenza (dal più alto al più basso):
 * 
 * 1. Chiamate di funzione - associative a destra
 * 2. head/tail - operatori unari su liste  
 * 3. ^ (potenza) - associativo a destra
 * 4. +/- unari - precedenza sui binari
 * 5. mult/% - associativi a sinistra
 * 6. +/- binari - associativi a sinistra  
 * 7. :: (cons) - associativo a destra per costruire liste
 * 8. Elementi primari (letterali, ID, parentesi)
 */
espressione: espressione '(' argomenti? ')'                    # chiamataFunzione  // Associativa a destra
           | ('head' | 'tail') '(' espressione ')'            # headTail          // Operatori unari liste
           | <assoc=right> espressione '^' espressione         # potenza           // Associativo a destra
           | ('+' | '-') espressione                           # unario            // Precedenza su binari
           | espressione ('*' | '/' | '%') espressione         # moltiplicazione   // Associativo a sinistra
           | espressione ('+' | '-') espressione               # addizione         // Associativo a sinistra
           | <assoc=right> espressione '::' espressione        # cons              // Associativo a destra
           | '[]'                                              # listaVuota        // Letterale lista vuota
           | INT                                               # intero            // Litterale intero
           | ID                                                # identificatore    // Riferimento a variabile
           | '(' espressione ')'                               # parantesi         // Precedenza massima
           ;

// Lista di argomenti per chiamate di funzione
argomenti: (espressione | condizione) (',' (espressione | condizione))*;

/**
 * CONDIZIONI - Gerarchia di precedenza (dal più alto al più basso):
 * 
 * 1. ! (negazione) - precedenza su and/or
 * 2. Operatori di confronto - non associativi
 * 3. and - associativo a sinistra, precedenza su or
 * 4. or - associativo a sinistra, precedenza più bassa
 * 
 * Note sui tipi per i confronti:
 * - Operatori <, <=, >, >= : solo interi
 * - Operatore == : interi o (lista vs [])
 */
condizione: condizione ('and' | 'or') condizione              # logico           // and ha prec. su or
          | '!' condizione                                     # negazione        // Precedenza su and/or
          | espressione ('<=' | '<' | '==' | '>' | '>=') espressione  # confronto  // Non associativi
          | ('true' | 'false')                                 # booleano         // Letterali booleani
          | '(' condizione ')'                                 # parentesiCondizione // Precedenza massima
          ;

// ========== TOKEN LESSICALI ==========

/**
 * Identificatori: iniziano con lettera o underscore,
 * seguiti da lettere, cifre o underscore
 */
ID: [_a-zA-Z][_a-zA-Z0-9]*;

/**
 * Numeri interi: sequenza di una o più cifre decimali
 */
INT: [0-9]+;

// ========== GESTIONE WHITESPACE E COMMENTI ==========

// Spazi bianchi ignorati
WS: [ \t\r\n]+ -> skip;

// Commenti su singola riga
COMMENT: '//' ~[\r\n]* -> skip;

// Commenti su più righe  
BLOCK_COMMENT: '/*' .*? '*/' -> skip;