#!/bin/bash

import re

if __name__ == "__main__":
    re_dat = re.compile('.*STATE="([A-Za-z ]*)".*')
    dat_file = open('ENNTT/nonnatives.dat', 'r')
    tok_file = open('ENNTT/nonnatives.tok', 'r')

    languages = {}

    for dat, tok in zip(dat_file.readlines(), tok_file.readlines()):
        print dat
        language = re_dat.match(dat).group(1)
        if language in languages:
            languages[language].append(tok)
        else:
            languages[language] = [tok]
    dat_file.close()
    tok_file.close()

    for language in languages:
        print(language)
        f = open('ENNTT/%s-proc.tok' % language, 'w')
        f.writelines(languages[language])
        f.close()
