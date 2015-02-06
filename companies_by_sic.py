import requests
from lxml import html

def by_sic_corpwatch(sic):
    # does not work
    params = {
        'sic_code': sic,
        'limit': 5000,
        }
    url = 'http://api.corpwatch.org/companies.json'
    r = requests.get(url, params=params)
    return r.json()

def by_sic(sic):
    url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=%s&owner=include&match=&start=0&count=4999&hidefilings=0' % sic
    r = requests.get(url)
    doc = html(r.text)
    rows = doc.findall('.//tr')
    companies = []
    for row in rows[1:]: # ditch the headers
        cik, name, state = [x.text_content() for x in row.findall('.//td')]
        cik = cik.lstrip('0') # official CIKs have leading zeroes, but they are painful for us
        yield [cik, name, state, sic]

