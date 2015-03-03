'''
Split a file into chunks, based on a delimiter

roughly equivalent to gnutools' csplit
'''

import sys
import argparse
import re

def filepart(num):
    filename = '%s%03d' % (args.outputfn, num)
    return open(filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--delimiter')
    parser.add_argument('--outputfn', default='/tmp/xxx')
    args = parser.parse_args()

    filenum = 1
    outfh = filepart(filenum)
    for line in sys.stdin:
        if line.match(args.delimiter):
            outfh.close()
            filenum +=1
            outfh = filepart(filenum)
            continue
        else:
            outfh.write(line)
