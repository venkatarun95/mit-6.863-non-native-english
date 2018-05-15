#!/bin/python

import nltk
import re
import sys
from nltk.grammar import CFG, PCFG, induce_pcfg, toy_pcfg1, toy_pcfg2

def process_pos_tag(tag):
    if tag[1] == 'DT':
        return tag[0].lower()
    if tag[1] == '$':
        return 'END'
    if tag[1] == "''":
        return 'QUOT'
    return tag[1]

re_line = re.compile('<NS type="[A-Z]*">(?:<i>[^<]*</i>)?(?:<c>[^<]*</c>)?(?:[^<]*)?</NS>')
re_err = re.compile('<NS type="([A-Z]*)">(?:<i>([^<]*)</i>)?(<c>[^<]*</c>)?([^<]*)?</NS>')
#re_line = re.compile('<NS type="[A-Z]*">[]</NS>')
def process_line(line):
    split = re_line.split(line)
    errs = re_line.findall(line)
    res = []
    all_errs = []
    for x in split:
        res += nltk.word_tokenize(x)
        if len(errs) == 0:
            assert(x == split[-1])
            break
        e = re_err.match(errs[0]).groups()
        all_errs += [(e[0], len(res))]
        err = ''
        if e[1] != None:
            err += e[1]
        if e[3] != None:
            err += ' ' + e[3]
        res += nltk.word_tokenize(err)
        errs = errs[1:]
    return (res, all_errs)

def get_err_pos(tree, pos=0):
    if type(tree) == nltk.tree.Tree:
        err_start, err_type = None, None
        res = []
        #print(tree.label())
        if tree.label() == "Err":
            err_start = pos
        for subtree in tree:
            errs, pos = get_err_pos(subtree, pos)
            res += errs
            if err_start != None:
                err_type = subtree.label()[3:]
        if err_start != None:
            res += [(err_type, err_start, pos)]
        return (res, pos)
    else:
        return ([], pos+1)

grammar = CFG.fromstring("""
S -> Fallback Err Fallback
S -> Fallback
Fallback -> AllTags Fallback
Fallback ->
S -> AllTags
AllTags -> 'END' | 'QUOT' | '(' | ')' | ',' | '--' | '.' | 'CC' | 'CD' | 'DT' | 'EX' | 'FW' | 'IN' | 'JJ' | 'JJR' | 'JJS' | 'LS' | 'MD' | 'NN' | 'NNP' | 'NNPS' | 'NNS' | 'PDT' | 'POS' | 'PRP' | 'PRP$' | 'RB' | 'RBR' | 'RBS' | 'RP' | 'SYM' | 'TO' | 'UH' | 'VB' | 'VBD' | 'VBG' | 'VBN' | 'VBP' | 'VBZ' | 'WDT' | 'WP' | 'WP$' | 'WRB' | '``' | Det | ':'
Det -> DetPl | DetSg | 'the' | 'some' | 'another' | 'no' | 'his' | 'her' | 'his/her'
DetSg -> 'a' | 'an' | 'this' | 'every' | 'another' | 'that' | 'each' | 'any' | 'neither'
DetPl -> 'all' | 'both' | 'these' | 'those'
Err -> ErrUD | ErrAGD

ErrUD -> Det 'NNP'
ErrUD -> Det 'NNPS'

ErrAGD -> DetPl 'NN'
ErrAGD -> DetSg 'NNS'
""")

# Hard to handle '<missing> place we went to'

parser = nltk.parse.EarleyChartParser(grammar) #ChartParser(grammar)

if __name__ == "__main__":
    f = open(sys.argv[1], 'r')
    for line in f.readlines():
        # Process input line
        line_toks, line_errs = process_line(line)
        orig_line = ' '.join(line_toks)
        if orig_line.find('<') != -1:
            continue

        # Tag and parse line
        pos = nltk.pos_tag(line_toks)
        pos = [process_pos_tag(x) for x in pos]
        pos_str = ' '.join(pos)
        parse = parser.parse(pos)
        num_parses = 0

        # Find all errors
        errs = []
        for x in parse:
            e, _ = get_err_pos(x)
            errs += e

        # Find overlap between errors
        errs_matched = []
        for gnd_err in line_errs:
            if gnd_err[0] in ["AGD", "UD", "AGN"]:
                found = False
                for det_err in errs:
                    if det_err[0] == gnd_err[0] or \
                    (gnd_err[0] == "AGN" and det_err[0] == "AGD"):
                        if det_err[1] <= gnd_err[1] and det_err[2] >= gnd_err[1]:
                            found = True
                            if det_err in errs_matched:
                                print("Warning: Duplicate error")
                            errs_matched += [det_err]
                if found == False and gnd_err != "AGN":
                    print("Did not find '%s' error in line:" % gnd_err[0])
                    print(line)
                    print(pos_str)
                    print(errs)
                else:
                    print("Found '%s' error" % gnd_err[0])
        if len(errs_matched) < len(errs):
            print("Found extraneous errors")
            print(line)
            print(pos_str)
            print(line_errs)
            print(errs)

    f.close()

