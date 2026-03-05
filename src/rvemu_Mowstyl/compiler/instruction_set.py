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
"""Code related to defining the instructions available."""

from __future__ import annotations
from enum import Enum


InstructionType: Enum = Enum("InstructionType", [
    "R",
    "I",
    "S",
    "B",
    "U",
    "J"
    ])


reg_alias = {
    "zero": "x0",
    "ra": "x1",
    "sp": "x2",
    "gp": "x3",
    "tp": "x4",
    "t0": "x5",
    "t1": "x6",
    "t2": "x7",
    "fp": "x8",
    "s0": "x8",
    "s1": "x9",
    "a0": "x10",
    "a1": "x11",
    "a2": "x12",
    "a3": "x13",
    "a4": "x14",
    "a5": "x15",
    "a6": "x16",
    "a7": "x17",
    "s2": "x18",
    "s3": "x19",
    "s4": "x20",
    "s5": "x21",
    "s6": "x22",
    "s7": "x23",
    "s8": "x24",
    "s9": "x25",
    "s10": "x26",
    "s11": "x27",
    "t3": "x28",
    "t4": "x29",
    "t5": "x30",
    "t6": "x31"
    }

alias_reg = {v: k for k, v in reg_alias.items()}


rv32i_instructions: Dict[str, Dict[str, Any]] = {
    "add":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b000, "func7": 0b0000000},
    "sub":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b000, "func7": 0b0100000},
    "slt":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b010, "func7": 0b0000000},
    "sltu":   {"type": InstructionType.R, "op": 0b0110011, "func3": 0b011, "func7": 0b0000000},
    "addi":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b000},
    "slti":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b010},
    "sltiu":  {"type": InstructionType.I, "op": 0b0010011, "func3": 0b011},
    "and":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b111, "func7": 0b0000000},
    "or":     {"type": InstructionType.R, "op": 0b0110011, "func3": 0b110, "func7": 0b0000000},
    "xor":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b100, "func7": 0b0000000},
    "andi":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b111},
    "ori":    {"type": InstructionType.I, "op": 0b0010011, "func3": 0b110},
    "xori":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b100},
    "sll":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b001, "func7": 0b0000000},
    "srl":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b101, "func7": 0b0000000},
    "sra":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b101, "func7": 0b0100000},
    "slli":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b001, "func7": 0b0000000},
    "srli":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b101, "func7": 0b0000000},
    "srai":   {"type": InstructionType.I, "op": 0b0010011, "func3": 0b101, "func7": 0b0100000},
    "lw":     {"type": InstructionType.I, "op": 0b0000011, "func3": 0b010},
    "lh":     {"type": InstructionType.I, "op": 0b0000011, "func3": 0b001},
    "lhu":    {"type": InstructionType.I, "op": 0b0000011, "func3": 0b100},
    "lb":     {"type": InstructionType.I, "op": 0b0000011, "func3": 0b000},
    "lbu":    {"type": InstructionType.I, "op": 0b0000011, "func3": 0b011},
    "sw":     {"type": InstructionType.S, "op": 0b0100011, "func3": 0b010},
    "sh":     {"type": InstructionType.S, "op": 0b0100011, "func3": 0b001},
    "sb":     {"type": InstructionType.S, "op": 0b0100011, "func3": 0b000},
    "beq":    {"type": InstructionType.B, "op": 0b1100011, "func3": 0b000},
    "bne":    {"type": InstructionType.B, "op": 0b1100011, "func3": 0b001},
    "blt":    {"type": InstructionType.B, "op": 0b1100011, "func3": 0b100},
    "bge":    {"type": InstructionType.B, "op": 0b1100011, "func3": 0b101},
    "bltu":   {"type": InstructionType.B, "op": 0b1100011, "func3": 0b110},
    "bgeu":   {"type": InstructionType.B, "op": 0b1100011, "func3": 0b111},
    "jalr":   {"type": InstructionType.I, "op": 0b1100111},
    "jal":    {"type": InstructionType.J, "op": 0b1101111},
    "lui":    {"type": InstructionType.U, "op": 0b0110111},
    "auipc":  {"type": InstructionType.U, "op": 0b0010111}
    }

rvm_instructions: Dict[str, Dict[str, Any]] = {
    "mul":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b000, "func7": 0b0000001},
    "mulh":   {"type": InstructionType.R, "op": 0b0110011, "func3": 0b001, "func7": 0b0000001},
    "mulhsu": {"type": InstructionType.R, "op": 0b0110011, "func3": 0b010, "func7": 0b0000001},
    "mulhu":  {"type": InstructionType.R, "op": 0b0110011, "func3": 0b011, "func7": 0b0000001},
    "div":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b100, "func7": 0b0000001},
    "divu":   {"type": InstructionType.R, "op": 0b0110011, "func3": 0b101, "func7": 0b0000001},
    "rem":    {"type": InstructionType.R, "op": 0b0110011, "func3": 0b110, "func7": 0b0000001},
    "remu":   {"type": InstructionType.R, "op": 0b0110011, "func3": 0b111, "func7": 0b0000001}
    }

rv_instructions: Dict[str, Dict[str, Any]] = {
    "RV32I": rv32i_instructions,
    "RVM": rvm_instructions
    }

BIT_11 = 1 << 11
MASK0_11 = ((1 << 12) - 1)
MASK12_31 = ((1 << 20) - 1) << 12


def split_immediate(imm):
    least = imm & MASK0_11
    most = imm >> 12
    if (least & BIT_11) == 1:
        most += 1
    return least, most


def rebuild_immediate(match):
    sign = match.group(5)
    if sign is None:
        sign = ""
    prefix = match.group(6)
    if base is None:
        prefix = ""
        base = 10
    elif base == "x":
        prefix = "0x"
        base = 16
    else:
        prefix = "0b"
        base = 2
    return sign + prefix + val, base


def imm_mem_instruction(match):
    val = match.group(7)
    if val is None:
        return [match.string]
    raw_imm, base = rebuild_immediate(match)
    imm = int(raw_imm, base)
    least, most = split_immediate(imm)
    s1 = match.group(12)
    if s1 is None:
        instruction = match.group(1)
        if instruction == "la":
            instruction = f"addi x{match.group(2)}, x{match.group(2)}, {least}"
        else:
            instruction = f"{match.group(1)} x{match.group(2)}, {least}(x{match.group(2)})"
        return [f"auipc x{match.group(2)}, {most}",
                instruction]
    return [f"auipc x{s1}, {most}",
            f"{match.group(1)} x{match.group(2)}, {least}(x{s1})"]


def load_imm(match):
    raw_imm, base = rebuild_immediate(match)
    imm = int(raw_imm, base)
    bin_imm = np.binary_repr(imm)
    if len(bin_imm) <= 12:
        return [f"addi x{match.group(2)}, x0, {imm}"]
    least, most = split_immediate(imm)
    return [f"lui x{match.group(2)}, {most}",
            f"addi x{match.group(2)}, x{match.group(2)}, {least}"]


def call_function(match):
    raw_imm, base = rebuild_immediate(match)
    imm = int(raw_imm, base)
    bin_imm = np.binary_repr(imm)
    if len(bin_imm) <= 21:
        return [f"jal x1, {imm}"]
    least, most = split_immediate(imm)
    return [f"auipc x1, {most}",
            f"jalr x1, x1, {least}"]


pseudo_translate = {
    "seqz": lambda match: [f"sltiu x{match.group(2)}, x{match.group(4)}, 1"],
    "snez": lambda match: [f"sltu x{match.group(2)}, x0, x{match.group(4)}"],
    "sltz": lambda match: [f"slt x{match.group(2)}, x{match.group(4)}, x0"],
    "snez": lambda match: [f"slt x{match.group(2)}, x0, x{match.group(4)}"],
    "neg":  lambda match: [f"sub x{match.group(2)}, x0, x{match.group(4)}"],
    "not":  lambda match: [f"xori x{match.group(2)}, x{match.group(4)}, -1"],
    "add":  lambda match: [match.string if match.group(7) is None
                           else f"addi x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "slt":  lambda match: [match.string if match.group(7) is None
                           else f"slti x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "sltu": lambda match: [match.string if match.group(7) is None
                           else f"sltiu x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "and":  lambda match: [match.string if match.group(7) is None
                           else f"andi x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "or":   lambda match: [match.string if match.group(7) is None
                           else f"ori x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "xor":  lambda match: [match.string if match.group(7) is None
                           else f"xori x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "sll":  lambda match: [match.string if match.group(7) is None
                           else f"slli x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "srl":  lambda match: [match.string if match.group(7) is None
                           else f"srli x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "sra":  lambda match: [match.string if match.group(7) is None
                           else f"srai x{match.group(2)}, x{match.group(3)}, {match.group(7)}"],
    "lb":   imm_mem_instruction,
    "lh":   imm_mem_instruction,
    "lw":   imm_mem_instruction,
    "sb":   imm_mem_instruction,
    "sh":   imm_mem_instruction,
    "sw":   imm_mem_instruction,
    "mv":   lambda match: [f"addi x{match.group(2)}, x{match.group(4)}, 0"],
    "li":   load_imm,
    "la":   imm_mem_instruction,
    "ble":  lambda match: [f"bge x{match.group(3)}, x{match.group(2)}, {rebuild_immediate(match)[0]}"],
    "bgt":  lambda match: [f"blt x{match.group(3)}, x{match.group(2)}, {rebuild_immediate(match)[0]}"],
    "bleu": lambda match: [f"bgeu x{match.group(3)}, x{match.group(2)}, {rebuild_immediate(match)[0]}"],
    "bgtu": lambda match: [f"bltu x{match.group(3)}, x{match.group(2)}, {rebuild_immediate(match)[0]}"],
    "beqz": lambda match: [f"beq x{match.group(2)}, x0, {rebuild_immediate(match)[0]}"],
    "bnez": lambda match: [f"bne x{match.group(2)}, x0, {rebuild_immediate(match)[0]}"],
    "bltz": lambda match: [f"blt x{match.group(2)}, x0, {rebuild_immediate(match)[0]}"],
    "bgez": lambda match: [f"bge x{match.group(2)}, x0, {rebuild_immediate(match)[0]}"],
    "blez": lambda match: [f"bge x0, x{match.group(2)}, {rebuild_immediate(match)[0]}"],
    "bgtz": lambda match: [f"blt x0, x{match.group(2)}, {rebuild_immediate(match)[0]}"],
    "jalr": lambda match: [match.string if match.group(3) is not None
                           else f"jalr x1, x{match.group(2)}, 0"],
    "jal":  lambda match: [match.string if match.group(2) is not None
                           else f"jal x1, {rebuild_immediate(match)}"],
    "call": call_function,
    "ret":  lambda match: ["jalr x0, x1, 0"],
    "j":  lambda match: [f"jal x0, {rebuild_immediate(match)[0]}"],
    "jr":  lambda match: [f"jalr x0, x{match.group(2)}, 0"],
    "nop":  lambda match: [f"addi x0, x0, 0"]
    }


def getInstructionSet(base: str, extensions: List[str] = []) -> Dict[str, Dict[str, Any]]:
    instruction_set = rv_instructions[base].copy()
    for ext in extensions:
        instruction_set.update(rv_instructions[ext])
    return instruction_set


def getReversedSet(base: str, extensions: List[str] = []) -> Dict[str, Dict[str, Any]]:
    instruction_set = getInstructionSet(base, extensions)
    reversed_set = {}
    for instruction, data in instruction_set.items():
        opcode = data["op"]
        if opcode not in reversed_set:
            reversed_set[opcode] = (data["type"], instruction)
        if "func3" in data:
            func3 = data["func3"]
            if not isinstance(reversed_set[opcode][1], dict):
                reversed_set[opcode] = (data["type"], {func3: instruction})
            elif func3 not in reversed_set[opcode][1]:
                reversed_set[opcode][1][func3] = instruction
            if "func7" in data:
                func7 = data["func7"]
                if not isinstance(reversed_set[opcode][1][func3], dict):
                    reversed_set[opcode][1][func3] = {func7: instruction}
                elif func7 not in reversed_set[opcode][1][func3]:
                    reversed_set[opcode][1][func3][func7] = instruction
                else:
                    raise ValueError("Duplicated operation!")
    return (reversed_set, instruction_set["lw"]["op"])
