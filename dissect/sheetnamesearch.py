'''
Sheetnamesearch

Prepare names for working on the searches
'''

import argparse
import re
import tempfile
import json
import codecs

from collections import defaultdict

from dissect import sheets



def simplify_company_name(name):
    '''
    create a search term for a company:
     - strip off ltd, sarl etc
     - lowercase
     - short names get wrapped in word-boundary searches
     - very short names get skipped (create a non-matching regex)
    '''
    corptypes = re.compile(r'\b(limited|ltd|inc|sarl|plc|gmbh|sprl|s\.p\.r\.l)\b', re.I)
    name = name.lower().strip() # XXX probably want the standard normalizer here?
    subbed = corptypes.sub('', name)
    # remove chars with regex meaning
    subbed = re.escape(subbed)
    if len(subbed) < 4:
        return r'.^'
    #if len(subbed) < 8:
    #    return r'\b%s\b' % subbed
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

def searchterm_file(filename):
    '''
    generate file of search terms, one regex per line. return the filename
    assumes names_searchable has already been run
    '''
    sheet = get_search_sheet()
    with open(filename, 'w') as tfile:
        cells = sheet.range('B2:B%s' % sheet.row_count)
        lines = [x.value + u'\n' for x in cells if x.value]
        lines = [x.encode('utf-8') for x in lines]
        tfile.writelines(lines)
    return filename



def reconcile_matches(fn, clear = True):
    '''
    '''
    sheet = get_search_sheet()

    terms = sheet.range('B2:B%s' % sheet.row_count)
    line_numbers = dict(zip([x.value for x in terms], range(2,sheet.row_count+1)))

    match_counts = sheet.range('D2:D%s' % sheet.row_count)
    output_values = sheet.range('E2:E%s' % sheet.row_count)

    if clear:
        for ov in output_values:
            ov.value = ''

    matches = defaultdict(list)
    for line in codecs.open(fn):
        js = json.loads(line)
        url = js['filepath'].replace('/data/sedar', 'https://sedar.openoil.net.s3.amazonaws.com')
        for positive, details in js['positives'].items():
            positive = re.escape(positive) # re-escape
            lineno = line_numbers.get(positive, None)
            if lineno is None:
                print('no lineno for %s' % positive)
                continue

            matches[lineno].append(url)
    output = [', '.join(matches[lineno]) for lineno in range(2,sheet.row_count+1)]
    for lineno in range(2, sheet.row_count+1):
        if matches[lineno] or clear:
            if False and lineno > len(output_values):
                print('skipping silly line number')
                continue
            output_values[lineno-2].value = ', '.join(matches[lineno])
            match_counts[lineno-2].value = len(matches[lineno])
    sheet.update_cells(output_values)
    sheet.update_cells(match_counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['generate_searchterms', 'reconcile_results'])
    parser.add_argument('--filename', default='/tmp/namesearch_results',
                        help="file to work with")
    args = parser.parse_args()
    if args.action == 'generate_searchterms':
        names_searchable()
        tfn = searchterm_file(args.filename)
        print(tfn)
    elif args.action == 'reconcile_results':
        reconcile_matches(args.filename)
