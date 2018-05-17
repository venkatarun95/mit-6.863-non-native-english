Running the Detector
======================

The code for error detector is present in detect-error.py. It takes one
argument, the name of a file containing lines with sentences/paragraphs. If the
sentences are annotated with errors, it will assess its accuracy. You can run
`python detect-error.py fce-extracted/determiner-error-with-errs` to run the
detector on the ICLE dataset.

If it found an error correctly, it prints that an error was found along with the
location (in terms of number of tokens). Then it prints the original line. 

If the error was not annotated, then it assumes it has a false positive. It
prints 'FALSE-POSITIVE' followed by the original line after which it prints
helpful text. It prints the original line without annotation (orig_line), the
POS tags (pos_str), the list of detected errors (line_errors) and the text at
the location the errors were detected.

If there was a false negative, i.e. the error was annotated, but the detector
didn't find it, it prints FALSE-NEGATIVE, followed by the original line (i.e.
after removing annotations) and all the errors that it did detect.

Note that if the source file is not annotated, all detected errors are
classified as false positives. We should interpret these as detected errors.

Datasets
===========

The ICLE dataset is present in folder fce-extracted. The EUROPARL dataset is
present in the ENNTT folder. Along with the original data, we have included
processed data which are a result of some parsing operations.
`ENNTT/\*-proc.tok` contains sentences uttered by delegates from the respective
countries. `detect-error.py` can be directly used on these to detect errors.
`fce-extracted/byerr-\*` contains sentences that contain each type of error.
`fce-extracted/determiner-error-with-errs`` contains all sentences with
determiner errors. `fce-extracted/<language name>-with-tags` contains
sentences/paragraphs from ESL learners from those languages.
`fce-extracted/<language name>-errors-only` contains the error codes for those
ESL learners.

Scripts
======

The processed files described above were generated from the original dataset
format using the scripts `compile_enntt.py` and `extract-text.sh`.
`test-cases.txt` contains some test cases we were experimenting with.
`bigram.py` contains our code for understanding POS and character ngrams. We
covered these results only briefly in the paper as the results weren't
interesting. `run-detector.sh` is a script that can be run with commands `run`
and `graph` to process the EUROPARL dataset.
