#!/bin/python

import nltk
import re
import signal
import sys
from nltk.grammar import CFG, PCFG, induce_pcfg, toy_pcfg1, toy_pcfg2

'''
Notes:

 - Cannot distinguish between 'his', 'her', 'their'

 - Don't need very precise grammars (e.g. 'first few flights' vs 'few first
flights') in this application

 - Detecting missing determiners is hard. Also, NLTK does not have a class for
   mass nouns

 - FD isn't context free

 - We did not do spelling errors

'''

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
        res += nltk.word_tokenize(err.lower())
        errs = errs[1:]
    return (res, all_errs)

def get_err_pos(tree, pos=0):
    if type(tree) == nltk.tree.Tree:
        err_start, err_type = None, None
        res = []
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

def classify_gnd_err(gnd_err, pos, toks):
    if gnd_err[0] not in ["AGD", "UD", "FD", "CD"]:
        return True
    if toks[gnd_err[1]].lower() in ["his", "her", "their"] or\
       toks[gnd_err[1]+1].lower() in ["his", "her", "their"]:
        return True
    return None

def classify_det_err(det_err, pos, toks):
    if det_err[0] == "FD":
        if toks[det_err[1]].lower() == "an" and toks[det_err[2]-1][0].lower() in ["a", "e", "i", "o", "u"]:
            return True
        elif toks[det_err[1]].lower() == "a" and toks[det_err[2]-1][0].lower() not in ["a", "e", "i", "o", "u"]:
            return True
    return None

def handle_sigint(signum, frame):
    print("Found: %d, Not found: %d, Extraneous: %d" %
          (num_found, num_not_found, num_extraneous))
    exit(0)


grammar = CFG.fromstring("""
S -> Fallback Err Fallback
S -> Fallback
Fallback -> AllTags Fallback
Fallback ->
S -> AllTags
AllTags -> 'END' | 'QUOT' | '(' | ')' | ',' | '--' | '.' | 'CC' | 'CD' | 'DT' | 'EX' | 'FW' | 'IN' | 'JJ' | 'JJR' | 'JJS' | 'LS' | 'MD' | 'NN' | 'NNP' | 'NNPS' | 'NNS' | 'PDT' | 'POS' | 'PRP' | 'PRP$' | 'RB' | 'RBR' | 'RBS' | 'RP' | 'SYM' | 'TO' | 'UH' | 'VB' | 'VBD' | 'VBG' | 'VBN' | 'VBP' | 'VBZ' | 'WDT' | 'WP' | 'WP$' | 'WRB' | '``' | Det | ':'
Det -> DetPl | DetSg | DetNeut
DetNeut -> 'the' | 'some' | 'another' | 'no' | 'his' | 'her' | 'his/her' | 'any'
DetSg -> 'a' | 'an' | 'this' | 'every' | 'another' | 'that' | 'each' | 'neither'
DetPl -> 'all' | 'both' | 'these' | 'those'
Err -> ErrUD | ErrAGD | ErrFD | ErrAGV

NotNPHead -> 'END' | 'QUOT' | '(' | ')' | ',' | '--' | '.' | 'CC' | 'DT' | 'EX' | 'FW' | 'IN' | 'LS' | 'MD' | 'NN' | 'NNP' | 'NNPS' | 'NNS' | 'PDT' | 'POS' | 'PRP' | 'PRP$' | 'RB' | 'RBR' | 'RBS' | 'RP' | 'SYM' | 'TO' | 'UH' | 'VB' | 'VBD' | 'VBG' | 'VBN' | 'VBP' | 'VBZ' | 'WDT' | 'WP' | 'WP$' | 'WRB' | '``' | ':'

CDList -> 'CD' CDList
CDList ->

JJList -> 'JJ' JJList
JJList -> 'JJR' JJList
JJList -> 'JJS' JJList
JJList ->


ErrAGD -> DetPl JJList 'NN'
ErrAGD -> DetSg JJList CDList JJList 'NNS'

ErrFD -> 'a' AllTags
ErrFD -> 'an' AllTags

ErrUD -> Det JJList 'NNP'
ErrUD -> Det JJList CDList JJList 'NNPS'

""")

"""

DetPlNeut -> DetNeut | DetPl
DetSgNeut -> DetNeut | DetSg
NNPl -> 'NNPS' | 'NNS'
NNSg -> 'NNP' | 'NN'
NPPl -> DetPlNeut JJList CDList JJList NNPl
NPSg -> DetSgNeut JJList CDList JJList NNSg
NPPl -> JJList CDList JJList NNPl
NPSg -> JJList CDList JJList NNSg

ErrAGV -> NNPl 'VBP'
ErrAGV -> NNSg 'VBZ'
"""

# Hard to handle '<missing> place we went to'

parser = nltk.parse.EarleyChartParser(grammar) #ChartParser(grammar)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)

    num_found, num_not_found, num_extraneous = 0, 0, 0
    f = open(sys.argv[1], 'r')
    for line in f.readlines():
        # Process input line
        try:
            line_toks, line_errs = process_line(line)
            orig_line = ' '.join(line_toks)
            if orig_line.find('<') != -1:
                continue

            # Tag and parse line
            pos = nltk.pos_tag(line_toks)
            pos = [process_pos_tag(x) for x in pos]
            pos_str = ' '.join(pos)
            parse = parser.parse(pos)
        except ValueError, UnicodeDecodeError:
            continue
        num_parses = 0

        # Find all errors
        errs = []
        for x in parse:
            e, _ = get_err_pos(x)
            for x in e:
                caught = classify_det_err(x, pos, line_toks)
                if not caught and x not in errs:
                    errs += [x]

        # Find overlap between errors
        errs_matched = []
        for gnd_err in line_errs:
            #if gnd_err[0] in ["AGD", "UD", "AGN", "CQ"]:
            found = False
            for det_err in errs:
                if det_err[1] <= gnd_err[1] and det_err[2] >= gnd_err[1]:
                    found = True
                    if det_err not in errs_matched:
                        # Ignore duplicate errors
                        errs_matched += [det_err]
            if found == False:
                caught = classify_gnd_err(gnd_err, line_toks, pos)
                if caught == None:
                    print("Did not find '%s' error in line at %d:" % (gnd_err[0], gnd_err[1]))
                    print("FALSE-NEGATIVE %s" % line)
                    print(orig_line)
                    print(pos_str)
                    print(errs)
                    num_not_found += 1
            else:
                print("Found '%s' error" % gnd_err[0])
                print(orig_line)
                print(' '.join(line_toks[gnd_err[1]-2:gnd_err[1]+2]))
                num_found += 1
        if len(errs_matched) < len(errs):
            print("Found extraneous error")
            print("FALSE-POSITIVE %s" % line)
            print(orig_line)
            print(pos_str)
            print(line_errs)
            print(errs)
            for e in errs:
                print(' '.join(line_toks[e[1]-2:e[2]+2]))
            print(orig_line)
            num_extraneous += 1

    f.close()
    handle_sigint(None, None)

