# IPPcode23 interpreter
Projekt tvorí sada skriptov pro interpretáciu neštrukturovaného imperatívneho jazyka IPPcode23.

## Analyzátor kódu v IPPcode23 (`parse.php`)
Skript typu filter načíta zo štandardného vstupu zdrojový kód v IPPcode23, skontroluje lexikálnu a syntaktickú správnosť kódu a vypíše na štandardný výstup XML reprezentáciu programu.
### Syntax spustenia
`php8.1 parse.php [--help]`<br>
        
**-h, --help** - zobrazí pomocníka a skončí

## Interpret XML reprezentácie kódu (`interpret.py`)
Skript načíta XML reprezentáciu programu a tento program s využitím vstupu podľa parametrov príkazového riadku interpretuje a generuje výstup.
### Syntax spustenia
`python3.10 interpret.py [--source FILE] [--input FILE] [-h]`<br>
        
**--source FILE** - vstupný súbor s XML reprezentaciou zdrojového kódu<br/>
**--input FILE** - soubor se vstupmi pre samotnú interpretáciu zadaného zdrojového kódu<br/>
**-h, --help** - zobrazí pomocníka a skončí
