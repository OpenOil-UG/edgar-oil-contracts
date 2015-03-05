from sheets import CONN, SHEETS
import argparse
import barn
import codecs
import glob
import logging
import os
from util import pdftext
from bs4 import BeautifulSoup


def known_contracts(sheetid):
    book = CONN.open_by_key(sheetid)
    sheet = book.sheet1
    for rownum in range(1, sheet.row_count):
        row = sheet.row_values(rownum)
        if len(row) < 3:
            logging.warn('unable to ingest row %s' % ','.join(row))
            raise StopIteration
        (country, title, url) = row[:3]
        ## possible original url in 4th row
        yield url


def preprocess_url(url):
    '''
    handle fake URLs, for resources we don't have on the public web
    return either the correct URL, or None to skip
    '''
    ## XXX: this should be moved onto S3
    if 'docs.google.com' in url:
        # I'm manually downloading google-stored urls for now
        return None
    #url = url.replace('RC_CONTRACTS/', '/data/rc_contracts/raw/')
    url = url.replace('RC_CONTRACTS/', 's3://sec-mining.openoil.net/rc_contracts/')
    return url
        
def store_known_contracts(args):
    coll = barn.open_collection('knowncontracts', 'file', path=args.barndir)
    
    # XXX warning: special-handling
    for pattern in args.include_text_directory:
        for url in glob.glob(pattern + '/*'):
            print('ingesting %s' % url)
            res = coll.ingest(url)

    for url in known_contracts(args.sheetid):
        url = preprocess_url(url)
        if url is None:
            print('skipping %s' % url)
            continue
        print('ingesting %s' % url)
        res = coll.ingest(url)
    print('done')

def extracthtml(txt):
    return BeautifulSoup(txt).get_text()

def extractpdf(pdf):
    return pdftext.pdfdata2txt(pdf)

def donothing(txt):
    return txt

extractors = {
    'pdf': extractpdf,
    'html': extracthtml,
    'htm': extracthtml,
    'txt' : donothing,
    'raw': donothing,
    }

def store_contract_text(barndir, txtdir):
    coll = barn.open_collection('knowncontracts', 'file', path=barndir)
    for pkg in coll:
        extension = pkg.source.name.rsplit('.')[-1].lower()
        # fail fast if we hit an unknown filetype -- better than producing junk
        extractor = extractors.get(extension, donothing)
        text = extractor(pkg.source.data())
        outfile = '%s/%s.txt' % (txtdir, pkg.id)
        with codecs.open(outfile, 'w', 'utf-8', errors='ignore') as outf:
            outf.write(text)
    return coll

def run(args):
    pos_dir = args.pos_dir[0]
    for dirname in (args.barndir, pos_dir):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    store_known_contracts(args)
    store_contract_text(args.barndir, pos_dir)

def build_parser(parser=None):
    parser = parser or argparse.ArgumentParser()
    parser.add_argument('--barndir', default = '/tmp/contract_barn', help="where to download the unprocessed versions of our list of positive contracts")
    try:
        parser.add_argument('--pos_dir', default = '/tmp/contract_positive', help="where to put the extracted text of all the positive examples")
    except argparse.ArgumentError:
        # we are calling from dissect.py, which already has pos_dir as another option
        pass

    parser.add_argument('--sheetid', default=SHEETS['mining_contracts'],
                        help="ID of a google sheet containing links to documents to be considered positive examples. The links should be in column C, with no header line. If they are not plain text files, you should add special handling in preprocess_url")

    parser.add_argument('--include_text_directory', default=[], action='append',
                        help="Include text files from a directory on this machine. Supply the full path to the directory, which should contain only text files. This option can be given multiple times to include more than one directory")
    return parser

if __name__ == '__main__':
    # generate a watershed list
    parser = build_parser()
    args = parser.parse_args()
    run(args)

