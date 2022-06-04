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

    empty_ram_lines = 4096 - len(instructions_in_bits)
    bits = ",\n".join(
        f'"{i}"' for i in instructions_in_bits + ["0" * 36] * empty_ram_lines
    )

    print(
        """
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
USE IEEE.NUMERIC_STD.ALL;

entity ROM is
    Port (
        clk       : in  std_logic;
        write     : in  std_logic;
        disable   : in  std_logic;
        address   : in  std_logic_vector(11 downto 0);
        datain    : in  std_logic_vector(35 downto 0);
        dataout   : out std_logic_vector(35 downto 0)
          );
end ROM;

architecture Behavioral of ROM is

type memory_array is array (0 to ((2 ** 12) - 1) ) of std_logic_vector (35 downto 0);

signal memory : memory_array:= (
    """
    )

    print(bits)

    print(
        """
);

begin

process (clk)
    begin
       if (rising_edge(clk)) then
            if(write = '1') then
                memory(to_integer(unsigned(address))) <= datain;
            end if;
       end if;
end process;

with disable select
    dataout <= memory(to_integer(unsigned(address)))  when '0',
            (others => '0') when others;

end Behavioral;
"""
    )
