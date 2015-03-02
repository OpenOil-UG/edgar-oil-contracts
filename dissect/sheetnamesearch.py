'''
Sheetnamesearch

Prepare names for working on the searches
'''

import re
import tempfile

from dissect import sheets



def simplify_company_name(name):
    '''
    create a search term for a company:
     - strip off ltd, sarl etc
     - lowercase
     - short names get wrapped in word-boundary searches
     - very short names get skipped (create a non-matching regex)
    '''
    corptypes = re.compile(r'\b(limited|ltd|inc|sarl|plc|gmbh)\b', re.I)
    name = name.lower().strip() # XXX probably want the standard normalizer here?
    subbed = corptypes.sub('', name)
    # remove chars with regex meaning
    subbed = re.escape(subbed)
    if len(subbed) < 4:
        return r'.^'
    if len(subbed) < 8:
        return r'\b%s\b' % subbed
    return subbed

def get_search_sheet():
    book = sheets.CONN.open_by_key(sheets.SHEETS['reporting_companies'])
    return book.worksheet("Company Searches")

def names_searchable(rowcount = None):
    sheet = get_search_sheet()
    
    # supplying rowcount is just an efficiency hack
    # to stop gspread working through hundreds of blank lines
    rowcount = rowcount or sheet.row_count
    source_cells = sheet.range('A2:A%s' % rowcount)
    output_cells = sheet.range('B2:B%s' % rowcount)
    manual_cells = sheet.range('C2:C%s' % rowcount)
    for (incell, outcell, manualcell) in zip(source_cells, output_cells, manual_cells):
        outcell.value = manualcell.value or simplify_company_name(incell.value)
    sheet.update_cells(output_cells)
    return sheet

def searchterm_file():
    '''
    assumes names_searchable has already been run
    '''
    sheet = get_search_sheet()
    with tempfile.NamedTemporaryFile(delete=False) as tfile:
        cells = sheet.range('B2:B%s' % sheet.row_count)
        lines = [x.value + u'\n' for x in cells if x.value]
        lines = [x.encode('utf-8') for x in lines]
        tfile.writelines(lines)
    return tfile.name


if __name__ == '__main__':
    names_searchable()
    tfn = searchterm_file()
    print(tfn)
