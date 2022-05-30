import pyparsing as pp

from parsers import literal

parser = pp.Group(pp.Word(pp.alphanums + "_")("name") + literal.parser)("variable")
