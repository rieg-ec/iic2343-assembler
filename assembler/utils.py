from typing import Tuple, List
import pyparsing as pp
from parsers import code, data, label, array_item, char


class AsmInstruction:
    def __init__(self, raw_line, parsed_line, rom_dir=None) -> None:
        self.raw_line: str = raw_line
        self.parsed_line: pp.results.ParseResults = parsed_line
        self.rom_dir = rom_dir


def find_label_rom_address(label: str, rom: List[AsmInstruction]) -> int:
    """returns memory address of instruction right under label"""
    for (index, line) in enumerate(rom):
        if line.parsed_line.label_definition and line.parsed_line.label == label:
            instruction = rom[index + 1].parsed_line
            if instruction.label_definition:
                # instruction is another label definition, recursive call
                return find_label_rom_address(instruction.label, rom)

            return rom[index + 1].rom_dir

    raise Exception(f"Label {label} not in rom")


def find_variable_ram_address(name: str, ram: List[AsmInstruction]) -> int:
    for (index, line) in enumerate(ram):
        if line.parsed_line.variable.name == name:
            return index

    raise Exception(f"Variable {name} not in ram")


def move_data_to_ram(value: str, memory_dir: int) -> Tuple[str, str]:
    return (f"MOV A, {value}", f"MOV ({memory_dir}), A")


def clean_file_content(data: str) -> str:
    """returns file content without comments and empty lines"""
    out_tmp = data.split("\n")
    out = []
    for line in out_tmp:
        out.append(line.split("//")[0])
    return "\n".join(line for line in out if not line.isspace() and len(line) > 0)


def parse_asm(filename, only_instructions=False):
    with open(filename, encoding="latin-1") as file:
        file_data = clean_file_content(file.read())

        ram = []
        rom = []

        rom_dir = 0

        for line in file_data.split("\n"):
            if only_instructions:
                try:
                    parsed_line = code.parser.parse_string(line)
                    assembly_line = AsmInstruction(line, parsed_line, rom_dir)
                    rom.append(assembly_line)
                    rom_dir += 1
                except pp.exceptions.ParseException:
                    continue

            else:
                try:
                    parsed_line = data.parser.parse_string(line)
                    assembly_line = AsmInstruction(line, parsed_line)
                    ram.append(assembly_line)
                except pp.exceptions.ParseException:
                    try:
                        parsed_line = label.parser.parse_string(line)
                        assembly_line = AsmInstruction(line, parsed_line)
                        rom.append(assembly_line)
                    except pp.exceptions.ParseException:
                        try:
                            parsed_line = code.parser.parse_string(line)
                            assembly_line = AsmInstruction(line, parsed_line, rom_dir)
                            rom.append(assembly_line)
                            rom_dir += 1
                        except pp.exceptions.ParseException:
                            try:
                                parsed_line = array_item.parser.parse_string(line)
                                assembly_line = AsmInstruction(
                                    line, parsed_line, rom_dir
                                )
                                ram.append(assembly_line)
                            except:
                                continue

        return ram, rom


def convert_asm_to_bin(rom: List[AsmInstruction]) -> List[str]:
    instructions = []
    for asm in rom:
        if asm.parsed_line.ret or asm.parsed_line._pop:
            instructions.append("0" * 16 + "00000000000000010000")
        instruction = get_instruction_in_bits(asm)
        instructions.append(instruction)

    return instructions


def get_instruction_in_bits(asm: AsmInstruction) -> str:
    pl = asm.parsed_line

    if (pl.inc or pl.decr) and pl.operand_left.as_list() == ["A"]:
        op = "0" * 15 + "1"
    elif pl.literal:
        op = literal_to_padded_bits(asm)
    else:
        op = "0" * 16

    op += pre_PC(asm)
    op += load_A(asm)
    op += load_B(asm)
    op += sel_A(asm)
    op += sel_B(asm)
    op += sel_ALU(asm)
    op += sel_add(asm)
    op += sel_din(asm)
    op += sel_PC(asm)
    op += w(asm)
    op += inc_SP(asm)
    op += dec_SP(asm)
    op += load_PC(asm)

    return op


def pre_PC(asm):
    pl = asm.parsed_line

    return "1" if pl.jmp or pl.call or pl.ret else "0"


def load_A(asm):
    pl = asm.parsed_line

    if pl.cmp or pl._push:
        return "0"

    return "1" if pl.register and pl.operand_left.as_list() == ["A"] else "0"


def load_B(asm):
    pl = asm.parsed_line

    if pl.cmp or pl._push:
        return "0"

    return "1" if pl.register and pl.operand_left.as_list() == ["B"] else "0"


def sel_A(asm):
    pl = asm.parsed_line

    if pl.mov:
        if pl.operand_right.as_list() == ["A"]:
            return "00"
        return "11"

    if pl.inc:
        if pl.register == "A":
            return "00"
        return "01"

    if pl._push:
        if pl.register == "A":
            return "00"
        return "11"

    if pl._pop:
        return "11"

    return "00"


def sel_B(asm):
    pl = asm.parsed_line

    if pl.jmp or pl.call:
        return "00"

    if (
        pl.operand_right
        and pl.memory
        and pl.operand_right.as_list() == pl.memory.as_list()
    ):
        return "10"

    if (
        pl.operand_right
        and pl.literal
        and pl.operand_right.as_list() == pl.literal.as_list()
    ):
        return "01"

    if pl.operand_right and pl.register:
        if pl.operand_right.as_list() == ["B"]:
            return "00"

        if pl.operand_left.as_list() == ["A"] and pl.operand_right.as_list() == ["B"]:
            return "00"

    if (pl.inc or pl.decr) and pl.operand_left.as_list() == ["A"]:
        return "01"

    if (pl.inc or pl.decr) and pl.memory:
        return "10"

    if not pl.operand_right and pl.memory:
        return "00"

    if not pl.operand_right and pl.literal:
        return "01"

    if pl._push and pl.operand_left.as_list() == ["A"]:
        return "11"

    if pl.mov and pl.operand_right.as_list() == ["A"]:
        return "11"

    if pl._pop:
        return "10"

    return "00"


def sel_ALU(asm):
    pl = asm.parsed_line

    if pl.sub or pl.decr or pl.cmp:
        return "001"

    if pl._and:
        return "010"

    if pl._or:
        return "011"

    if pl.xor:
        return "100"

    if pl._not:
        return "101"

    if pl.shl:
        return "110"

    if pl.shr:
        return "111"

    return "000"


def sel_add(asm):
    pl = asm.parsed_line

    if pl._push or pl.call or pl.ret or pl._pop:
        return "10"

    if pl.memory and pl.memory[1] == "B":
        return "01"

    return "00"


def sel_din(asm):
    return "1" if asm.parsed_line.call else "0"


def sel_PC(asm):
    return "1" if asm.parsed_line.ret else "0"


def w(asm):
    pl = asm.parsed_line

    if (
        pl._push
        or pl.call
        or (pl.memory and pl.operand_left.as_list() == pl.memory.as_list())
    ):
        return "1"

    return "0"


def inc_SP(asm):
    return "0"


def dec_SP(asm):
    return "1" if asm.parsed_line._push or asm.parsed_line.call else "0"


def load_PC(asm):
    pl = asm.parsed_line

    if pl.jeq:
        return "001"
    elif pl.jne:
        return "010"
    elif pl.jgt:
        return "011"
    elif pl.jge:
        return "100"
    elif pl.jlt:
        return "101"
    elif pl.jle:
        return "110"
    elif pl.jcr:
        return "111"
    else:
        return "000"


def literal_to_padded_bits(asm: AsmInstruction):
    pl = asm.parsed_line

    if pl.bin:
        return pad_bits(pl.bin[0], 16)

    elif pl.hex:
        bits = str(bin(int(pl.hex[0], 16))).replace("0b", "")
        return pad_bits(bits)

    else:
        bits = str(bin(int(pl.dec[0]))).replace("0b", "")
        if len(bits) > 16:
            diff = len(bits) - 16
            bits = bits[diff:-1]

        return pad_bits(bits)


def pad_bits(bits: str, length: int = 16) -> str:
    return "0" * (length - len(bits)) + bits
