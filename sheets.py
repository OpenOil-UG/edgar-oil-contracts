'''
handle interaction with
'''

try:
    from doh.private import GUSER, GPS
except ImportError:
    GUSER = 'username@google.com'
    GPS = 'yourpassw.rd'

import argparse
import barn
import codecs
import glob
import gspread
import nltk
import os
from util import pdftext
import logging
logging.basicConfig(level=logging.INFO)

def _auth():
    global CONN
    CONN = gspread.login(GUSER,GPS)

_auth()


SHEETS = {
    'edgar_possible_contracts': '1KzTj6GzRrxhsBDCiW_k9toCj5ekkK4PcPpzWNsu4ZlI',
    'mining_contracts': '1jhEUfBaU8MmbSVDVrA8tEB-1-rypQcF78HzAw1ir1v0',
    }


def known_primary_contracts():
    '''
    '''
    pass

def inspected_rows():
    '''
    generate an iterable containing (filename, edgarpath, exhibitnumber)
    for every row that has been inspected
    '''
    book = CONN.open_by_key(SHEETS['edgar_possible_contracts'])
    sheet = book.sheet1
    # XXX needs error-handling; google taunts us with quasirandom reauthentication
    for rownum in range(2, sheet.row_count):
        row = sheet.row_values(rownum)
        if (len(row) < 4) or row[4] is None: # this row has not been manually inspected
            continue
        yield row
        if 'yes' in row[4].lower(): # primary contract
            pass

def known_contracts():
    book = CONN.open_by_key(SHEETS['mining_contracts'])
    sheet = book.sheet1
    for rownum in range(1, sheet.row_count):
        row = sheet.row_values(rownum)
        if len(row) < 3:
            logging.warn('unable to ingest row %s' % ','.join(row))
            raise StopIteration
        (country, title, url) = row[:3]
        ## possible original url in 4th row
        yield url

def dl_google_doc(url):
    '''ingest text of a google doc, then return the url of a tempfile
    with its text'''
    return url

def preprocess_url(url):
    '''
    handle fake URLs, for resources we don't have on the public web
    return either the correct URL, or None to skip
    '''
    ## XXX: this should be moved onto S3
    if 'docs.google.com' in url:
        # I'm manually downloading google-stored urls for now
        return None
    url = url.replace('RC_CONTRACTS/', '/data/rc_contracts/raw/')
    return url
        
def store_known_contracts(outdir):
    coll = barn.open_collection('knowncontracts', 'file', path=outdir)
    for url in glob.glob('/data/drivelicenses/*'):
        print('ingesting %s' % url)
        res = coll.ingest(url)

    for url in known_contracts():
        url = preprocess_url(url)
        if url is None:
            print('skipping %s' % url)
            continue
        print('ingesting %s' % url)
        res = coll.ingest(url)
    print('done')

# XXX write these!!!
def extracthtml(txt):
    return nltk.clean_html(txt)

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
        with codecs.open(outfile, 'w', 'utf-8') as outf:
            outf.write(text)
    return coll


if __name__ == '__main__':
    # generate a watershed list
    parser = argparse.ArgumentParser()
    parser.add_argument('--barndir', default = '/tmp/contract_barn', help="where to download the unprocessed versions of our list of positive contracts")
    parser.add_argument('--posdir', default = '/tmp/contract_positive', help="where to put the extracted text of all the ")
    args = parser.parse_args()
    for dirname in (args.barndir, args.posdir):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    store_known_contracts(args.barndir)
    store_contract_text(args.barndir, args.posdir)
