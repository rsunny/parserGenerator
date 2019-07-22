import sys
from src import classes
from src import bitPack


def build_and_check_matrix(non_terminals, terminals, rules):
    matrix = dict()
    lts, rts = build_terminal_sets(non_terminals, terminals, rules)

    # Initialize precedence matrix.
    non_operator = []
    for i in terminals:
        matrix[i] = dict()
        for j in terminals:
            matrix[i][j] = dict()
            matrix[i][j]['='] = []
            matrix[i][j]['>'] = []
            matrix[i][j]['<'] = []

    for rule in rules:
        # Check digrams.
        rhs = rule.rhs
        for i in range(0, len(rhs) - 1):
            tok1 = rhs[i]
            tok2 = rhs[i + 1]
            if (tok1 in terminals) and (tok2 in terminals):
                matrix[tok1][tok2]['='].append(classes.Conflict(rule, i, i + 1))
            elif (tok1 in non_terminals) and (tok2 in terminals):
                for tok in rts[tok1]:
                    matrix[tok][tok2]['>'].append(classes.Conflict(rule, i, i + 1))
            elif (tok1 in terminals) and (tok2 in non_terminals):
                for tok in lts[tok2]:
                    matrix[tok1][tok]['<'].append(classes.Conflict(rule, i, i + 1))
            else:
                non_operator.append(classes.Conflict(rule, i, i + 1))

        # Check trigrams.
        for i in range(0, len(rhs) - 1):
            tok1 = rhs[i]
            tok2 = rhs[i + 1]
            tok3 = rhs[i + 2]
            if (tok1 in terminals) and (tok2 in non_terminals) and (tok3 in terminals):
                matrix[tok1][tok3]['='].append(classes.Conflict(rule, i, i + 2))

    for j in terminals:
        if j != '__TERM':
            matrix['__TERM'][j]['<'].append(classes.Conflict(rules[0], 0, 0))
            matrix[j]['__TERM']['>'].append(classes.Conflict(rules[0], 0, 0))

    matrix['__TERM']['__TERM']['='].append(classes.Conflict(rules[0], 0, 0))

    # Check matrix.
    conflict_error = False
    if len(non_operator) > 0:
        conflict_error = True
        print("\33[1;31mERROR\33[0m: The following rules violate the operator precedence form: no two non-terminals "
              "may be adjacent.")
        i = 0
        for con in non_operator:
            sys.stdout.write("%2d: %s\n" % (i, con.to_string()))
            i += 1

    for i in terminals:
        for j in terminals:
            conflicts = dict()
            if len(matrix[i][j]['=']) > 0:
                conflicts['='] = matrix[i][j]['=']
            if len(matrix[i][j]['>']) > 0:
                conflicts['>'] = matrix[i][j]['>']
            if len(matrix[i][j]['<']) > 0:
                conflicts['<'] = matrix[i][j]['<']
            if len(conflicts) > 1:
                conflict_error = True
                print("\33[1;31mERROR\33[0m: Terminals %s and %s have conflicting relations:" % (i, j))
                for prec in conflicts:
                    print("  \33[1;34m%s\33[0m:" % prec)
                    for con in conflicts[prec]:
                        print("    %s" % con.toString())
    return matrix, conflict_error


def build_terminal_sets(non_terminals, terminals, rules):
    lts = dict()
    rts = dict()

    # Initialize terminal sets.
    for non_terminal in non_terminals:
        lts[non_terminal] = set()
        rts[non_terminal] = set()

    # Direct terminals.
    for rule in rules:
        found = False
        i = 0
        while not found and i < len(rule.rhs):
            token = rule.rhs[i]
            if token in terminals:
                lts[rule.lhs].add(token)
                found = True
            i += 1
        i = len(rule.rhs) - 1
        found = False
        while not found and i >= 0:
            token = rule.rhs[i]
            if token in terminals:
                rts[rule.lhs].add(token)
                found = True
            i -= 1

    # Indirect terminals.
    modified = True
    while modified:
        modified = False
        for rule in rules:
            lhs = rule.lhs
            rhs = rule.rhs
            token = rhs[0]
            if token in non_terminals:
                for ttoken in lts[token]:
                    if ttoken not in lts[lhs]:
                        lts[lhs].add(ttoken)
                        modified = True
            token = rhs[len(rhs) - 1]
            if token in non_terminals:
                for ttoken in rts[token]:
                    if ttoken not in rts[lhs]:
                        rts[lhs].add(ttoken)
                        modified = True
    return lts, rts


def to_real_matrix(matrix, terminals):
    real_matrix = dict()
    for i in terminals:
        real_matrix[i] = dict()
        for j in terminals:
            real_matrix[i][j] = 'ND'

    for i in terminals:
        for j in terminals:
            if len(matrix[i][j]['=']) > 0:
                real_matrix[i][j] = '='
            elif len(matrix[i][j]['>']) > 0:
                real_matrix[i][j] = '>'
            elif len(matrix[i][j]['<']) > 0:
                real_matrix[i][j] = '<'
            else:
                real_matrix[i][j] = 'ND'
    return real_matrix


def to_int_matrix(real_matrix, terminals):
    if len(terminals) % 4 == 0:
        row_len = len(terminals) / 4
    else:
        row_len = len(terminals) / 4 + 1

    int_matrix = [0] * int(row_len) * len(terminals)
    for i in range(0, len(terminals)):
        for j in range(0, len(terminals)):
            bitPack.write_precedence(int_matrix, i, j, real_matrix[terminals[i]][terminals[j]], row_len)
    return int_matrix, row_len
