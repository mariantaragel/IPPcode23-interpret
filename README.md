# IPPcode23 interpreter
Projekt tvorí sada skriptov pro interpretáciu neštrukturovaného imperatívneho jazyka IPPcode23.

## Analyzátor kódu v IPPcode23 (`parse.php`)
Skript typu filter načíta zo štandardného vstupu zdrojový kód v IPPcode23, skontroluje lexikálnu a syntaktickú správnosť kódu a vypíše na štandardný výstup XML reprezentáciu programu.
### Syntax spustenia
`php8.1 parse.php [--help]`<br>
        
**-h, --help** - zobrazí pomocníka a skončí

## Interpret XML reprezentácie kódu (`interpret.py`)
