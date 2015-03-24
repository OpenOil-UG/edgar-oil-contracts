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

from edgar_link import edgar_from_filepath
from util import filename_to_s3path

import reviewed

###
# file filters -- these operate on the entire file
# 
# they should be implemented as generator functions, returning each line
##

def sortedjson(pin, args):
    '''
    order json by score, highest-scoring first
    '''
    jsons = [json.loads(ln) for ln in pin.readlines()]
    jsons.sort(key=lambda x: int(x['score']), reverse=True)
    for j in jsons:
        yield json.dumps(j)


###
# row filters -- these operate on the json version of each line
# 
# They should return the altered line, still as json
##


def s3links(jline, args):
    jline['filepath'] = filename_to_s3path(jline['filepath'])
    return jline

def edgar_link(jline, args):
    if ('edgar' in jline['filepath']):
        ignored, jline['edgar_link'], jline['edgar_exhibit_number'] = edgar_from_filepath(jline['filepath'])
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


def countrynames(jline, args):
    jline['country_names'] = ','.join(jline['country_names'])
    return jline

def search_term(jline, args):
    return jline


## Runners
#
# these set up which options will be used
# then call run_inner to do the actual processsing


def run_pipe_default(pin, pout, args):

    file_filters = [sortedjson]
    row_filters = [countrynames, s3links]
    if args.include_old_reviews:
        row.filters.appened(is_reviewed)

    if args.edgar:
        row_filters.append(edgar_link)
        cols = ['score', 'filepath', 'edgar_link', 'edgar_exhibit_number', 'prior_review', 'positives', 'country_names', 'extract']
    else:
        cols = ['score', 'filepath','prior_review', 'positives', 'country_names', 'extract']
 
    return run_inner(pin, pout, file_filters, row_filters, cols)

def run_eiti_concessions(pin, pout, args):
    file_filters = [sortedjson]
    row_filters = [countrynames, s3links]

    cols = ['score', 'filepath','prior_review', 'positives', 'country_names', 'extract'] 

    return run_inner(pin, pout, file_filters, row_filters, cols)
    

def run_inner(pin, pout, file_filters, row_filters, cols):
    writer = unicodecsv.writer(pout, encoding='utf-8')
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
    parser.add_argument('--include_old_reviews', type=bool, default=False, help='include cross-reference against previous reviews?')
    parser.add_argument('--edgar', default=False, action='store_true', help='apply edgar-specific post-processing (e.g. fixing links)')
    parser.add_argument('--eiti_concessions', default=False, action='store_true', help='Suppress normal processing. Instead generate output for EITI concession list')    
    args = parser.parse_args()
    if args.eiti_concessions:
        run_eiti_concessions(sys.stdin, sys.stdout, args)
    else:
        run_pipe_default(sys.stdin, sys.stdout, args)
