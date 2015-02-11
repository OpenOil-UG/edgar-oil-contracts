'''
Given the filepath of a local edgar-download, go back to the url of the edgar filing
'''
import re
import sys

def goback(_fn):
    #fn = '111270610-K_2010-09-28_0001062993-10-003164.txt_extracted_4.txt'
    fn = _fn.strip('"').split('/')[-1]
    cik, rest = re.match('(\d+)(.*)', fn).groups()
    exhibit_num = re.search('(\d+).txt$', fn).group(1)
    filenum = re.search('_([\d\-]+).txt_extracted_', fn).group(1)
    filenum_short = ''.join(filenum.split('-'))
    url = 'http://www.sec.gov/Archives/edgar/data/%s/%s/%s-index.htm' % (cik, filenum_short, filenum)
    return _fn.strip(), url, exhibit_num


if __name__ == '__main__':
    for line in sys.stdin:
        print(','.join(goback(line)))
