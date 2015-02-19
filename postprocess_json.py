'''
turn mrjob's json output into a CSV file ready for
upload to google drive.
Also include other filtering
'''

import argparse
import unicodecsv
import json
import csv
import sys
import functools32

import reviewed

def sortedjson(pin, args):
    '''
    '''
    jsons = [json.loads(ln) for ln in pin.readlines()]
    jsons.sort(key=lambda x: int(x['score']), reverse=True)
    for j in jsons:
        yield json.dumps(j)

def s3links(jline, args):
    jline['filepath'] = jline['filepath'].replace('/data/sedar', 'https://sedar.openoil.net.s3.amazonaws.com')
    return jline

@functools32.lru_cache()
def get_reviewed_records():
    return set(reviewed.review_sheets().keys())

def is_reviewed(jline, args):
    '''
    has this filing already been manually reviewed?
    '''
    prior_review = None
    prior = reviewed.review_sheets().get(jline['filepath'], {})
    prior_review = prior.get('classification', None)
    jline['prior_review'] = prior_review
    return jline

def run_pipe(pin, pout, args):
    writer = unicodecsv.writer(pout, encoding='utf-8')

    file_filters = [sortedjson]
    row_filters = [s3links, is_reviewed]

    cols = ['score', 'filepath','prior_review', 'positives', 'country_names', 'extract']

    for filt in file_filters:
        pin = filt(pin, args)

    for line in pin:
        jline = json.loads(line)
        for filt in row_filters:
            jline = filt(jline, args)    
        
        rowdetails = [ jline.get(key, '') for key in cols]
        writer.writerow(rowdetails)

    pout.flush()
    
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    run_pipe(sys.stdin, sys.stdout, args)