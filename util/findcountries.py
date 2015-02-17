'''
find all country names
'''
import os
import re

def build_regex(fn=None):
    if fn is None:
        fn = os.path.join(os.path.dirname(__file__), 'countries.txt')
    fh = open(fn)
    country_names = [x.strip().lower() for x in fh.readlines() if not x.startswith('#')]
    bigre = re.compile('(' + '|'.join(country_names) + ')')
    return bigre

CREGEX = build_regex()
    
def countries_from_text(text):
    text = text.lower()
    return(sorted(set(x[0] for x in CREGEX.findall(text))))
