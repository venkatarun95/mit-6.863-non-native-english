#!/bin/python

import nltk
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

grammar = CFG.fromstring("""
S -> Fallback Err Fallback
S -> Fallback
Fallback -> AllTags Fallback
Fallback ->
S -> AllTags
AllTags -> 'END' | 'QUOT' | '(' | ')' | ',' | '--' | '.' | 'CC' | 'CD' | 'DT' | 'EX' | 'FW' | 'IN' | 'JJ' | 'JJR' | 'JJS' | 'LS' | 'MD' | 'NN' | 'NNP' | 'NNPS' | 'NNS' | 'PDT' | 'POS' | 'PRP' | 'PRP$' | 'RB' | 'RBR' | 'RBS' | 'RP' | 'SYM' | 'TO' | 'UH' | 'VB' | 'VBD' | 'VBG' | 'VBN' | 'VBP' | 'VBZ' | 'WDT' | 'WP' | 'WP$' | 'WRB' | '``' | Det | ':'
Det -> DetPl | DetSg | 'the' | 'some' | 'another' | 'no'
DetSg -> 'a' | 'an' | 'this' | 'every' | 'another' | 'that' | 'each' | 'any' | 'neither'
DetPl -> 'all' | 'both' | 'these' | 'those'

Err -> Det 'NNP'
Err -> Det 'NNPS'
Err -> DetPl 'NN'
Err -> DetSg 'NNS'
""")

# Hard to handle '<missing> place we went to'

parser = nltk.parse.EarleyChartParser(grammar) #ChartParser(grammar)

if __name__ == "__main__":
    f = open(sys.argv[1], 'r')
    for line in f.readlines():
        if line.find('<') != -1:
            continue
        pos = nltk.pos_tag(nltk.word_tokenize(line))
        pos = [process_pos_tag(x) for x in pos]
        parse = parser.parse(pos)
        num_parses = 0
        pos_str = ' '.join(pos)
        for x in parse:
            num_parses += 1
            if num_parses > 1:
                parse = parser.parse(pos)
                # for x in parse:
                #     print(x)
                print(line)
                pos_str = ' '.join(pos)
                #print(pos_str)
                break

        # print(line)
        # print(pos_str)
        # patterns = ["DT NNS"]
        # for pat in patterns:
        #     if pos_str.find(pat) != -1:
        #         print(line)
        #         print(pat, pos)
    f.close()

