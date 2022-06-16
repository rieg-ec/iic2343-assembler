import pyparsing as pp

charset = "".join(chr(i) for i in range(32, 127)).replace("#", "")

parser = pp.Char('"') + pp.Word(pp.alphas)("string") + pp.Char('"')
