#!/bin/bash

if [[ $1 == "run" ]]; then
    for file in ENNTT/*-proc.tok; do
        language=`echo $file | sed 's/ENNTT\/\(.*\)-proc.tok/\1/'`
        echo $language
        python detect-error.py "$file" >ENNTT/detected-$language.log
    done
elif [[ $1 == "graph" ]]; then
    for file in ENNTT/detected-*.log; do
        language=`echo $file | sed 's/ENNTT\/detected-\(.*\).log/\1/'`
        num_err=`grep FALSE-POSITIVE $file | wc -l`
        num_words=`wc -w ENNTT/$language-proc.tok | sed 's/\ *\([0-9]*\)[^0-9]*/\1/'`
        err_rate=`awk "END {print 1.0*$num_err/$num_words;}" /dev/null`
        confidence=`awk -v p=$err_rate -v n=$num_words 'BEGIN{print 2 * sqrt(p*(1-p)/n)}' /dev/null`
        echo $language $num_err $num_words $err_rate $confidence
    done
fi


# Austria 39 2135 0.018267 0.00579644
# Belgium 1205 66526 0.0181132 0.0010341
# Bulgaria 94 6023 0.0156068 0.00319422
# Cyprus 463 35153 0.013171 0.00121613
# Denmark 235 14442 0.016272 0.00210559
# Estonia 930 50184 0.0185318 0.00120405
# Finland 1504 81456 0.018464 0.000943375
# France 540 28210 0.0191421 0.00163165
# Germany 309 16929 0.0182527 0.00205768
# Greece 186 12899 0.0144197 0.00209931
# Hungary 657 37851 0.0173575 0.00134256
# Italy 250 15060 0.0166003 0.00208229
# Latvia 229 13202 0.0173459 0.00227253
# Lithuania 335 17722 0.0189031 0.00204596
# Luxembourg 791 46168 0.0171331 0.00120788
# Malta 544 40109 0.013563 0.00115511
# Netherlands 1164 63612 0.0182984 0.00106281
# Poland 568 35691 0.0159144 0.00132484
# Portugal 1034 53511 0.0193231 0.00119017
# Romania 443 29364 0.0150865 0.00142271
# Slovakia 107 6267 0.0170736 0.00327283
# Slovenia 17 1169 0.0145423 0.00700258
# Spain 965 54272 0.0177808 0.00113455
# Sweden 955 52361 0.0182388 0.00116957
