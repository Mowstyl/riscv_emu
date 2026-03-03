#   ---------------------------------------------------------------------------------
#   RISC-V Emulator
#   Copyright (C) 2026  Mowstyl
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   ---------------------------------------------------------------------------------
"""Code related to translating from pure RISC-V assembler code to machine code binary."""


from __future__ import annotations
from .instruction_set import InstructionType, getInstructionSet, reg_alias, pseudo_translate
from .bintoasm import bin_to_asm
from .compiler import lexer
from math import ceil

import numpy as np
import numpy.typing as npt
import re


'''
RegEx Structure:
    type
    rd
    rs1 (optional)
    rs2 (optional)
    imm (optional)
    offset
    base
It expects this:
    type rd, (rs1, rs2 | imm) | offset(base)
Groups:
    1: type
    2: rd id (without the x)
    3: rs1 id (without the x)
    4: rs2 id (without the x)
    5: imm sign
    6: imm base (b for bin, x for hex, nothing for dec)
    7: imm
    8: offset sign
    9: offset base (b for bin, x for hex, nothing for dec)
    10: offset
    11: rs2 id (containing mem. addr.) (without the x)
'''

reg_regex = r"(?:(?:x|t|s|a)(?:[1-3]?[0-9]))|(?:(?:g|f|t|s)p)|(?:ra|zero)"

imm_regex = r"(?:0(?:x|X)[0-9a-fA-F]+)|(?:0(?:b|B)[01]+)|(?:(?:\+|-)?[0-9]+)"

arg_regex = rf"(?:{reg_regex})|(?:{imm_regex})"

test_regex = rf"^\s*([a-z\.]+)(?:\s+({arg_regex})(?:\s*,\s*({arg_regex}))?(?:\s*,|\(\s*({arg_regex})\))?)?\s*$"

pseudo_regex = r"^\s*([a-z\.]+)(?:\s+(?:x([1-3]?[0-9]))?\s*,?\s*(?:(?:(?:x([1-3]?[0-9])\s*,\s*)?(?:(?:x([1-3]?[0-9]))|(\+|-)?(?:0(x|b))?([0-9a-fA-F]+)))|(?:(\+|-)?(?:0(x|b))?([0-9a-fA-F]+)\s*\(\s*x([1-3]?[0-9])\s*\)))?(?:\s*,\s*x([1-3]?[0-9]))?)?$"

riscv_regex = r"^\s*([a-z\.]+)\s+x([1-3]?[0-9])\s*,\s*(?:(?:(?:x([1-3]?[0-9])\s*,\s*)?(?:(?:x([1-3]?[0-9]))|(\+|-)?(?:0(x|b))?([0-9a-fA-F]+)))|(?:(\+|-)?(?:0(x|b))?([0-9a-fA-F]+)\s*\(\s*x([1-3]?[0-9])\s*\)))$"

reg_regex = r"((?:\s*,|\()|\s+)((?:(?:s|t|a)[1-9]*[0-9])|zero|ra|sp|tp|gp|fp)"

pseudo_parser = re.compile(pseudo_regex)

riscv_parser = re.compile(riscv_regex)

reg_parser = re.compile(reg_regex)


BIT_MASK: List[int] = [np.uint32(1 << i) for i in range(32)]


def parse(file_name):
    all_tokens = []
    i = 1
    in_comment = False
    with open(file_name, 'r') as file:
        for line in file:
            tokens, errored, in_comment = lexer.tokenize(line, file_name, i, in_comment)
            if tokens is not None and len(tokens) > 0:
                all_tokens.append(tokens)
            i += 1
    print(all_tokens)


def asm_to_bin(asm_code: List[str], base: str, extensions: List[str] = []) -> npt.NDArray[np.int32]:
    """Doc String."""
    instruction_set: Dict[str, Dict[str, Any]] = getInstructionSet(base, extensions)
    num_instructions: int = len(asm_code)
    bin_data: npt.NDArray[np.uint32] = np.empty(num_instructions, dtype=np.uint32)
    errored: bool = False

    for i in range(num_instructions):
        raw_instruction: str = asm_code[i]
        result: np.uint32 = np.uint32(0)
        parsed_instruction: re.Match = riscv_parser.match(raw_instruction)
        if (parsed_instruction is None):
            print("Error: Wrong instruction format in line", i)
            errored = True
            continue
        instruction_name: str = parsed_instruction.group(1)
        if instruction_name not in instruction_set:
            print("Error: Unknown instruction \"" + instruction_name + "\" in line", i)
            errored = True
            continue
        instruction_data: Dict[str, Any] = instruction_set[instruction_name]
        instruction_type = instruction_data["type"]

        # Operation info
        result += instruction_data["op"]
        if "func3" in instruction_data:
            result += instruction_data["func3"] << 12
        if "func7" in instruction_data:
            result += instruction_data["func7"] << 25

        # Immediate
        if instruction_type != InstructionType.R:
            immediate, field_bits, has_error = calculate_immediate(instruction_type, instruction_data, parsed_instruction, i)
            if has_error:
                errored = True
            bit_list: List[int] = [1 if char == "1" else 0 for char in immediate[::-1]]
            if field_bits > 5:  # Shifts
                result += bit_list[-1] * BIT_MASK[31]
            acc: int = 0
            if instruction_type == InstructionType.I or instruction_type == InstructionType.S or instruction_type == InstructionType.B:
                acc2: int = 0
                for j in range(1, 5):
                    acc += bit_list[j] * BIT_MASK[j]
                if field_bits > 5:
                    for j in range(5, 11):
                        acc2 += bit_list[j] * BIT_MASK[j - 5]
                acc += bit_list[0] if instruction_type != InstructionType.B else bit_list[11]
                if instruction_type == InstructionType.I:
                    acc = acc << 20
                else:
                    acc = acc << 7
                acc2 = acc2 << 25
                result += acc + acc2
            elif instruction_type == InstructionType.U:
                for j in range(19):
                    result += bit_list[j] * BIT_MASK[12 + j]
            else:
                for j in range(12, 20):
                    result += bit_list[j] * BIT_MASK[j]
                result += bit_list[11] * BIT_MASK[20]
                for j in range(1, 11):
                    result += bit_list[j] * BIT_MASK[20 + j]

        # Destination Registry
        if instruction_type != InstructionType.S and instruction_type != InstructionType.B:
            rd = int(parsed_instruction.group(2))
            if rd < 0 or rd > 31:
                print(f"Error: Unknown dest registry x{rd} in line {i}")
                errored = True
            result += np.uint32(rd) << 7

        # Source Registries
        if instruction_type != InstructionType.U and instruction_type != InstructionType.J:  # Sources
            rs1_group = 3 if instruction_type != InstructionType.S and instruction_type != InstructionType.B else (2 if instruction_type != InstructionType.S else 11)
            if instruction_type != InstructionType.S and parsed_instruction.group(11) is not None:
                rs1_group = 11
            rs1 = int(parsed_instruction.group(rs1_group))
            if rs1 < 0 or rs1 > 31:
                print(f"Error: Unknown source 1 registry x{rs1} in line {i}")
                errored = True
            result += np.uint32(rs1) << 15
            if instruction_type != InstructionType.I:  # Source 2
                rs2_group = 2 if instruction_type == InstructionType.S else (4 if instruction_type != InstructionType.B else 3)
                rs2 = int(parsed_instruction.group(rs2_group))
                if rs2 < 0 or rs2 > 31:
                    print(f"Error: Unknown source 2 registry x{rs2} in line {i}")
                    errored = True
                result += np.uint32(rs2) << 20
        bin_data[i] = result
    if (errored):
        return None
    return bin_data


def calculate_immediate(instruction_type, instruction_data, parsed_instruction, line_number) -> Tuple[str, int, bool]:
    errored = False
    starting_group = 5
    if parsed_instruction.group(10) is not None:
        starting_group = 8

    # Sign bit
    raw_sign: str = parsed_instruction.group(starting_group)
    if raw_sign is not None:
        if parsed_instruction.group(starting_group + 1) is not None:
            print(f"Error: Unexpected sign with hex or bin immediate in line {line_number}")
            errored = True
    else:
        raw_sign = ""
    sext = True

    # Calculate immediate size
    num_bits: int = 12
    only_even: bool = instruction_type == InstructionType.B or instruction_type == InstructionType.J
    if "func7" in instruction_data:
        num_bits = 5
        if instruction_type == InstructionType.I:
            sext = False
            if raw_sign != "":
                print(f"Error: Unexpected sign with shift instruction in line {line_number}")
                errored = True
    elif instruction_type == InstructionType.U or instruction_type == InstructionType.J:
        num_bits = 20
    if only_even:
        num_bits += 1
    max_num: int = 1 << (num_bits - 1) if sext else (1 << num_bits) - 1
    min_num: int = -max_num if sext else 0
    if sext:
        max_num -= 1

    # Decode the number
    encoding: str = parsed_instruction.group(starting_group + 1)
    raw_number: str = raw_sign + parsed_instruction.group(starting_group + 2)
    current_size: int = len(raw_number)
    immediate: str  # Final number in binary
    original: str = raw_number
    if encoding is not None:
        original = "0" + encoding + original
    if encoding is None:
        int_number = np.int32(raw_number)
        if not sext:
            int_number = np.uint32(raw_number)
        if int_number > max_num or int_number < min_num:
            print(f"Error: Immediate {raw_number} too big. Expected range [{min_num}, {max_num}] in line {line_number}")
            errored = True
        immediate = np.binary_repr(int_number, width=num_bits)
    elif encoding == "x":
        max_hex_size: int = ceil(num_bits / 4)
        extra_bits: int = num_bits % 4
        max_most: int = (1 << extra_bits) - 1
        if current_size > max_hex_size or (max_most != 0 and current_size == max_hex_size and int(raw_number[0], 16) > max_most):
            print(f"Error: Immediate 0x{raw_number} too big. Max expected value {hex((1 << num_bits) - 1)} in line {line_number}")
            errored = True
        if extra_bits == 0:
            extra_bits = 4
        raw_number = np.binary_repr(int(raw_number, 16), width=num_bits)  # Raw number is now in binary of specified size
        current_size = len(raw_number)
    else:
        dirty: bool = current_size > num_bits
        while current_size > num_bits and current_size >= 2 and raw_number[0] == raw_number[1]:
            raw_number = raw_number[1:]
            current_size -= 1
        if current_size > num_bits:
            print(f"Error: Immediate 0b{raw_number} too big. Expected {num_bits} bit{"s" if num_bits > 1 else ""} value in line {line_number}")
            errored = True
        elif dirty:
            print(f"Warning: Too many leading sign bits in immediate 0b{raw_number}. Expected {num_bits} bit{"s" if num_bits > 1 else ""} value in lineline_number{line_number}")
        if current_size < num_bits:
            raw_number = "0" + raw_number  # Ensure the first bit is the sign bit
            current_size += 1
    if encoding is not None:  # Only binary after this point
        immediate = raw_number
        if current_size < num_bits:
            sign_bit: str = raw_number[0]
            immediate = sign_bit * (num_bits - current_size) + immediate

    if only_even and immediate[-1] != "0":
        print(f"Error: Immediate {original} must be an even number in line {line_number}")
        errored = True
    return immediate, num_bits, errored


def reg_from_alias(match):
    return match.group(1) + reg_alias[match.group(2)]


def purify_asm(asm_code: List[str]) -> List[str]:
    pure_asm = []
    errored = False
    for i in range(len(asm_code)):
        raw_line = asm_code[i]
        line = reg_parser.sub(reg_from_alias, raw_line)
        parsed = riscv_parser.match(line)
        if parsed is None:
            print(f"Error: Could not parse instruction in line {i}")
            errored = True
            continue
        name = parsed.group(1)
        if name in pseudo_translate:
            translation = pseudo_translate[name](parsed)
            for instruction in translation:
                pure_asm.append(line)
        else:
            pure_asm.append(line)
    if errored:
        return None
    return pure_asm


def sample():
    sample_code = [
        "add x31, x30, x0",
        "addi x31, x30,0xFFF",
        "addi x31,x30,0b11111000010",
        "lui x1, 0x27",
        "addi x31,x30, -27",
        "lw x5, 0(x3 )",
        "jal x0, 24",
        "lw x5, 0(x7)",
        "bge x6, x5, 0x2C",
        "sw x6, 0(x29)",
        "sub x5, x6, x7",
        "addi s0, s1, 12",
        "lh t2, -6(s3)",
        "srai t1,t2, 29",
        "sb t5, 45(zero)",
        "beq s0, t5, 0x10",
        "lui s5, 0x8cdef",
        "jal ra, 0xa67f8"]
    pure_asm = purify_asm(sample_code)
    res = asm_to_bin(pure_asm, "RV32I", ["RVM"])
    for i in range(len(res)):
        instruction = pure_asm[i]
        encoded_instruction = res[i]
        print(f"{instruction} -> {encoded_instruction:#0{10}x}")
        print(np.binary_repr(encoded_instruction, width=32))
    asm = bin_to_asm(res, "RV32I", ["RVM"])
    for i in range(len(asm)):
        print(pure_asm[i], "->", asm[i])

if __name__ == "__main__":
    sample()
