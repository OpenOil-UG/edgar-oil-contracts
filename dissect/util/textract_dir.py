'''
run textract on an entire directory
'''

import glob
import os
import textract


def run(dirname, outdir=None):
    outdir = outdir or dirname
    for fn in glob.glob1(dirname, '*'):
        print('processing %s' % fn)
        if fn.endswith('txt'):
            continue
        outfilepath = '%s/%s.txt' % (outdir, fn)
        infilepath = '%s/%s' % (outdir, fn)
        if os.path.exists(outfilepath):
            continue
        try:
            output = textract.process(infilepath, method='tesseract')
        except Exception:
            print('cannot read %s' % infilepath)
            continue
        with open(outfilepath, 'w') as outfh:
            outfh.write(output)
