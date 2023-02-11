<?php
/**
 * @file parse.php
 * @brief IPPcode21 analyser
 * @author Marián Tarageľ
 * @date 11.2.2023
 */

ini_set('display_errors', 'stderr');

parse_args($argc, $argv);
parse_header();

$xmlheader = '<?xml version="1.0" encoding="utf-8"?><program></program>';
$program = new SimpleXMLElement($xmlheader);
$program->addAttribute('language', 'IPPcode23');

while ($line = fgets(STDIN)) {
    $token_array = scan($line);
    if (count($token_array) < 1) {
        continue;
    }
    switch ($token_array[0]) {
        case "MOVE":
        case "NOT":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            if (count($token_array) != 3) {
                error(23);
            }
            if (!parse_var($token_array[1]) || !parse_symb($token_array[2])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
        
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            if (count($token_array) != 1) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
    
        case "DEFVAR":
        case "POPS":
            if (count($token_array) != 2) {
                error(23);
            }
            if (!parse_var($token_array[1])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;

        case "CALL":
        case "LABEL":
        case "JUMP":
            if (count($token_array) != 2) {
                error(23);
            }
            if (!parse_label($token_array[1])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
        
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            if (count($token_array) != 2) {
                error(23);
            }
            if (!parse_symb($token_array[1])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
        
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            if (count($token_array) != 4) {
                error(23);
            }
            if (!parse_var($token_array[1]) || !parse_symb($token_array[2]) || !parse_symb($token_array[3])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
        
        case "READ":
            if (count($token_array) != 3) {
                error(23);
            }
            if (!parse_var($token_array[1])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
        
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            if (count($token_array) != 4) {
                error(23);
            }
            if (!parse_label($token_array[1]) || !parse_symb($token_array[2]) || !parse_symb($token_array[3])) {
                error(23);
            }
            generate_xml($program, $token_array);
            break;
        
        default:
            error(22);
            break;
    }
}

$dom = dom_import_simplexml($program)->ownerDocument;
$dom->formatOutput = true;
echo $dom->saveXML($dom, LIBXML_NOEMPTYTAG);

exit(0);

function add_arg($instruction, $type, $num)
{
    $arg = $instruction->addChild('arg' . $num);
    $arg->addAttribute('type', $type);
}

function add_args($instruction, $args)
{
    for ($i = 1; $i < count($args); $i++) {
        $type_and_value = explode("@", $args[$i]);
        add_arg($instruction, $type_and_value[0], $i);
    }
}

function generate_xml($program, $token_array)
{
    static $order = 1;
    $instruction = $program->addChild('instruction');
    $instruction->addAttribute('order', $order);
    $instruction->addAttribute('opcode', $token_array[0]);
    $order++;
    add_args($instruction, $token_array);
}

function parse_var($var)
{
    return preg_match('/^(GF|LF|TF)@([a-zA-Z]|(_|-|$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|$|&|%|\*|!|\?))*$/', $var);
}

function parse_symb($symb)
{
    if (parse_var($symb)) {
        return 1;
    }
    elseif (preg_match('/^bool@(true|false)$/', $symb)) {
        return 1;
    }
    elseif (preg_match('/^nil@nil$/', $symb)) {
        return 1;
    }
    elseif (preg_match('/^int@(-?)\d*$/', $symb)) {
        return 1;
    }
    elseif (preg_match('/^string@([^\\#\s]*(\\\d\d\d)?)*$/', $symb)) {
        return 1;
    }
    else {
        return 0;
    }
}

function parse_label($label)
{
    return preg_match('/^([a-zA-Z]|(_|-|$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|$|&|%|\*|!|\?))*$/', $label);
}

function error($error_code)
{
    echo "Error: " . $error_code . "\n";
    exit($error_code); 
}

function scan($line)
{
    $instruction = preg_replace('/#.*/', "", $line);
    $instruction = trim($instruction);
    if (strlen($instruction) == 0) {
        return array();
    }
    $instruction = explode(" ", $instruction);
    $instruction[0] = strtoupper($instruction[0]);
    return $instruction;
}

function parse_header()
{
    while ($header = fgets(STDIN)) {
        $header = preg_replace('/\s*/', "", $header);
        $header = preg_replace('/#.*/', "", $header);
        if (strlen($header) > 0) {
            if ($header == ".IPPcode23") {
                return;
            }
            else {
                error(21);
            }
        }
    }
    error(21);
}

function help()
{
    printf("Použitie: php8.1 parse.php [--help]
Skript typu filter načíta zo štandardného vstupu zdrojový kód v IPPcode23,
skontroluje lexikálnu a syntaktickú správnosť kódu a vypíše na štandardný
výstup XML reprezentáciu programu.
        
-help, --help\tzobrazí pomocníka a skončí\n");
    exit(0);
}

function parse_args($argc, $argv)
{
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
}
?>