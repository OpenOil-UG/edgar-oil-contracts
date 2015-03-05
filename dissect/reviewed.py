'''
generate list of filings which have already been reviewed
'''
import functools32
import sheets
import logging
logging.basicConfig(level=logging.DEBUG)


def spreadsheet_rows(st):
    '''
    Iterator over all rows in a spreadsheet
    it'd be nicer to get row
    '''
    headings = st.row_values(1)
    records = st.get_all_records()
    for record in records:
        yield [record.get(h, None) for h in headings]


@functools32.lru_cache()
def review_sheets():
    '''
    iterator over all sheets listing reviewed filings
    TODO: add filters to all this
    '''
    
    details = {
    }
    sheetlabels = (
        # id, label, (...maybe more cols needed for filters?)
        ('1G-pDGp1_XmcVei-Xhpb6a1Gr5BKywI7LxHjGDU9_q08', 'sedar 2014 first watershed'),
        ('1AzNLq4CZa4C5M_sjDy8ZZIRYq7f1LKOKe3gngYfFCPI', 'sedar 2014 second watershed'),
        ('1HICJemIqrL1KrgENis3zR9CQJ_fUi0NYuNAvdUJJKn0', 'edgar first go'),
        ('1KzTj6GzRrxhsBDCiW_k9toCj5ekkK4PcPpzWNsu4ZlI',  'edgar second go, trying to filter out licenses'), 
        )
    for key, name in sheetlabels:
        logging.debug('processing sheet %s' % name)
        st = sheets.CONN.open_by_key(key).sheet1
        for row in spreadsheet_rows(st):
            if len(row) < 3:
                logging.debug('skipping too-short row')
                continue
            classification = row[2]
            if not (classification and classification.strip()):
                logging.debug('skipping non-analyzed row')
                continue
            url = row[1]
            logging.debug('adding row to details')
            details[url] = {
                'classification': classification,
                'sheet_key': key,
                'sheet_label': name,
                'row': row,
                }
    return details
