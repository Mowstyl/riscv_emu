import re


#comment_regex = r"(?<!\\)(?:#|(?:\/\/))"
valid_escapes = {"a", "b", "e", "f", "n", "r", "t", "v", "\\", "'", '"', "?"}

valid_octal = "01234567"
valid_hex = "0123456789abcdefABCDEF"


def tokenize(line, filename, number, in_comment):
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
            current = current[:-1]  # We remove the last / character
            if current != "":
                tokens.append(current)
            last_char = None
            break

        # -----------------------------
        # Detect multi-line comment
        # -----------------------------
        if last_char == "/" and character == "*":
            current = current[:-1]  # We remove the last / character
            if current != "":
                tokens.append(current)
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
            if character == ",":
                if last_char == ",":
                    print(f"[ERROR] Unexpected '{character}' at {filename}:{number}:{index}")
                    errored = True
            last_char = character
            if current != "":
                tokens.append(current)
                current = ""
            continue

        # -----------------------------
        # Regular character
        # -----------------------------
        current += character
        last_char = character

    # -----------------------------
    # End of line
    # -----------------------------
    if in_string:
        print(f"[ERROR] Unclosed string at {filename}:{number}")
        errored = True
    if current:
        tokens.append(current)

    return tokens, errored, in_comment
