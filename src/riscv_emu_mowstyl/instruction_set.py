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
