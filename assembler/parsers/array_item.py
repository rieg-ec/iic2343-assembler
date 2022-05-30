import pyparsing as pp


parser = pp.Word(pp.alphanums)("array_item")

parser.ignore(pp.Literal("DATA:"))
parser.ignore(pp.Literal("CODE:"))
