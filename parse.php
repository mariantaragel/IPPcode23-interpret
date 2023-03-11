<?php
/**
 * @file parse.php
 * @brief IPPcode23 analyser
 * @author Marián Tarageľ
 * @date 9.3.2023
 */

ini_set('display_errors', 'stderr');

class Parser
{
    protected $data;
    private $header = ".IPPCODE23";
    private $help_message = "usage: parse.php [--help]
A filter script reads the source code in IPPcode23 from standard input, checks
the lexical and syntactic correctness of the code and writes to standard output
XML representation of the program.

-h, --help\tshow this help message and exit\n";

    /** Parser constructor */
    public function __construct()
    {
        $this->data = new DataType();
    }
    
    /**
     * Argument parser
     * @param mixed $argc The number of arguments passed to script
     * @param mixed $argv Array of arguments passed to script
     */
    public function parse_args($argc, $argv)
    {
        if ($argc > 2) {
            $this->error_handler(10);
        }
        
        if ($argc == 2) {
            if ($argv[1] == "-h" || $argv[1] == "--help") {
                $this->help();
            }
            else {
                $this->error_handler(10);
            }
        }
    }

    /** Parse header .IPPcode23 */
    public function parse_header()
    {
        while ($header = fgets(STDIN)) {
            $header = preg_replace('/\s*/', "", $header);
            $header = preg_replace('/#.*/', "", $header);
            if (strlen($header) > 0) {
                if (strtoupper($header) == $this->header) {
                    return;
                }
                else {
                    $this->error_handler(21);
                }
            }
        }
        $this->error_handler(21);
    }

    /**
     * Handling errors
     * @param mixed $error_code Return code of a script
     */
    public function error_handler($error_code)
    {
        fprintf(STDERR, "Error: " . $error_code . "\n");
        exit($error_code);
    }

    /** Print help message */
    private function help()
    {
        echo $this->help_message;
        exit(0);
    }

    /**
     * One line of source code will be transformed to token array
     * @param mixed $line Line of source code
     * @return array Array of tokens
     */
    public function scan($line)
    {
        $instruction = preg_replace('/#.*/', "", $line);
        $instruction = trim($instruction);
        if (strlen($instruction) == 0) {
            return array();
        }
        $instruction = preg_replace('/\s+/', " ", $instruction);
        $instruction = explode(" ", $instruction);
        $instruction[0] = strtoupper($instruction[0]);
        return $instruction;
    }

    /**
     * Check syntax of instructions with no arguments
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode($instruction)
    {
        if (count($instruction) != 1) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with label argument
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_label($instruction)
    {
        if (count($instruction) != 2) {
            $this->error_handler(23);
        }
        if (!$this->data->is_label($instruction[1])) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with symb argument
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_symb($instruction)
    {
        if (count($instruction) != 2) {
            $this->error_handler(23);
        }
        if (!$this->data->is_symb($instruction[1])) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with var argument
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_var($instruction)
    {
        if (count($instruction) != 2) {
            $this->error_handler(23);
        }
        if (!$this->data->is_var($instruction[1])) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with two arguments var and symb
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_var_symb($instruction)
    {
        if (count($instruction) != 3) {
            $this->error_handler(23);
        }
        if (!$this->data->is_var($instruction[1]) || !$this->data->is_symb($instruction[2])) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with two arguments var and type
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_var_type($instruction)
    {
        if (count($instruction) != 3) {
            $this->error_handler(23);
        }
        if (!$this->data->is_var($instruction[1]) || !$this->data->is_type($instruction[2])) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with three arguments label, symb and symb
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_label_symb_symb($instruction)
    {
        if (count($instruction) != 4) {
            $this->error_handler(23);
        }
        if (!$this->data->is_label($instruction[1]) ||
            !$this->data->is_symb($instruction[2]) ||
            !$this->data->is_symb($instruction[3])) {
            $this->error_handler(23);
        }
    }

    /**
     * Check syntax of instruction with three arguments var, symb and symb
     * @param mixed $instruction Array of instruction tokens
     */
    public function check_opcode_var_symb_symb($instruction)
    {
        if (count($instruction) != 4) {
            $this->error_handler(23);
        }
        if (!$this->data->is_var($instruction[1]) ||
            !$this->data->is_symb($instruction[2]) ||
            !$this->data->is_symb($instruction[3])) {
            $this->error_handler(23);
        }
    }
}

class DataType
{
    private $type_regex = '/^(int|string|bool)$/';
    private $var_regex = '/^(GF|LF|TF)@([a-zA-Z]|(_|-|\$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|\$|&|%|\*|!|\?))*$/';
    private $label_regex = '/^([a-zA-Z]|(_|-|\$|&|%|\*|!|\?))([a-zA-Z0-9]|(_|-|\$|&|%|\*|!|\?))*$/';
    private $nil_regex = '/^nil@nil$/';
    private $lit_bool_regex = '/^bool@(true|false)$/';
    private $lit_string_regex = '/^string@([^#\s\\\]*(\\\[0-9][0-9][0-9])*)*$/';
    private $lit_int_decimal_regex = '/^int@(-|\+)?\d+$/';
    private $lit_int_hexadecimal_regex = '/^int@0[xX][\da-fA-F]+$/';
    private $lit_int_octal_regex = '/^int@0[oO][0-7]+$/';

    /**
     * Match type
     * @param mixed $type The input token
     * @return int 1 if the token type is type, otherwise 0
     */
    public function is_type($type) {
        return preg_match($this->type_regex, $type);
    }

    /**
     * Match var
     * @param mixed $var The input token
     * @return int 1 if the token type is var, otherwise 0
     */
    public function is_var($var) {
        return preg_match($this->var_regex, $var);
    }

    /**
     * Match label
     * @param mixed $label The input token
     * @return int 1 if the token type is label, otherwise 0
     */
    public function is_label($label) {
        return preg_match($this->label_regex, $label);
    }

    /**
     * Match symb
     * @param mixed $symb The input token
     * @return int 1 if the token type is symb, otherwise 0
     */
    public function is_symb($symb)
    {
        if ($this->is_var($symb) || $this->is_nil($symb)) {
            return 1;
        }
        elseif ($this->is_lit_bool($symb) || $this->is_lit_int($symb) || $this->is_lit_string($symb)) {
            return 1;
        }
        else {
            return 0;
        }
    }

    /**
     * Match nil
     * @param mixed $nil The input token
     * @return int 1 if the token type is nil, otherwise 0
     */
    public function is_nil($nil) {
        return preg_match($this->nil_regex, $nil);
    }

    /**
     * Match lit bool
     * @param mixed $bool The input token
     * @return int 1 if the token type is lit bool, otherwise 0
     */
    public function is_lit_bool($bool) {
        return preg_match($this->lit_bool_regex, $bool);
    }

    // Match lit string
    /**
     * Match lit string
     * @param mixed $string The input token
     * @return int 1 if the token type is lit string, otherwise 0
     */
    public function is_lit_string($string) {
        return preg_match($this->lit_string_regex, $string);
    }

    /**
     * Match lit int (decimal, hexadecimal and octal)
     * @param mixed $int The input token
     * @return int 1 if the token type is lit int, otherwise 0
     */
    public function is_lit_int($int)
    {
        if (preg_match($this->lit_int_decimal_regex, $int)) {
            return 1;
        }
        elseif (preg_match($this->lit_int_hexadecimal_regex, $int)) {
            return 1;
        }
        else {
            return preg_match($this->lit_int_octal_regex, $int);
        }
    }

    /**
     * Return type of token
     * @param mixed $token The input token
     * @return string String representation of token type
     */
    public function get_type($token)
    {
        if ($this->is_var($token)) {
            return "var";
        }
        elseif ($this->is_type($token)) {
            return "type";
        }
        elseif ($this->is_label($token)) {
            return "label";
        }
        else {
            $token_divided = explode("@", $token);
            return $token_divided[0];
        }
    }
}

class XMLGenerator
{
    protected $simpleXML;
    protected $data;
    private $xml_header = '<?xml version="1.0" encoding="utf-8"?><program></program>';

    /** XMLGenerator constructor */
    public function __construct()
    {
        $this->simpleXML = new SimpleXMLElement($this->xml_header);
        $this->data = new DataType();
    }

    /**
     * Generate XML of valid instruction
     * @param mixed $token_array Instruction in array of tokens
     */
    public function generate_xml($token_array)
    {
        static $order = 1;
        $instruction = $this->simpleXML->addChild('instruction');
        $instruction->addAttribute('order', $order);
        $instruction->addAttribute('opcode', $token_array[0]);
        $order++;
        $this->add_args($instruction, $token_array);
    }

    /** Print XML to stdout */
    public function print_xml()
    {
        $dom = dom_import_simplexml($this->simpleXML)->ownerDocument;
        $dom->formatOutput = true;
        echo $dom->saveXML($dom, LIBXML_NOEMPTYTAG);
    }

    /**
     * Add attribute language with value
     * @param mixed $lang Language
     * @param mixed $value Name of a language
     */
    public function add_lang_code($lang, $value) {
        $this->simpleXML->addAttribute($lang, $value);
    }

    /**
     * Add one agrument of instruction to XML
     * @param mixed $instruction XML node of instruction
     * @param mixed $type Type of argument
     * @param mixed $num Agrument order
     * @param mixed $value Value of argument
     */
    private function add_arg($instruction, $type, $num, $value)
    {
        $arg = $instruction->addChild('arg' . $num, $value);
        $arg->addAttribute('type', $type);
    }

    /**
     * Add more arguments of instruction to XML
     * @param mixed $instruction XML node of instruction
     * @param mixed $args Array of instruction
     */
    private function add_args($instruction, $args)
    {
        for ($i = 1; $i < count($args); $i++) {
            $type = $this->data->get_type($args[$i]);
            $args[$i] = str_replace('&', '&amp;', $args[$i]);
            $value = explode("@", $args[$i], 2);
            if ($this->data->is_type($type) || $type == "nil") {
                $this->add_arg($instruction, $type, $i, $value[1]);
            }
            else {
                $this->add_arg($instruction, $type, $i, $args[$i]);
            }
        }
    }
}

$parser = new Parser();
$parser->parse_args($argc, $argv);
$parser->parse_header();

$program = new XMLGenerator();
$program->add_lang_code('language', 'IPPcode23');

// Read source code by lines
while ($line = fgets(STDIN)) {
    $token_array = $parser->scan($line);
    if (count($token_array) < 1) {
        continue;
    }

    // Based on first token check syntax of instructions
    match($token_array[0]) {
        "MOVE", "NOT", "INT2CHAR", "STRLEN", "TYPE" => $parser->check_opcode_var_symb($token_array),
        "CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK" => $parser->check_opcode($token_array),
        "DEFVAR", "POPS" => $parser->check_opcode_var($token_array),
        "CALL", "LABEL", "JUMP" => $parser->check_opcode_label($token_array),
        "PUSHS", "WRITE", "EXIT", "DPRINT" => $parser->check_opcode_symb($token_array),
        "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR" =>
            $parser->check_opcode_var_symb_symb($token_array),
        "READ" => $parser->check_opcode_var_type($token_array),
        "JUMPIFEQ", "JUMPIFNEQ" => $parser->check_opcode_label_symb_symb($token_array),
        default => $parser->error_handler(22)
    };
    
    $program->generate_xml($token_array);
}

$program->print_xml();
exit(0);

?>