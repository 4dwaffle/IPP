import re
import argparse
import xml.etree.ElementTree as ET
from operator import attrgetter


class instruction:
    def __init__(self, order, opcode):
        self._order = order
        self._opcode = opcode
        self._args = []
    def add_arg(self, arg_type, value):
        self._args.append(argument(arg_type, value))
    def get_order(self):
        return self._order
    def get_opcode(self):
        return self._opcode
    def get_args(self):
        return self._args

class argument:
    def __init__(self, arg_type, value):
        self._type = arg_type
        self._value = value
    def set_type(self, arg_type):
        self._type = arg_type
    def set_value(self, value):
        self._value = value
    def get_type(self):
        return self._type
    def get_value(self):
        return self._value
    
class variable:
    def __init__(self, name, var_type, value):
        self._name = name
        self._type = var_type 
        self._value = value
    def set_type(self, var_type):
        self._type = var_type
    def set_value(self, value):
        self._value = value
    def get_name(self):
        return self._name
    def get_type(self):
        return self._type
    def get_value(self):
        return self._value
    
def sort_children(parent, attr):
    parent[:] = sorted(parent, key=lambda child: int(child.get(attr)))    

def add_args2ins(ins, arg_count, element):
    i = 0
    while i < arg_count:
        ins.add_arg(element[i].attrib['type'], element[i].text)
        i+=1

def print_ins(instructions):
    print("instructions:")
    k = 0
    for j in instructions:
        a = instructions[k].get_args()
        print(instructions[k].get_order(), instructions[k].get_opcode(), end=" ")
        print_args(instructions[k].get_args())
        k = k + 1

def print_args(args):
    i = 0
    for a in args:
        print(args[i].get_type(), args[i].get_value(), end="; ")
        i += 1

def print_all():
    print_ins(instructions)
    print("GF:")
    for g in GF:
        print(g.get_name(), g.get_type(), g.get_value())
    print("end")
#returns number of arguments based on the opcode
def count_arg(opcode):
    match opcode:
        #0 ARGS
        case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK":  return 0
        #1 ARG
        case "DEFVAR" | "CALL" | "PUSH" | "POPS" | "JUMP" | "EXIT" | "DPRINT" | "LABEL" | "WRITE":   return 1
        #2 ARGS
        case "MOVE" |  "INT2CHAR" | "READ" | "STRLEN" |  "TYPE"| "NOT":  return 2
        #3 ARGS
        case "ADD" | "SUB" | "MUL" | "IDIV" | "LT" | "GT" | "EQ" | "AND" | "OR" | "STRI2INT" | "CONCAT" | "GETCHAR" | "SETCHAR" | "JUMPIFEQ" | "JUMPIFNEQ":   return 3
        case _:     exit(32)

def exists_in_frame(var_name, frame) -> bool:
    i = 0
    for f in frame:
        if frame[i].get_name() == var_name:
            return 1
        i += 1
    return 0

def get_index_of_var(var_name, frame) -> int:
    i = 0
    for f in frame:
        if frame[i].get_name() == var_name:
            return i
        i += 1
    exit(4)

def get_var(var) -> variable:
    splitted = var.get_value().split("@")
    frame = splitted[0]
    if len(splitted) > 1:
        var_name = splitted[1]
    if  frame == "GF":
        index = get_index_of_var(var_name, GF)
    return GF[index]

def interpret_DEFVAR(arg):
    splitted = arg.get_value().split("@")
    frame = splitted[0]
    var_name = splitted[1]

    if frame ==  "GF":
        if exists_in_frame(var_name, GF):
            exit(5)
        else:
            GF.append(variable(var_name, "", ""))
    elif frame == "LF":
        if exists_in_frame(var_name, LF):
            exit(6)
        else:
            LF.append(variable(var_name, "", ""))
    else:
        exit(55)

def interpret_MOVE(arg1, arg2):
    splitted1 = arg1.get_value().split("@")
    frame1 = splitted1[0]
    var1_name = splitted1[1]
    var2_type = arg2.get_type()
    var2_value = arg2.get_value()
    if frame1 == "GF":
        index = get_index_of_var(var1_name, GF)
        GF[index].set_type(var2_type)
        GF[index].set_value(var2_value)

def interpret_READ(arg1, arg2):
    if input:
        file_in = open(input, 'r+')
        lines = file_in.readlines()
        global input_current_line
        if input_current_line < len(lines):
            read = lines[input_current_line]
            input_current_line += 1
    else:
        read = input()
    splitted = arg1.get_value().split("@") 
    frame = splitted[0]
    var_name = splitted[1]
    if arg2.get_value() == "int":
        try:
            var_type = "int"
            read = int(read)
        except:
            read = "nil"
            var_type = "nil"
    elif arg2.get_value() == "string":
        var_type = "string"
    elif arg2.get_value() == "bool":
        var_type = "bool"
        if read.upper() == "TRUE":
            read = "true"
        else:
            read = "false"
    else:
        exit(3)

    if frame == "GF":
        index = get_index_of_var(var_name, GF)
        GF[index].set_value(read)
        GF[index].set_type(var_type)
    elif frame == "LF":
        index = get_index_of_var(var_name, GF)
        LF[index].set_value(read)
        LF[index].set_type(var_type)
    else:
        exit(7)

def interpret_POPS(arg):
    if not stack:
        exit(55)
    else:
        arg.set_value(stack.pop)

def interpret_WRITE(arg):
    if arg.get_type() == "var":
        var = get_var(arg)
        arg.set_type(var.get_type())
        arg.set_value(var.get_value())
    if arg.get_value() == "nil":
        if arg.get_type() == "nil":
            print("", end='')
    elif arg.get_type() != "int":
        print(arg.get_value().strip('\n'), end='')
    else:
        print(arg.get_value(), end='')

def interpret_arithmetic(result, operand1, operand2, operation):
    var_name = result.get_value().split("@")[1]
    result_index = get_index_of_var(var_name, GF)
    if operand1.get_type() == "var":
        var_name = operand1.get_value().split("@")[1]
        index = get_index_of_var(var_name, GF)
        operand1.set_value(GF[index].get_value())
        operand1.set_type(GF[index].get_type())
    if operand2.get_type() == "var":
        var = get_var(operand2)
        operand2.set_type(var.get_type())

    if operand1.get_type() == "int" and operand2.get_type() == "int":
        try:
            value1 = int(operand1.get_value())
            value2 = int(operand2.get_value())
        except:
            exit(12)
        match operation:
            case "ADD":     tmp =  value1 + value2
            case "SUB":     tmp =  value1 - value2
            case "MUL":     tmp =  value1 * value2
            case "IDIV":    
                if value2 != 0:
                    tmp =  value1 / value2
                else:
                    exit(57)
        GF[result_index].set_value(tmp)
        GF[result_index].set_type("int")
    else:
        exit(53)

def interpret_relation(result, operand1, operand2, operator):
    splitted = result.split("@")
    frame = splitted[0]
    var_name = splitted[1]

    if frame == "GF":
        if not exists_in_frame(var_name, GF):
            exit(54)

    result.set_type("bool")
    tmp_result = 0 #= false
    if (operand1.get_type() == "int" and operand2.get_type() == "int"):
        match operator:
            case "LT":
                if operand1 < operand2:
                    tmp_result = 1
            case "GT":
                if operand1 > operand2:
                    tmp_result = 1
            case "EQ":
                if operand1 == operand2:
                    tmp_result = 1
    elif (operand1.get_type() == "string" and operand2.get_type() == "string"):
        if operator == "EQ":
            if operand1.get_value() == operand2.get_value():
                tmp_result = 1
    elif (operand1.get_type() == "bool" and operand2.get_type() == "bool"):
        match operator:
            case "EQ":
                if operand1.get_value() == operand2.get_value():
                    tmp_result = 1
            case "LT":
                if operand1.get_value().uppper() == "FALSE" and operand2.get_value().upper() == "TRUE":
                    tmp_result = 1
            case "GT":
                if operand1.get_value().uppper() == "TRUE" and operand2.get_value().upper() == "FALSE":
                    tmp_result = 1
    else:
        exit(7)
    if tmp_result == 1:
        result.set_value("true")
    else:
        result.set_value("false")

def interpret_NOT(result, operand):
    splitted = result.split("@")
    frame = splitted[0]
    var_name = splitted[1]

    if frame == "GF":
        if not exists_in_frame(var_name, GF):
            exit(54)    
    result.set_type("bool")
    if operand.get_type() == "bool":
        if operand.get_value().upper() == "TRUE":
            result.set_value("false")
        elif operand.get_value().upper() == "FALSE":
            result.set_value("true")
        else:
            exit(6)

def interpret_EXIT(arg):
    err = -1
    try:
        err = int(arg.get_value())
    except:
        exit(57)
    if err < 0 or err > 49:
        exit(57)
    else:
        exit(err)

def interpret_logic(result, operand1, operand2, operator):
    splitted = result.split("@")
    frame = splitted[0]
    var_name = splitted[1]

    if frame == "GF":
        if not exists_in_frame(var_name, GF):
            exit(54)

    if operand1.get_type() == "var":
        var = get_var(operand1)
        operand1.set_type(var.get_type())
        operand1.set_value(var.get_value())
    if operand2.get_type() == "var":
        var = get_var(operand2)
        operand2.set_type(var.get_type())
    
    
    if operand1.get_type() != "bool" or operand2.get_type() != "bool":
        exit(7)
    tmp_result = 0 #false
    match operator:
        case "AND":
            if operand1 and operand2:
                tmp_result = 1
        case "OR":
            if operand1 or operand2:
                tmp_result = 1
        case _: 
            exit(8)
    result.set_type("bool")
    if tmp_result == 1:
        result.set_value("true")
    else:
        result.set_value("false")

def interpret_TYPE(arg1, arg2):
    if arg2.get_type() == "var":
        var = get_var(arg2)
        arg2.set_type(var.get_type())
        arg2.set_value(var.get_value())
    splitted = arg1.get_value().split("@")
    frame = splitted[0]
    var_name = splitted[1]

    if frame == "GF":
        if not exists_in_frame(var_name, GF):
            exit(54)
    index = get_index_of_var(var_name, GF)
    value = arg2.get_value()
    ret_type = ""

    if re.match(r"^[-+]?\d+$", value):
        ret_type = "int"
    elif value.upper() == "TRUE" or value.upper() == "FALSE":
        ret_type = "bool"
    elif value == "nil":
        ret_type = "nil"
    elif value:
        ret_type = "string"
    else:
        print("",end='')
    GF[index].set_value(ret_type)

def preload_labels():
    for i in instructions:
        if i.get_opcode().upper() == "LABEL":
            label = i.get_args()[0].get_value()
            if label in labels:
                exit(52)
            else:
                labels.append(label)

def print_labels():
    i = 0
    for l in labels:
        print(labels[i])
        i += 1

def interpret_JUMP(arg) -> int:
    label = arg.get_value()
    if not label in labels:
        exit(52)
    i = 0
    while (i <= len(instructions)):
        i += 1
        if instructions[i].get_args()[0].get_value() == label:
            return i   
    exit(52)

def interpret_JUMPIF(arg1, arg2, arg3, relation) -> int:
    if arg2.get_type() == "var":
        var_name = arg2.get_value().split("@")[1]
        index = get_index_of_var(var_name, GF)
        arg2.set_value(GF[index].get_value())
        arg2.set_type(GF[index].get_type())
    if arg3.get_type() == "var":
        var_name = arg3.get_value().split("@")[1]
        index = get_index_of_var(var_name, GF)
        arg3.set_value(GF[index].get_value())
        arg3.set_type(GF[index].get_type())

    if arg2.get_type() == arg3.get_type() or arg2.get_type() == "nil" or arg3.get_type() == "nil":
        if arg2.get_value() == arg3.get_value():
            if relation == "EQ":
                return interpret_JUMP(arg1)
            else:
                return -1
        else:
            if relation == "NEQ":
                return interpret_JUMP(arg1)
            else:
                return -1
    else:
        exit(53)
            
def interpret(instructions):
    instruction_number = 0
    while (instruction_number < len(instructions)):
        ins = instructions[instruction_number]
        match ins.get_opcode().upper():
            case "DEFVAR":
                interpret_DEFVAR(ins.get_args()[0])
            case "MOVE":
                interpret_MOVE(ins.get_args()[0], ins.get_args()[1])
            case "READ":
                interpret_READ(ins.get_args()[0], ins.get_args()[1])
            case "PUSHS":
                stack.append(ins.get_args()[0].get_value())
            case "POPS":
                interpret_POPS(ins.get_args()[0])
            case "WRITE":
                interpret_WRITE(ins.get_args()[0])
            case "ADD":
                interpret_arithmetic(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "ADD")
            case "SUB":
                interpret_arithmetic(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "SUB")
            case "MUL":
                interpret_arithmetic(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "MUL")
            case "IDIV":
                interpret_arithmetic(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "IDIV")
            case "LT":
                interpret_relation(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "LT")
            case "GT":
                interpret_relation(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "GT")
            case "EQ":
                interpret_relation(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "EQ")
            case "AND":
                interpret_logic(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "AND")
            case "OR":
                interpret_logic(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "OR")
            case "NOT":
                interpret_NOT(ins.get_args()[0], ins.get_args()[1])
            case "EXIT":
                interpret_EXIT(ins.get_args()[0])
            case "TYPE":
                interpret_TYPE(ins.get_args()[0], ins.get_args()[1])
            case "LABEL":
                print("",end='')
            case "JUMP":
                instruction_number = interpret_JUMP(ins.get_args()[0])
            case "JUMPIFEQ":
                tmp = interpret_JUMPIF(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "EQ")
                if tmp != -1:
                    instruction_number = tmp
            case "JUMPIFNEQ":
                tmp = interpret_JUMPIF(ins.get_args()[0], ins.get_args()[1], ins.get_args()[2], "NEQ")
                if tmp != -1:
                    instruction_number = tmp
        instruction_number += 1


#arg parse
parser = argparse.ArgumentParser()
parser.add_argument("--source", help="File with XML representation of source code")
parser.add_argument("--input",  help="File with inputs for interpretation of source code")
args = parser.parse_args()
if not args.source and not args.input:
    exit(11)
if args.source:
    source = args.source
if args.input:
    input = args.input
    input_current_line = 0



#Load and check XML
try:
    tree = ET.parse(source)
except:
    exit(31)
root = tree.getroot()

if root.tag != "program":
    exit(32)

for ins in root:
    if ins.tag != "instruction":
        exit(32)
    if len(ins.attrib) < 2:
        exit(32)
    if not ins.attrib['order'].isnumeric():
        exit(32)
    if int(ins.attrib['order']) < 1:
        exit(32)

sort_children(root, "order")
for ins in root.findall("*"):
    ins[:] = sorted(ins, key=attrgetter("tag"))
last_order = 0
for ins in root:
    if ins.attrib['order'] == last_order:
        exit(32)
    last_order = ins.attrib['order']

    ins_atributes = list(ins.attrib.keys())
    if not "order" in ins_atributes or not "opcode" in ins_atributes:
        exit(32)
    arg_count = 0
    expected_arg_count = count_arg(ins.attrib['opcode'])
    
    for arg in ins:    
        if arg.attrib['type'] == "int":
            if not(re.match(r"^[-+]?\d+$", arg.text)):
                exit(32)
        arg_count += 1
        if not(re.match(r"arg" + re.escape(str(arg_count)) + "", arg.tag)):
            exit(32)
    if arg_count != expected_arg_count:
        exit(32)
    
#Create instruction objects from XML
instructions = []
for element in root:
    i = instruction(element.attrib['order'], element.attrib['opcode'])
    match count_arg(element.attrib['opcode']):
        case 0:
            continue
        case 1: 
            add_args2ins(i, 1, element)
        case 2:
            add_args2ins(i, 2, element)
        case 3:
            add_args2ins(i, 3, element)
        case _:
            exit(9)
    instructions.append(i)

GF = []
LF = []
stack = []
labels = []
preload_labels()

interpret(instructions)





#print_labels()
#print_all()