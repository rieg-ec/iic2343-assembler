import sys
import os
from utils import (
    convert_asm_to_bin,
    move_data_to_ram,
    find_label_rom_address,
    find_variable_ram_address,
    parse_asm,
)

filename = sys.argv[1]

if __name__ == "__main__":
    ram, rom = parse_asm(filename)

    with open("tmp.asm", "w") as file:
        for (index, line) in enumerate(ram):
            # create instructions to move variables to ram
            try:
                literal = "".join(line.parsed_line.variable.literal)
            except AttributeError:
                literal = line.parsed_line[0]

            instructions = move_data_to_ram(literal, index)
            for instruction in instructions:
                file.write(instruction + "\n")

        for line in rom:
            base = len(ram) * 2
            if not line.parsed_line.label_definition:
                pl = line.parsed_line

                if pl.label:
                    rom_dir = find_label_rom_address(pl.label, rom)
                    new_line = line.raw_line.replace(pl.label, str(rom_dir + base))
                    file.write(new_line + "\n")

                elif pl.variable:
                    ram_dir = find_variable_ram_address(pl.variable, ram)
                    new_line = line.raw_line.replace(pl.variable, str(ram_dir))
                    file.write(new_line + "\n")

                else:
                    file.write(line.raw_line + "\n")

    _, rom = parse_asm("tmp.asm", only_instructions=True)
    os.remove("tmp.asm")

    instructions_in_bits = convert_asm_to_bin(rom)
    for instruction in instructions_in_bits:
        print(instruction)
