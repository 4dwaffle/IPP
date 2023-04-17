import re
import argparse
import xml.etree.ElementTree as ET


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
        self.type = arg_type
        self.value = value
    def get_type(self):
        return self.type
    def get_value(self):
        return self.value


def add_args2ins(ins, arg_count, element):
    i = 0
    while i < arg_count:
        ins.add_arg(element[i].attrib['type'], element[i].text)
        i+=1

def print_ins(instructions):
    print()
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
    print()

#returns number of arguments based on the opcode
def count_arg(oppcode):
    match oppcode:
        #0 ARGS
        case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK":  return 0
        #1 ARG
        case "DEFVAR" | "CALL" | "PUSH" | "POPS" | "JUMP" | "EXIT" | "DPRINT" | "LABEL" | "WRITE":   return 1
        #2 ARGS
        case "MOVE" |  "INT2CHAR" | "READ" | "STRLEN" |  "TYPE":  return 2
        #3 ARGS
        case "ADD" | "SUB" | "MUL" | "IDIV" | "LT" | "GT" | "EQ" | "AND" | "OR" | "NOT" | "STRI2INT" | "CONCAT" | "GETCHAR" | "SETCHAR" | "JUMPIFEQ" | "JUMPIFNEQ":   return 3
        case _:     return -1       #ERR



def interpret(ins):
    match ins.get_opcode().upper():
        case "DEFVAR":
            print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    



#arg parse
parser = argparse.ArgumentParser()
parser.add_argument("--source", help="File with XML representation of source code")
parser.add_argument("--input",  help="File with inputs for interpretation of source code")
args = parser.parse_args()
if not args.source and not args.input:
    print("At least one of parameters (--source or --input) is obligatory.")
if args.source:
    source = args.source
if args.input:
    input = args.input



#Load and check XML
tree = ET.parse(source)
root = tree.getroot()

if root.tag != 'program':
    print("ERR1")

for ins in root:
    if ins.tag != 'instruction':
        print("ERR2")
        break
    ins_atributes = list(ins.attrib.keys())
    if not 'order' in ins_atributes or not 'opcode' in ins_atributes:
        print('ERR3')
    for arg in ins:
        if not(re.match(r"arg[123]", arg.tag)):
            print("ERR4")
    
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
            print(element.attrib['opcode'])
            print("ERR5")
    instructions.append(i)
print_ins(instructions)

#intepret instructions
for i in instructions:
    interpret(i)



print("end")