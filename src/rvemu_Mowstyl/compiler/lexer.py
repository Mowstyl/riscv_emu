#comment_regex = r"(?<!\\)(?:#|(?:\/\/))"
valid_escapes = "abefnrtv\\'\"?"
valid_octal = "01234567"
valid_hex = "0123456789abcdefABCDEF"
valid_operations = {
    "||": 12,
    "&&": 11,
    "|":  10,
    "^":   9,
    "&":   8,
    "==":  7,
    "!=":  7,
    "<":   6,
    "<=":  6,
    ">":   6,
    ">=":  6,
    "<<":  5,
    ">>":  5,
    "+":   4,
    "-":   4,
    "*":   3,
    "/":   3,
    "%":   3,
    "!":   2,
    "~":   2
    }
first_op = {operator[0] for operator in valid_operations}
second_op = {operator[1] for operator in valid_operations if len(operator) > 1}
op_symbols = first_op & second_op


def tokenize_file(file_name: str) -> List[List[str]]:
    all_tokens = []
    i = 1
    in_comment = False
    with open(file_name, 'r') as file:
        for line in file:
            tokens, errored, in_comment = tokenize(line, file_name, i, in_comment)
            if tokens is not None and len(tokens[1]) > 0:
                all_tokens.append(tokens)
            i += 1
    if in_comment:
        print(f"[WARNING] Unclosed multi-line comment")
    if errored:
        all_tokens = None
    return all_tokens


def tokenize(line: str, filename: str, number: int, in_comment: bool) -> Tuple[List[Str], bool, bool]:
    tokens = []
    errored = False
    escaping = False
    in_string = False
    parsing_hex = False
    parsing_octal = False
    escaped_char = ""
    last_char = None
    has_tag = False
    current = ""

    for index, character in enumerate(line):
        # -----------------------------
        # Multiline comment
        # -----------------------------
        if in_comment:
            if character == "/" and last_char == "*":  # We find a / preceded by an *
                in_comment = False
                last_char = None
            else:  # We find an *
                last_char = character
            continue

        # -----------------------------
        # Inside string
        # -----------------------------
        if in_string:
            # If previous escape character
            if escaping:
                if parsing_hex:
                    if character in valid_hex:
                        escaped_char += character
                        continue
                    else:
                        parsing_hex = False
                    if not parsing_hex:
                        current += chr(int(escaped_char, 16))
                elif parsing_octal:
                    if character in valid_octal:
                        escaped_char += character
                    else:
                        parsing_octal = False
                    if not parsing_octal or len(escaped_char) == 3:
                        current += chr(int(escaped_char, 8))
                        parsing_octal = False
                    else:
                        continue
                elif character in valid_escapes:
                    current += ("\\" + character).encode().decode('unicode_escape')
                elif character == "x":
                    parsing_hex = True
                elif character in valid_octal:
                    parsing_octal = True
                    escaped_char += character
                else:
                    print(f"[WARNING] Unknown escape '\\{character}' at {filename}:{number}:{index}")
                    current += character
                escaping = False
            elif character == "\\":
                escaping = True
            # Check for string end
            elif character == "\"":
                in_string = False
                tokens.append(current)
                current = ""
                character = ""  # Do not append the closing quotes
            current += character
            continue

        # -----------------------------
        # Detect start of string
        # -----------------------------
        if character == "\"":
            in_string = True
            last_char = None
            if current != "":
                tokens.append(current)
                current = ""
            continue

        # -----------------------------
        # Detect single-line comment with hash
        # -----------------------------
        if character == "#":
            if current != "":
                tokens.append(current)
            last_char = None
            break  # The rest of the line is a comment

        # -----------------------------
        # Detect single-line comment with double slash
        # -----------------------------
        if last_char == "/" and character == "/":
            if current != "":
                current = current[:-1]
                if current != "":
                    tokens.append(current)
                    current = ""
            else:
                tokens = tokens[:-1]
            last_char = None
            break

        # -----------------------------
        # Detect multi-line comment
        # -----------------------------
        if last_char == "/" and character == "*":
            if current != "":
                current = current[:-1]
                if current != "":
                    tokens.append(current)
                    current = ""
            else:
                tokens = tokens[:-1]
            in_comment = True
            last_char = None
            continue

        # -----------------------------
        # Whitespace or separators
        # -----------------------------
        if character.isspace() or character in ",:":
            if character == ":":
                if has_tag:
                    print(f"[ERROR] Multiple tags at {filename}:{number}:{index}")
                    errored = True
                elif current == "":
                    print(f"[ERROR] Unexpected '{character}' at {filename}:{number}:{index}")
                    errored = True
                has_tag = True
                current += ":"
            last_char = None
            if current != "":
                tokens.append(current)
                current = ""
            if character == ",":
                tokens.append(",")
            continue

        # -----------------------------
        # Operations
        # -----------------------------
        last_char = character

        if character in op_symbols or character in "()":
            if current != "":
                tokens.append(current)
                current = ""
            elif character in second_op and last_char in first_op:
                composite = last_char + character
                if composite in valid_operations:
                    tokens = tokens[:-1]
                    character = composite
            tokens.append(character)
            continue

        # -----------------------------
        # Regular character
        # -----------------------------
        current += character

    # -----------------------------
    # End of line
    # -----------------------------
    if in_string:
        print(f"[ERROR] Unclosed string at {filename}:{number}")
        errored = True
    if current:
        tokens.append(current)

    return (number, tokens), errored, in_comment
