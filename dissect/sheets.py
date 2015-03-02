'''
handle interaction with google docs
'''

try:
    from doh.private import GUSER, GPS
except ImportError:
    GUSER = 'username@google.com'
    GPS = 'yourpassw.rd'

import gspread
import logging
logging.basicConfig(level=logging.INFO)

def _auth():
    global CONN
    CONN = gspread.login(GUSER,GPS)

_auth()


SHEETS = {
    'edgar_possible_contracts': '1KzTj6GzRrxhsBDCiW_k9toCj5ekkK4PcPpzWNsu4ZlI',
    'mining_contracts': '1jhEUfBaU8MmbSVDVrA8tEB-1-rypQcF78HzAw1ir1v0',
    'reporting_companies': '1TOZfW0RI8K178v5mm_6vZBvILiGfIW5hLSDO5vCDQRM',
    }


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

