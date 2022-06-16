import pyparsing as pp

binary = pp.Word(pp.nums)("value") + "b"
hex = pp.Word(pp.nums)("value") + "h"
decimal = pp.Word(pp.nums)("value") | pp.Word(pp.nums)("value") + "d"

parser = (binary("bin") | hex("hex") | decimal("dec"))("literal")
