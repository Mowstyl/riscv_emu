from collections import OrderedDict
from enum import Enum, auto
from .lexer import valid_operations

import numpy as np
import numpy.typing as npt


def parse_tokens(all_tokens: List[List[str]]):
    num_lines: int = len(all_tokens)
    i: int = 0
    errored: bool = False
    the_end = False
    symbols: Tuple[Set[str], Set[str], Dict[str, Number], Dict[str, Tuple[int, Region]]] = (set(), set(), {}, {})
    # symbols[0]: Global Symbols
    # symbols[1]: External Symbols
    # symbols[2]: Macros  # Maps symbol -> number
    # symbols[3]: Labels  # Maps label -> (direction relative to region start, memory region)
    data: npt.NDArray[np.int8] = None
    rodata: npt.NDArray[np.int8] = None
    bss: npt.NDArray[np.int8] = None
    while i < num_lines:
        line, line_tokens = all_tokens[i]
        num_tokens = len(line_tokens)
        directive = line_tokens[0]
        match directive:
            case ".data":
                if num_tokens > 1:
                    print(f"[ERROR] Unexpected tokens after .data, at line {line}")
                    errored = True
                if data is not None:
                    print(f"[ERROR] Duplicated .data region, at line {line}")
                    errored = True
                data, mem_size, i = data_parser(symbols, Region.DATA, all_tokens, i+1, num_lines)
                errored = (data is None) or errored
            case ".rodata":
                if num_tokens > 1:
                    print(f"[ERROR] Unexpected tokens after .rodata, at line {line}")
                    errored = True
                if rodata is not None:
                    print(f"[ERROR] Duplicated .rodata region, at line {line}")
                    errored = True
                rodata, mem_size, i = data_parser(symbols, Region.RODATA, all_tokens, i+1, num_lines)
                errored = (rodata is None) or errored
            case ".bss":
                if num_tokens > 1:
                    print(f"[ERROR] Unexpected tokens after .bss, at line {line}")
                    errored = True
                if bss is not None:
                    print(f"[ERROR] Duplicated .bss region, at line {line}")
                    errored = True
                bss, mem_size, i = data_parser(symbols, Region.BSS, all_tokens, i+1, num_lines)
                errored = (bss is None) or errored
            case ".text":
                pass
            case ".global":
                errored = global_parser(symbols, line_tokens, num_tokens, line) or errored
            case ".extern":
                errored = extern_parser(symbols, line_tokens, num_tokens, line) or errored
            case ".equ":
                errored = equ_parser(symbols, line_tokens, num_tokens, line) or errored
            case ".end":
                if num_tokens > 1:
                    print(f"[ERROR] Unexpected tokens after .end, at line {line}")
                    errored = True
                if line < num_lines:
                    print(f"[ERROR] Found lines after .end, at line {line}")
                    errored = True
                the_end = True
                break
            case _:
                print(f"[ERROR] Expected a section or symbol access related directive, at line {line}")
                errored = True
        i += 1
    if not the_end:
        print(f"[WARNING] Unexpected EOF. Did you forget .end?")
        errored = True
    #if errored:
    #    return None, None, None
    return symbols[0], symbols[1], symbols[2]


def global_parser(symbols: Tuple[Set[str], Set[str], Dict[str, Number], Dict[str, Tuple[int, Region]]], line_tokens: List[str], num_tokens: int, line: int) -> bool:
    errored = False
    if num_tokens < 2:
        print(f"[ERROR] .global needs symbol, at line {line}")
        errored = True
    elif num_tokens > 2:
        print(f"[ERROR] .global has too many symbols, at line {line}")
        errored = True
    elif line_tokens[1] in symbols[0]:
        print(f"[WARNING] Tag '{line_tokens[1]}' already defined as global, at line {line}")
    elif line_tokens[1] in symbols[1] or line_tokens[1] in symbols[2] or line_tokens[1] in symbols[3]:
        print(f"[ERROR] Symbol '{line_tokens[1]}' is already defined, at line {line}")
        errored = True
    else:
        symbols[0].add(line_tokens[1])
    return errored


def extern_parser(symbols: Tuple[Set[str], Set[str], Dict[str, Number], Dict[str, Tuple[int, Region]]], line_tokens: List[str], num_tokens: int, line: int) -> bool:
    errored = False
    if num_tokens < 2:
        print(f"[ERROR] .extern needs symbol, at line {line}")
        errored = True
    elif num_tokens > 2:
        print(f"[ERROR] .extern has too many symbols, at line {line}")
        errored = True
    elif line_tokens[1] in symbols[1]:
        print(f"[WARNING] Tag '{line_tokens[1]}' already defined as extern, at line {line}")
    elif line_tokens[1] in symbols[0] or line_tokens[1] in symbols[2] or line_tokens[1] in symbols[3]:
        print(f"[ERROR] Symbol '{line_tokens[1]}' is already defined, at line {line}")
        errored = True
    else:
        symbols[1].add(line_tokens[1])
    return errored


def equ_parser(symbols: Tuple[Set[str], Set[str], Dict[str, Number], Dict[str, Tuple[int, Region]]], line_tokens: List[str], num_tokens: int, line: int) -> bool:
    errored = False
    try:
        if line_tokens[2] != ",":
            print(f"[ERROR] .equ needs a comma between the symbol and its value, at line {line}")
            return True
        symbol = line_tokens[1]
        value, _ = number_parser(symbols[2], line_tokens, 3, line)
        if value is None:
            return True
        if symbol in symbols[2]:
            print(f"[WARNING] Overloading value previously assigned to '{symbol}', at line {line}")
        if symbol in symbols[0] or symbol in symbols[1] or symbol in symbols[3]:
            print(f"[ERROR] Symbol '{symbol}' is already defined, at line {line}")
            return True
        symbols[2][symbol] = value
    except IndexError:
        print(f"[ERROR] .equ needs a symbol, a comma and a value, at line {line}")
        errored = True
    return errored


def number_parser(macro_dict: Dict[str, Number], line_tokens: List[str], start: int, line: int) -> Tuple[Number, int]:
    stack = []  # .append + .pop()
    queue = []  # .append + .pop(0)
    expected_value = True

    for i in range(start, len(line_tokens)):
        raw_value = line_tokens[i]
        if expected_value:  # Check for unary operation symbol
            if raw_value in "+-!~":
                match raw_value:
                    case "-":
                        queue.append(-1)
                        raw_value = "*"
                        expected_value = True
                    case "!":
                        queue.append(0)
                        raw_value = "=="
                        expected_value = True
                    case "~":
                        queue.append(~0)
                        raw_value = "^"
                        expected_value = True
                    case _:
                        continue
        value = None
        if raw_value.isnumeric():
            if "." not in raw_value:
                value = int(raw_value)
            else:
                value = float(raw_value)
        if value is None:
            try:
                value = int(raw_value, 16)
            except:
                try:
                    value = int(raw_value, 2)
                except:
                    value = None
        if value is None and raw_value in macro_dict:
            value = macro_dict[raw_value]
        if value is not None:
            if not expected_value:
                print(f"[ERROR] Unexpected value {value} while parsing expression, at line {line}")
                return None, i
            queue.append(value)
            expected_value = False
        elif raw_value in valid_operations:
            if expected_value:
                print(f"[ERROR] Unexpected operator {raw_value} while parsing expression, at line {line}")
                return None, i
            precedence = valid_operations[raw_value]
            while len(stack) > 0 and stack[-1] != "(" and valid_operations[stack[-1]] <= precedence:
                queue.append(stack.pop())
            stack.append(raw_value)
            expected_value = True
        elif raw_value == ",":
            i -= 1
            break
        elif raw_value == "(":
            if not expected_value:
                i -= 1
                break
            stack.append(raw_value)
        elif raw_value == ")":
            while len(stack) > 0 and stack[-1] != "(":
                queue.append(stack.pop())
            if len(stack) == 0:
                print(f"[ERROR] Mismatched parenthesis while parsing expression, at line {line}")
                return None, i
            stack.pop()
        else:
            print(f"[ERROR] Undefined symbol {raw_value}, at line {line}")
            return None, i
    while stack:
        operator = stack.pop()
        if operator == "(":
            print(f"[ERROR] Unclosed parenthesis while parsing expression, at line {line}")
            return None, i
        queue.append(operator)
    return operate_rpn(queue), i


def operate_rpn(rpn: List[str]):
    stack = []
    for token in rpn:
        if token not in valid_operations:
            stack.append(token)
        else:
            right = stack.pop()
            left = stack.pop()

            match token:
                case "||":
                    stack.append(left or right)
                case "&&":
                    stack.append(left and right)
                case "|":
                    stack.append(left | right)
                case "^":
                    stack.append(left ^ right)
                case "&":
                    stack.append(left & right)
                case "==":
                    stack.append(left == right)
                case "!=":
                    stack.append(left != right)
                case "<":
                    stack.append(left < right)
                case "<=":
                    stack.append(left <= right)
                case ">":
                    stack.append(left > right)
                case ">=":
                    stack.append(left >= right)
                case "<<":
                    stack.append(left << right)
                case ">>":
                    stack.append(left >> right)
                case "+":
                    stack.append(left + right)
                case "-":
                    stack.append(left - right)
                case "*":
                    stack.append(left * right)
                case "/":
                    stack.append(left / right)
                case "%":
                    stack.append(left % right)
    return stack.pop()


def number_list_parser(macro_dict: Dict[str, Number], line_tokens: List[str], start: int, line: int) -> List[Number]:
    num_tokens = len(line_tokens)
    all_numbers = []
    while start < num_tokens:
        number, start = number_parser(macro_dict, line_tokens, start, line)
        if number is None:
            return None
        all_numbers.append(number)
        start += 1
        if start >= num_tokens:
            break
        if line_tokens[start] != ",":
            print(f"[ERROR] Expected comma separated values, at line {line}")
            return None
        start += 1
    return all_numbers


def data_parser(symbols: Tuple[Set[str], Set[str], Dict[str, Number], Dict[str, Tuple[int, Region]]], region: Region, all_tokens: List[List[str]], i: int, num_lines: int):
    errored: bool = False
    raw_data = []
    region_size = 0
    data: npt.NDArray[np.int8] = None
    found_label = False
    while i < num_lines:
        line, line_tokens = all_tokens[i]
        num_tokens = len(line_tokens)
        start = 0
        while line_tokens[start][-1] == ":":
            label = line_tokens[start][:-1]
            if label in symbols[0] or label in symbols[1] or label in symbols[2] or label in symbols[3]:
                print(f"[ERROR] Symbol '{label}' is already defined, at line {line}")
                errored = True
            symbols[3][label] = (region_size, region)
            found_label = True
            start += 1
            if num_tokens == 1:
                continue
        directive = line_tokens[start]
        i += 1
        match directive:
            case ".word":
                found_label = False
                if region != Region.DATA and region != Region.RODATA:
                    print(f"[ERROR] .word found outside of .data or .rodata, at line {line}")
                    errored = True
                    continue
                if region_size % 4 != 0:
                    print(f"[ERROR] Misaligned .word, at line {line}")
                    errored = True
                all_numbers = number_list_parser(symbols[2], line_tokens, start + 1, line)
                if all_numbers is None:
                    errored = True
                    continue
                region_size += 4 * len(all_numbers)
                try:
                    raw_data += [np.int32(number).tobytes()[i] for number in all_numbers for i in range(4)]
                except OverflowError:
                    print(f"[ERROR] Number too big for a word, at line {line}")
                    errored = True
            case ".half":
                found_label = False
                if region != Region.DATA and region != Region.RODATA:
                    print(f"[ERROR] .half found outside of .data or .rodata, at line {line}")
                    errored = True
                    continue
                if region_size % 2 != 0:
                    print(f"[ERROR] Misaligned .half, at line {line}")
                    errored = True
                all_numbers = number_list_parser(symbols[2], line_tokens, start + 1, line)
                if all_numbers is None:
                    errored = True
                    continue
                region_size += 2 * len(all_numbers)
                try:
                    raw_data += [np.int16(number).tobytes()[i] for number in all_numbers for i in range(2)]
                except OverflowError:
                    print(f"[ERROR] Number too big for a half, at line {line}")
                    errored = True
            case ".byte":
                found_label = False
                if region != Region.DATA and region != Region.RODATA:
                    print(f"[ERROR] .byte found outside of .data or .rodata, at line {line}")
                    errored = True
                    continue
                all_numbers = number_list_parser(symbols[2], line_tokens, start + 1, line)
                if all_numbers is None:
                    errored = True
                    continue
                region_size += len(all_numbers)
                try:
                    raw_data += [np.int8(number) for number in all_numbers]
                except OverflowError:
                    print(f"[ERROR] Number too big for a byte, at line {line}")
                    errored = True
            case ".zero":
                found_label = False
                size, start = number_parser(symbols[2], line_tokens, start + 1, line)
                if size is None:
                    errored = True
                    continue
                region_size += size
                if region != Region.DATA and region != Region.RODATA:
                    raw_data.append((size, 0))
                else:
                    raw_data += [np.int8(0) for i in range(size)]
                if start + 1 < num_tokens:
                    print(f"[ERROR] Unexpected tokens after value, at line {line}")
                    errored = True
            case ".space":
                found_label = False
                if region != Region.BSS:
                    print(f"[ERROR] .space found outside of .bss, at line {line}")
                    errored = True
                    continue
                size, start = number_parser(symbols[2], line_tokens, start + 1, line)
                if size is None:
                    errored = True
                    continue
                region_size += size
                raw_data.append((size, -1))
                if start + 1 < num_tokens:
                    print(f"[ERROR] Unexpected tokens after value, at line {line}")
                    errored = True
            case ".align":
                if found_label:
                    print(f"[WARNING] .align with label found, at line {line}")
                    found_label = False
                size, start = number_parser(symbols[2], line_tokens, start + 1, line)
                if size is None:
                    errored = True
                    continue
                region_size += size
                if region != Region.DATA and region != Region.RODATA:
                    raw_data.append((size, None))
                else:
                    raw_data += [None for i in range(size)]
                if start + 1 < num_tokens:
                    print(f"[ERROR] Unexpected tokens after value, at line {line}")
                    errored = True
            case ".string":
                remaining = num_tokens - start - 1
                if remaining <= 0:
                    print(f"[ERROR] String not found after .string, at line {line}")
                    errored = True
                    continue
                raw_bytes = line_tokens[start + 1].encode()
                raw_data += [np.int8(byte) for byte in raw_bytes]
                raw_data.append(np.int8(0))  # Add null character \0 at the end
                region_size += len(raw_bytes) + 1
                if remaining > 1:
                    print(f"[ERROR] Unexpected tokens after value, at line {line}")
                    errored = True
            case ".global":
                errored = global_parser(symbols, line_tokens, num_tokens, line) or errored
            case ".extern":
                errored = extern_parser(symbols, line_tokens, num_tokens, line) or errored
            case ".equ":
                errored = equ_parser(symbols, line_tokens, num_tokens, line) or errored
            case _:
                if found_label:
                    print(f"[ERROR] Unexpected {directive} directive after label, at line {line}")
                    errored = True
                i -= 1
                break
        found_label = False
    i -= 1
    if errored:
        #raw_data = None
        region_size = -1
    return raw_data, region_size, i


class Region(Enum):
    DATA = auto()
    RODATA = auto()
    BSS = auto()
    TEXT = auto()
