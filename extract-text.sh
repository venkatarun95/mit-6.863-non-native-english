#!/bin/bash

set -u

datadir=fce/fce-released-dataset/dataset
outdir=fce-extracted

# if [[ -d $outdir ]]; then
#     trash $outdir
# fi
# mkdir $outdir

# Create one file for each language. The file contains the list of all errors
# made by learners
echo "Compiling by language"
# for file in $datadir/*/*.xml; do
#     # The native language of the learner
#     language=`head -n 10 $file | sed -n 's/.*\<language\>\(.*\)\<\/language\>.*/\1/p'`
#     cat $file | sed -n 's/type="\([A-Z]*\)"/(( \1 ))/gp' | grep -o '(( [A-Z]* ))' | grep -o '[A-Z]\+' >>$outdir/$language-errors-only
#     grep '<p>.*</p>' $file >>$outdir/$language-with-tags
#     #cat $outdir/$language-with-tags | sed 's/\<[^>]*\>/ /gp' >>$outdir/$language-without-tags
# done

echo "Compiling by error type"
cat $outdir/*-with-tags >/tmp/extract-text-all-errs
trash $outdir/byerr-*
while read line; do
    echo $line | grep -o 'type="[A-Z]*"' | grep -o '[A-Z][A-Z]*' >/tmp/extract-text-err-types
    while read error; do
        echo $line >>$outdir/byerr-$error
        line=`echo $line | sed 's/<p>\(.*\)<\/p>/\1/'`
        for i in 1 2 3; do
            line=`echo $line | sed 's/<NS type="[A-Z]*"><i>\([^<]*\)<\/i><c>[^<]*<\/c><\/NS>/\1/gp' | sed 's/<NS type="[A-Z]*"><c>[a-zA-Z ]*<\/c><\/NS>//gp' | sed 's/<NS type="[A-Z]*"><i>\([a-zA-Z ]*\)<\/i><\/NS>/\1/gp' | uniq >>$outdir/byerr-$error-orig`
        done
    done </tmp/extract-text-err-types
done </tmp/extract-text-all-errs

exit

# cmd=""; for err in "AGD CD FD MD RD UD"; do cmd="$cmd $outdir/byerr-$err-orig" done; echo $cmd
# fce-extracted/byerr-AGD-orig fce-extracted/byerr-CD-orig fce-extracted/byerr-FD-orig fce-extracted/byerr-MD-orig fce-extracted/byerr-RD-orig fce-extracted/byerr-UD-orig

# Count the number of each type of error made by learners of each language
for language_file in $outdir/*; do
    cat $language_file | sort | uniq -c >$language_file-errcnt
done

# List all error types encountered
cat ErrorTypes/*-errcnt | grep -o '[A-Z]\+' | sort | uniq >$outdir/all-error-types

# For each error type, list for each language, the fraction of errors that
# constitute that type
echo "Compiling by error type"
while read err_type; do
    echo $err_type
    for lang_file in $outdir/*-errcnt; do
        # Total number of all errors in this language
        tot_errs=`awk '{tot+=$1} END{print tot}' $lang_file`
        # Number of errors of this type in this language
        errs=`grep " $err_type$" $lang_file | grep -o '[0-9]\+'`
        if [[ $errs == "" ]]; then errs=0; fi
        language=`echo $lang_file | sed 's/.*\/\([A-Za-z]*\)-.*/\1/'`
        echo $language `awk -v a=$errs -v b=$tot_errs 'BEGIN{print a/b}'` $errs $tot_errs >>$outdir/err_type-$err_type
    done
done <$outdir/all-error-types
