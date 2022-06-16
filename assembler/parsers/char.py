import pyparsing as pp

charset = "".join(chr(i) for i in range(32, 127)).replace("#", "")

parser = pp.Char("'") + pp.Char(charset)("char") + pp.Char("'")
