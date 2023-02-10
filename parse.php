<?php
ini_set('display_errors', 'stderr');

if ($argc > 2) {
    error(10);
}

if ($argc == 2) {
    if ($argv[1] == "-help" || $argv[1] == "--help") {
        help();        
    }
    else {
        error(10);
    }
}

parse_header();

while ($line = fgets(STDIN)) {
    $line = substr($line, 0, -1);
    $token_array = scan($line);
    if (count($token_array) < 1) {
        continue;
    }

    switch (strtoupper($token_array[0])) {
        case "MOVE":
            if (count($token_array) != 3) {
                error(23);
            }
            if (!parse_var($token_array[1]) && !parse_symb($token_array[2])) {
                error(23);
            }
            break;
        case "CREATEFRAME":
            if (count($token_array) != 1) {
                error(23);
            }
            break;
        case "PUSHFRAME":
            if (count($token_array) != 1) {
                error(23);
            }
            break;
        case "POPFRAME":
            break;
        case "DEFVAR":
            break;
        case "CALL":
            break;
        case "RETURN":
            break;
        case "PUSHS":
            break;
        case "POPS":
            break;
        case "ADD":
            break;
        case "SUB":
            break;
        case "MUL":
            break;
        case "LT":
            break;
        case "GT":
            break;
        case "EQ":
            break;
        case "AND":
            break;
        case "OR":
            break;
        case "NOT":
            break;
        case "INT2CHAR":
            break;
        case "STRI2INT":
            break;
        case "READ":
            break;
        case "WRITE":
            break;
        case "CONCAT":
            break;
        case "STRLEN":
            break;
        case "GETCHAR":
            break;
        case "SETCHAR":
            break;
        case "TYPE":
            break;
        case "LABEL":
            break;
        case "JUMP":
            break;
        case "JUMPIFEQ":
            break;
        case "JUMPIFNEQ":
            break;
        case "EXIT":
            break;
        case "DPRINT":
            break;
        case "BREAK":
            break;
        default:
            error(22);
            break;
    }
}

exit(0);

function parse_var($var) {
    return preg_match('/(GF|LF|TF)@([a-zA-Z]|(_|-|$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|$|&|%|\*|!|\?))*/', $var);
}

function parse_symb($symb) {
    return 1;
}

function parse_label($label) {
    return preg_match('/([a-zA-Z]|(_|-|$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|$|&|%|\*|!|\?))*/', $label);
}

function error($error_code) {
    echo "Error: " . $error_code . "\n";
    exit($error_code); 
}

function scan($line) {
    $instruction = explode(" ", $line);
    $token_array = [];
    foreach ($instruction as &$token) {
        if ($token[0] == '#') {
            break;
        }
        $token_array[] = $token;
    }
    return $token_array;
}

function parse_header() {
    $header = fgets(STDIN);
    $header = substr($header, 0, -1);
    if ($header != ".IPPcode23") {
        var_dump($header);
        error(21);
    }
}

function help() {
    printf(
        "Použitie: php8.1 parse.php [--help]
Skript typu filter načíta zo štandardného vstupu zdrojový kód v IPPcode23,
skontroluje lexikálnu a syntaktickú správnosť kódu a vypíše na štandardný
výstup XML reprezentáciu programu.
        
-help, --help\tzobrazí pomocníka a skončí\n");
    exit(0);
}
?>