import re
import argparse
import xml.etree.ElementTree as ET

print("ahoj")
parser = argparse.ArgumentParser()
parser.add_argument("--source", help="File with XML representation of source code")
parser.add_argument("--input", help="File with inputs for interpretation of source code")
args = parser.parse_args()
if not args.source and not args.input:
    print("At least one of parameters (--source or --input) is obligatory.")
if args.source:
    source = args.source
    print(source)
if args.input:
    input = args.input
    print(input)