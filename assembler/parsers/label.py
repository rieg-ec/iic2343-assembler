import pyparsing as pp

parser = (pp.Word(pp.alphanums + "_")("label") + pp.Word(":").suppress())(
    "label_definition"
)

parser.ignore(pp.Literal("DATA:"))
parser.ignore(pp.Literal("CODE:"))
