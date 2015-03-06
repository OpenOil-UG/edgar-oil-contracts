#!/bin/bash


# At one point edgar text extraction was putting text into the root directory
# rather than one dir per company. This command fixes that

BASEDIR=/data/mining/edgar_filings_text

for dname in `find $BASEDIR -mindepth 1 -type d`; do
    mv $dname*txt $dname;
done