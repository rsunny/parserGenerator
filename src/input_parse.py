import argparse
import re
import sys
from src import scanner


def parse_commandline_args():
    parser = argparse.ArgumentParser(description='PAPAGENO : the Parallel Parser Generator')
    parser.add_argument('--verbose'   ,'-v', metavar='verb', help='Verbosity level [0-2]', default=0, type=int)
    parser.add_argument('--inputfile' ,'-i', metavar='inputfile', help='Grammar description file', required=True)
    parser.add_argument('--out_header', metavar='header_outpath', help='Location where the output header files should '
                                                                       'be generated. Defaults to ./include/ in the '
                                                                       'calling path', default='./include/')
    parser.add_argument('--out_core', metavar='source_outpath', help='Location where the output C files should be '
                                                                     'generated. Defaults to ./lib/ in the calling '
                                                                     'path', default='./lib/')
    parser.add_argument('--recombination', metavar='recombination', help='String chunk recombination strategy: choose '
                                                                         'between single and log. Defaults to single',
                        default='SINGLE')
    parser.add_argument('--prealloc_stack', metavar='prealloc_stack', help='Preallocated number of symbols for buffered'
                                                                           ' parsing stack. Defaults to 1024',
                        default=1024, type=int)
    parser.add_argument('--token_avg_size', metavar='token_avg_size', help='Size, in bytes of the average token. '
                                                                           'Default is 5 bytes', default='5.0')
    parser.add_argument('--cache_line_size', metavar='cache_line_size', help='Size, in bytes of cache line. Default is '
                                                                             '64 bytes', default=64, type=int)
    return parser.parse_args()


def parse_grammar_description(args):
    input_file = open(args.inputfile, "r")
    input_lines = input_file.readlines()

    # Parse C preamble.
    line_index = 0
    c_preamble = ""
    for input_line in input_lines:
        if re.match("%nonterminal", input_line):
            break
        if re.match("%%", input_line):
            line_index += 1
            break
        c_preamble += input_line
        line_index += 1

    if args.verbose == 1:
        print("C preamble:")
        print(c_preamble)

    # Parse axiom.
    axiom, line_index = scanner.get_axiom(input_lines, line_index)

    # Parse reduction rules and semantic functions.
    inp = ''.join(input_lines[line_index:])
    rules = scanner.get_rules(inp)
    # fill each rule with an index
    for index in range(0, len(rules)):
        rule = rules[index]
        rule.index = index
    if args.verbose == 2:
        print("Rules:")
        for index in range(0, len(rules)):
            rule = rules[index]
            sys.stdout.write("%2d:%s\n" % (index, rule.toString()))
    return rules, axiom, c_preamble
