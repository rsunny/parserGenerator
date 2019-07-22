import sys
import re
from src import classes


def get_axiom(input_lines, line_index):
    axiom = ""
    for input_line in input_lines[line_index:]:
        line_index += 1
        if input_line == "\n":
            continue
        if re.match("%axiom", input_line):
            line_split = input_line.split()
            if axiom == "":
                axiom = line_split[2]
            else:
                print("Only one axiom is allowed: old %s, new %s" % (axiom, line_split[2]))
        if re.match("%%", input_line):
            break
        if axiom == "":
            print("The axiom must be defined.")
            sys.exit(-1)
    return axiom, line_index


def get_rules(inp):
    rules = []
    i = 0
    while i < len(inp):
        # LHS : RHS [RHS]* [{.}] [| RHS [RHS]* [{.}]] ;
        current_rule = classes.Rule()
        rules.append(current_rule)
        current_lhs, ch, i = next_token(i, inp)
        current_rule.lhs = current_lhs
        ch, i = skip_space(i, inp)
        if ch != ":":
            print("No : after lhs.")
            sys.exit(-1)
        ch, i = next_char(i, inp)
        while ch != ";":
            # RHS [RHS]* [{.}]
            ch, i = skip_space(i, inp)
            while ch.isalpha() or ch.isdigit():
                token, ch, i = next_token(i, inp)
                current_rule.rhs.append(token)
                ch, i = skip_space(i, inp)
            if ch == "{":
                # {.}
                brace_balance = 1
                current_rule.text = "{"
                ch, i = next_char(i, inp)
                while brace_balance != 0:
                    current_rule.text += ch
                    if ch == "}":
                        brace_balance -= 1
                    if ch == "{":
                        brace_balance += 1
                    ch, i = next_char(i, inp)
                ch, i = skip_space(i, inp)
            if ch == "|":
                current_rule = classes.Rule()
                rules.append(current_rule)
                current_rule.lhs = current_lhs
                ch, i = next_char(i, inp)
                ch, i = skip_space(i, inp)
        ch, i = next_char(i, inp)
        ch, i = skip_space(i, inp)
    if len(rules) == 0:
        print("Grammar has no rules.")
        sys.exit(-1)
    return rules


def next_char(index, input_rules):
    index += 1
    if index >= len(input_rules):
        return "", index
    return input_rules[index], index


def skip_space(index, input_rules):
    if index >= len(input_rules):
        return "", index
    ch = input_rules[index]
    if ch == "2":
        print(input_rules[index: (index + 20)])
    if ch == "/" and input_rules[index + 1] == "*":
        comment = True
    else:
        comment = False
    while ch.isspace() or comment:
        ch, index = next_char(index, input_rules)
        if ch == "/" and input_rules[index + 1] == "*":
            comment = True
        if input_rules[index - 1] == "/" and input_rules[index - 2] == "*":
            comment = False
        if ch == "":
            break
    return ch, index


def next_token(index, input_rules):
    if index >= len(input_rules):
        return "EOF", "", index
    ch, index = skip_space(index, input_rules)
    if ch == "":
        return "EOF", "", index
    if not ch.isalpha():
        print("Token must start with a letter.")
        sys.exit(-1)
    token = ""
    while ch.isalpha() or (ch in "_-") or ch.isdigit():
        token += ch
        ch, index = next_char(index, input_rules)
    return token, ch, index
