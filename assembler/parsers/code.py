import pyparsing as pp
from parsers import literal

register = (pp.Char("A") | pp.Char("B"))("register")
variable = pp.Word(pp.alphas + "_")("variable")
memory = ("(" + (register | literal.parser | variable) + ")")("memory")
label = pp.Word(pp.alphanums + "_")("label")

operands_with_label = literal.parser | memory | register | label
operands_with_variable = literal.parser | memory | register | variable

single_operand = operands_with_label("operand_left")
double_operand = (
    operands_with_variable("operand_left")
    + pp.Char(",").suppress()
    + operands_with_variable("operand_right")
)

# fmt: off
JMP = (
    (
        pp.Literal("JMP")("jmp")
        | pp.Literal("JEQ")("jeq")
        | pp.Literal("JNE")("jne")
        | pp.Literal("JGT")("jgt")
        | pp.Literal("JGE")("jge")
        | pp.Literal("JLT")("jlt")
        | pp.Literal("JLE")("jle")
        | pp.Literal("JCR")("jcr")
    )("instruction")
    + (label("label") | literal.parser)
)("jmp")
MOV = ((pp.Literal("MOV"))("instruction") + double_operand)("mov")
ADD = ((pp.Literal("ADD"))("instruction") + (double_operand | single_operand))("add")
SUB = ((pp.Literal("SUB"))("instruction") + (double_operand | single_operand))("sub")
AND = ((pp.Literal("AND"))("instruction") + (double_operand | single_operand))("_and")
OR = ((pp.Literal("OR"))("instruction") + (double_operand | single_operand))("_or")
XOR = ((pp.Literal("XOR"))("instruction") + (double_operand | single_operand))("xor")
NOT = ((pp.Literal("NOT"))("instruction") + (double_operand | single_operand))("_not")
SHL = ((pp.Literal("SHL"))("instruction") + (double_operand | single_operand))("shl")
SHR = ((pp.Literal("SHR"))("instruction") + (double_operand | single_operand))("shr")
INC = ((pp.Literal("INC"))("instruction") + single_operand)("inc")
DEC = ((pp.Literal("DEC"))("instruction") + single_operand)("decr")
CMP = ((pp.Literal("CMP"))("instruction") + double_operand)("cmp")
NOP = (pp.Literal("NOP")("instruction"))("nop")
PUSH = ((pp.Literal("PUSH"))("instruction") + single_operand)("_push")
POP = ((pp.Literal("POP"))("instruction") + single_operand)("_pop")
CALL = ((pp.Literal("CALL"))("instruction") + single_operand)("call")
RET = ((pp.Literal("RET"))("instruction"))("ret")
# fmt: on

parser = (
    MOV
    | ADD
    | SUB
    | AND
    | OR
    | XOR
    | NOT
    | SHL
    | SHR
    | INC
    | DEC
    | CMP
    | NOP
    | PUSH
    | POP
    | JMP
    | CALL
    | RET
)("instruction")
