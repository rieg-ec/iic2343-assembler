import pyparsing as pp

from parsers import literal

parser = pp.Group(pp.Word(pp.alphanums + "_")("name") + literal.parser)("variable")

parser.ignore(pp.Literal("JMP"))
parser.ignore(pp.Literal("JEQ"))
parser.ignore(pp.Literal("JNE"))
parser.ignore(pp.Literal("JGT"))
parser.ignore(pp.Literal("JGE"))
parser.ignore(pp.Literal("JLT"))
parser.ignore(pp.Literal("JLE"))
parser.ignore(pp.Literal("JCR"))
