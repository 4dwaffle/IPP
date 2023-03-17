<?php

ini_set('display_errors', 'std_err');

if ($argc > 1) {
    if ($argv[1] == "--help") {
        echo ("Usage: parse.php < [IPPCODE23] > [OUTPUT.xml]");
        exit(0);
    }
}

function printInstructionStart($order, $exploded)
{
    $exploded = strtoupper($exploded);
    echo ("\t<instruction order=\"$order\" opcode=\"$exploded\">\n");
}
function printInstructionEnd()
{
    echo ("\t</instruction>\n");
}
function printArg($arg, $type, $argCount)
{
    if ($type == "<var>" || $type == "<symb>") {
        $type = getVarSymbType($arg);
    }

    if ($type == "label") {
        checkLabel($arg);
    } else {
        if (!(str_contains($arg, "@") || $arg == "int" || $arg == "string" || $arg == "bool")) {
            exit(23);
        }
    }

    if (!ctype_lower($type) && !isFrame($type)) {
        exit(23);
    }
    echo ("\t\t<arg$argCount type=\"$type\">");
    if ($arg == "type") {
        echo ($arg);
    }
    if ($type == "int" || $type == "string" || $type == "bool" || $type == "nil") {
        checkString($arg);
        $exploded = explode('@', $arg);

        if ($type == "string") {
            $exploded[1] = convertString($exploded[1]);
        } else if ($type == "bool") {
            checkBool($exploded[1]);
        } else if ($type == "int") {
            checkInt($exploded[1]);
        } else if ($type == "nil") {
            if ($exploded[1] != "nil") {
                exit(23);
            }
        }
        echo ("$exploded[1]");
    } else {
        $exploded = explode('@', $arg);
        if (substr_count($arg, '@') > 1) {
            exit(23);
        }
        if ($type == "var") {
            if (!isFrame($exploded[0])) {
                exit(23);
            }
            if (checkLabel($exploded[1])) {
                exit(23);
            }
            $arg = convertString($arg);
        }
        echo ($arg);
    }
    echo ("</arg$argCount>\n");
}

function isLabel($string)
{
    if(preg_match('(^[a-zA-Z_&$%*!?-][a-zA-Z_0-9&$%*!?-]*$)', $string))
    {
        return 1;
    }
    else
    {
        return 0;
    }
}
function isFrame($string)
{
    if ($string == "GF" || $string == "LF" || $string == "TF") {
        return 1;
    } else {
        return 0;
    }
}

function checkInt($string)
{
    if (!is_numeric($string)) {
        exit(23);
    }
}

function convertString($string)
{
    $string = str_replace("&", "&amp;", $string);
    $string = str_replace("<", "&lt;", $string);
    $string = str_replace(">", "&gt;", $string);
    return $string;
}

function checkString($string)
{
    $slashCount = substr_count($string, "\\");
    if ($slashCount > 0) {
        $matchesCount = preg_match_all('(\\\[0-9])', $string);
        if ($matchesCount != $slashCount) {
            exit(23);
        }
    }

}
function checkLabel($string) //or var after @
{
    if (!preg_match('(^[a-zA-Z_&$%*!?-][a-zA-Z_0-9&$%*!?-]*$)', $string)) {
        exit(23);
    } else {
        return 0;
    }
}
function checkBool($string)
{
    if ($string == "false" || $string == "true") {
        return 1;
    } else {
        exit(23);
    }
}

function getVarSymbType($arg) //int@22 format
{
    $exploded = explode('@', $arg);
    $type = $exploded[0];
    if (isFrame($type)) {
        $type = "var";
    }
    return $type;
}

function varExists($var, $varArr)
{
    if (is_null($varArr)) {
        return true;
    }

    foreach ($varArr as $value) {
        if ($var == $value) {
            return false;
        }
    }
}

$header = false;
$order = 0;
$varArr[] = null;

echo ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
echo ("<program language=\"IPPcode23\">\n");

while ($line = fgets((STDIN))) {
    $line = preg_replace('!\s+!', ' ', $line); //reduces multiple whitespaces

    //skip comments
    if (str_contains($line, '#')) {
        if (preg_match('(^\s*#.*$)', $line)) {
            continue;
        }
        $line = preg_replace('(\#.*)', '', $line);
    }

    $line = trim($line, " \n");
    $exploded = explode(' ', $line);
    if (empty($line)) {
        continue;
    }
    if (strtoupper($exploded[0]) == ".IPPCODE23") {
        if ($order > 0) {
            exit(22);
        }
        if ($header == false) {
            $header = true;
            $order++;
            continue;
        } else {
            echo ("here");
            exit(22);
        }
    }
    if ($header == false) {
        exit(21);
    }
    switch (strtoupper($exploded[0])) {
        //0 arguments    34
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            printInstructionStart($order, $exploded[0]);
            printInstructionEnd();
            if (!(empty($exploded[1]) || $exploded[1] == "#")) {
                exit(23);
            }
            break;
        //1 argument
        case "DEFVAR":
            array_push($varArr, $exploded[0]);
            if (varExists($exploded[1], $varArr)) {
                exit(52);
            }
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "var", 1);
            printInstructionEnd();
            if (!empty($exploded[2])) {
                exit(23);
            }
            break;
        case "CALL":
        case "LABEL":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "label", 1);
            printInstructionEnd();
            if (!empty($exploded[2])) {
                exit(23);
            }
            break;
        case "POPS":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "<var>", 1);
            printInstructionEnd();
            $splitted = explode("@", $exploded[1]);
            if (!isFrame($splitted[0])) {
                exit(23);
            }
            if (!empty($exploded[2])) {
                exit(23);
            }
            break;
        case "EXIT":
        case "PUSHS":
            printInstructionStart($order, $exploded[0]);
            if (!str_contains($exploded[1], "@")) {
                exit(23);
            }
            printArg($exploded[1], "<symb>", 1);
            printInstructionEnd();
            if (!empty($exploded[2])) {
                exit(23);
            }
            break;
        case "DPRINT":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "<symb>", 1);
            printInstructionEnd();
            if (!empty($exploded[2])) {
                exit(23);
            }
            if(!str_contains($exploded[1], "@"))
            {
                exit(23);
            }
            break;
        case "JUMP":
            printInstructionStart($order, $exploded[0]);
            $frame = explode('@', $exploded[1]);
            if (isFrame($frame[0])) {
                $type = "var";
            }
            else {
                $type = "<symb>";
            }
            printArg($exploded[1], "label", 1);
            printInstructionEnd();
            break;
        case "WRITE":
            printInstructionStart($order, $exploded[0]);
            $frame = explode('@', $exploded[1]);
            if (isFrame($frame[0])) {
                $type = "var";
            }
            else {
                $type = "<symb>";
            }
            if(!str_contains($exploded[1], "@"))
            {
                exit(23);
            }
            if (!empty($exploded[2])) {
                exit(23);
            }
            printArg($exploded[1], $type, 1);
            printInstructionEnd();
            break;
        //2 arguments
        case "MOVE":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "var", 1);
            printArg($exploded[2], "<symb>", 2);
            printInstructionEnd();
            if (!empty($exploded[3])) {
                exit(23);
            }
            break;
        case "INT2CHAR":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "var", 1);
            printArg($exploded[2], "<symb>", 2);
            printInstructionEnd();
            if(!(str_contains($exploded[1], "@") && str_contains($exploded[2], "@")))
            {
                exit(23);
            }
            break;
        case "READ":
            printInstructionStart($order, $exploded[0]);
            switch ($exploded[2]) {
                case "int":
                case "string":
                case "bool":
                    printArg($exploded[1], "var", 1);
                    printArg($exploded[2], "type", 2);
                    break;
                default:
                    printArg("nil@nil", "@nil", 1);
                    break;
            }
            if (!empty($exploded[3])) {
                exit(23);
            }
            printInstructionEnd();
            break;
        case "STRLEN":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "int", 1);
            printArg($exploded[2], "type", 2);
            $splitted = explode($exploded[1], "@");
            if(!isFrame($splitted[1]))
            {
                exit(23);
            }
            if (!empty($exploded[3])) {
                exit(23);
            }
            if(!(str_contains($exploded[1], "@") && str_contains($exploded[2], "@")))
            {
                exit(23);
            }
            printInstructionEnd();
            break;
        case "TYPE":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "type", 1);
            printArg($exploded[2], "type", 2);
            printInstructionEnd();
            $splitted = explode($exploded[1], "@");
            if(!isFrame($splitted[1]))
            {
                exit(23);
            }
            if (!empty($exploded[3])) {
                exit(23);
            }
            if(!(str_contains($exploded[1], "@") && str_contains($exploded[2], "@")))
            {
                exit(23);
            }
            break;
        case "NOT":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "var", 1);
            printArg($exploded[2], "<symb>", 2);
            if (!empty($exploded[3])) {
                exit(23);
            }
            if(!(str_contains($exploded[1], "@") && str_contains($exploded[2], "@")))
            {
                exit(23);
            }
            printInstructionEnd();
            break;
        //3 arguments
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "var", 1);
            printArg($exploded[2], "<symb>", 2);
            printArg($exploded[3], "<symb>", 3);
            if (!empty($exploded[4])) {
                exit(23);
            }
            if(!(str_contains($exploded[1], "@") && str_contains($exploded[2], "@") && str_contains($exploded[3], "@")))
            {
                exit(23);
            }
            printInstructionEnd();
            break;
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "var", 1);
            printArg($exploded[2], "<symb>", 2);
            printArg($exploded[3], "<symb>", 3);
            if (!empty($exploded[4])) {
                exit(23);
            }
            printInstructionEnd();
            if(!(str_contains($exploded[1], "@") && str_contains($exploded[2], "@") && str_contains($exploded[3], "@")))
            {
                exit(23);
            }
            break;
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            printInstructionStart($order, $exploded[0]);
            printArg($exploded[1], "label", 1);
            printArg($exploded[2], "<symb>", 2);
            printArg($exploded[3], "<symb>", 3);
            if (!empty($exploded[4])) {
                exit(23);
            }
            printInstructionEnd();
            if(!(str_contains($exploded[2], "@") && str_contains($exploded[3], "@")) || str_contains($exploded[1], "@"))
            {
                exit(23);
            }
            break;
        default:
            exit(22);
    }
    $order++;

}
if ($header == false) {
    exit(21);
}
echo ("</program>")
    ?>