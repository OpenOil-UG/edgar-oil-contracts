'''
Extract text parts from EDGAR filigs
'''

import codecs
import os
from lxml import html
import argparse

def walkdir(filingdir, outdir):
    parser = html.HTMLParser(recover=True)
    for (dirpath, dirnames, filenames) in os.walk(filingdir):
        for filename in filenames:
            if '_extracted_' in filename:
                continue # don't eat our own tail
            print('handling %s' % filename)
            filepath_in = os.path.join(dirpath, filename)
            dirpath_out = dirpath.replace(filingdir, outdir)
            if not os.path.exists(dirpath_out):
                os.makedirs(dirpath_out)
            filepath_out_base = dirpath_out + filename + '_extracted_%s.txt'
            with open(filepath_in) as fin:
                doc = html.fromstring(fin.read(), parser=parser)
                for i, docpart in enumerate(doc.findall('.//document')):
                    outfile = codecs.open(filepath_out_base % i, 'w', 'utf-8')
                    outfile.write(docpart.text_content())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--filingdir", default='/data/filings', help="directory with the raw edgar downloads")
    parser.add_argument("--outdir", default="/data/filings_text", help="where to write the extracted text files")
    args = parser.parse_args()
    walkdir(args.filingdir, args.outdir)
