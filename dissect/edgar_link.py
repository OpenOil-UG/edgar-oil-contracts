'''
Given the filepath of a local edgar-download, go back to the url of the edgar filing
'''
import re
import sys

def goback(_fn):
    #fn = '111270610-K_2010-09-28_0001062993-10-003164.txt_extracted_4.txt'
    groups = _fn.strip('"').split('/')
    cik = groups[-2]
    #cik, rest = re.match('(\d+)(.*)', c).groups()
    exhibit_num = re.search('(\d+).txt$', groups[-1]).group(1)
    filenum = re.search('_([\d\-]+).txt_extracted_', groups[-1]).group(1)
    filenum_short = ''.join(filenum.split('-'))
    url = 'http://www.sec.gov/Archives/edgar/data/%s/%s/%s-index.htm' % (cik, filenum_short, filenum)
    human_exhibit_num = str(int(exhibit_num) + 1) # don't make users count from 0
    return _fn.strip(), url, human_exhibit_num

def edgar_from_filepath(_fn):
    return goback(_fn)

if __name__ == '__main__':
    for line in sys.stdin:
        print(','.join(goback(line)))
