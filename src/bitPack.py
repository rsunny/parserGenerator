import ctypes


def precedence_rel_to_int(rel):
    if rel == '=':
        return 0
    if rel == '>':
        return 1
    if rel == '<':
        return 2
    return 3


def int_to_precedence_rel(rel):
    if rel == 0:
        return "="
    if rel == 1:
        return ">"
    if rel == 2:
        return "<"
    return "ND"


def write_precedence(matrix, i, j, rel, row_len):
    pos = j % 4
    shift = 6 - 2 * pos
    value = matrix[i * row_len + j / 4] & ~(0x03 << shift)
    matrix[i * row_len + j / 4] = value | ((precedence_rel_to_int(rel) & 0x03) << shift)


def get_precedence(matrix, i, j, row_len):
    pos = j % 4
    shift = 6 - 2 * pos
    value = (matrix[i * row_len + j / 4] & (0x03 << shift)) >> shift
    return int_to_precedence_rel(value)


def int_to_token(i, non_terminals, terminals):
    if i < len(non_terminals):
        return non_terminals[i]
    else:
        return terminals[i - len(non_terminals)]


def token_to_int(t, non_terminals, terminals):
    if t in non_terminals:
        return non_terminals.index(t)
    else:
        return terminals.index(t) + len(non_terminals)


def packed_int_to_token(i, non_terminals, terminals):
    non_terminal_bit_mask = 1 << 30
    i = i & ctypes.c_uint32(~non_terminal_bit_mask).value
    return int_to_token(i, non_terminals, terminals)


def token_to_packed_int(t, non_terminals, terminals):
    if t in non_terminals:
        return token_to_int(t, non_terminals, terminals)
    else:
        non_terminal_bit_mask = 1 << 30
        return token_to_int(t, non_terminals, terminals) | ctypes.c_uint32(non_terminal_bit_mask).value
