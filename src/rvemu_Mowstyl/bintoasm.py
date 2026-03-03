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
"""Code related to translating from machine code binary to RISC-V assembler code."""


from __future__ import annotations
from .instruction_set import InstructionType, getReversedSet

import numpy as np


BIT0_6_MASK = (1 << 7) - 1
BIT7_11_MASK = ((1 << 5) - 1) << 7
BIT12_14_MASK = ((1 << 3) - 1) << 12
BIT15_19_MASK = BIT7_11_MASK << 8
BIT20_24_MASK = BIT15_19_MASK << 5
BIT25_31_MASK = BIT0_6_MASK << 25
BIT31_MASK = 1 << 31
IMM12_MASK = (1 << 12) - 1
IMM20_MASK = (1 << 20) - 1
BIT12_31_MASK = IMM20_MASK << 12
ALL_MASK = (1 << 32) - 1

def bin_to_asm(bin_code: List[int], base: str, extensions: List[str] = []):
    reversed_set, load_opcode = getReversedSet(base, extensions)
    asm_code = []
    for i in range(len(bin_code)):
        encoded_asm = bin_code[i]
        opcode = encoded_asm & BIT0_6_MASK
        has_func7: bool = False
        if opcode not in reversed_set:
            print("Error: Unknown opcode {opcode} in line {i}")
            return None
        instruction_type, instruction = reversed_set[opcode]
        bit7_11 = (encoded_asm & BIT7_11_MASK) >> 7
        bit15_19 = (encoded_asm & BIT15_19_MASK) >> 15
        bit20_24 = (encoded_asm & BIT20_24_MASK) >> 20
        bit12_14 = (encoded_asm & BIT12_14_MASK) >> 12
        bit25_31 = (encoded_asm & BIT25_31_MASK) >> 25
        func7 = None
        if instruction_type != InstructionType.U and instruction_type != InstructionType.J:
            func3 = bit12_14
            instruction = instruction[func3]
            if isinstance(instruction, dict):
                has_func7 = True
                func7 = bit25_31
                instruction = instruction[func7]

        if instruction_type == InstructionType.R:
            asm_code.append(f"{instruction} x{bit7_11}, x{bit15_19}, x{bit20_24}")
            continue
        sign_bit = (encoded_asm & BIT31_MASK)
        if instruction_type == InstructionType.I:
            high = 0
            if func7 is None:
                high = (bit25_31 << 5)
            else:  # Shifts are unsigned
                sign_bit = 0
            imm = bin_to_dec(high + bit20_24, sign_bit)
            if opcode != load_opcode:
                asm_code.append(f"{instruction} x{bit7_11}, x{bit15_19}, {imm}")
            else:
                asm_code.append(f"{instruction} x{bit7_11}, {imm}(x{bit15_19})")
            continue
        if instruction_type == InstructionType.S:
            imm = bin_to_dec((bit25_31 << 5) + bit7_11, sign_bit)
            asm_code.append(f"{instruction} x{bit20_24}, {imm}(x{bit15_19})")
            continue
        if instruction_type == InstructionType.B:
            imm0_4 = bit7_11 & ((1 << 5) - 2)
            imm5_10 = (bit25_31 & ((1 << 6) - 1)) << 5
            imm11 = (bit7_11 & 1) << 11
            imm = bin_to_dec((sign_bit << 12) + imm11 + imm5_10 + imm0_4, sign_bit)
            asm_code.append(f"{instruction} x{bit15_19}, x{bit20_24}, {hex(imm)}")
            continue
        bit12_31 = (encoded_asm & BIT12_31_MASK) >> 12
        if instruction_type == InstructionType.U:
            imm = bin_to_dec(bit12_31, 0)
            asm_code.append(f"{instruction} x{bit7_11}, {hex(imm)}")
            continue
        if instruction_type == InstructionType.J:
            imm12_19 = bit12_14 + (bit15_19 << 3)
            rem = encoded_asm >> 20
            imm11 = rem & 1
            rem = rem >> 1
            imm0_10 = (rem & ((1 << 10) - 1)) << 1
            imm = bin_to_dec(imm0_10 + (imm11 << 11) + (imm12_19 << 12) + (sign_bit << 20), sign_bit)
            asm_code.append(f"{instruction} x{bit7_11}, {hex(imm)}")
            continue
        print(f"Error: Unknown instruction type {instruction_type}")
        return None
    return asm_code


def bin_to_dec(imm, sign_bit):
    if sign_bit != 0:
        imm = -np.int32((imm - 1) ^ IMM12_MASK)
    else:
        imm = np.int32(imm)
    return imm
