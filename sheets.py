'''
handle interaction with
'''

try:
    from doh.private import GUSER, GPS
except ImportError:
    GUSER = 'username@google.com'
    GPS = 'yourpassw.rd'

import barn
import gspread

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
        (country, title, url) = row[:3]
        ## possible original url in 4th row
        yield url

def store_known_contracts(outdir):
    coll = barn.open_collection('knowncontracts', 'file', path=outdir)
    for url in known_contracts():
        print('ingesting %s' % url)
        res = coll.ingest(url)
    print('done')

# XXX write these!!!
def extracthtml(txt):
    return txt

def extractpdf(pdf):
    return pdf


extractors = {
    'pdf': extractpdf,
    'html': extracthtml,
    'htm': extracthtml,
    'txt' : lambda x: x,
    'raw': lambda x: ''
    }

def store_contract_text(barndir, txtdir):
    coll = barn.open_collection('knowncontracts', 'file', path=barndir)
    for pkg in coll:
        extension = pkg.source.name.rsplit('.')[-1].lower()
        # fail fast if we hit an unknown filetype -- better than producing junk
        extractor = extractors[extension]
        text = extractor(pkg.source.data())
        outfile = '%s/%s.txt' % (txtdir, pkg.id)
        open(outfile, 'w').write(text)
        

        # here's some 
    return coll

