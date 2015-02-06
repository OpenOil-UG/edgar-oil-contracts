import requests
from lxml import html
from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

def by_sic_corpwatch(sic):
    # does not work
    params = {
        'sic_code': sic,
        'limit': 5000,
        }
    url = 'http://api.corpwatch.org/companies.json'
    r = requests.get(url, params=params)
    return r.json()

class EdgarIndices(MRJob):

    def mapper(self, _, x):
        for year in range(1993, 2016):
            for qtr in [1,2,3,4]:
                urlpattern = 'ftp://ftp.sec.gov/edgar/full-index/2014/QTR%s/company.gz' % (year, qtr)
                yield urlpattern

class SICCorps(MRJob):
    '''
    input: SIC codes, one per line
    output: tab-delimited cik, name, company, sic for companies with that SIC
    '''

    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, _, sic):
        url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=%s&owner=include&match=&start=0&count=4999&hidefilings=0' % sic
        r = requests.get(url)
        doc = html.fromstring(r.text)
        rows = doc.findall('.//tr')
        companies = []
        for row in rows[1:]: # ditch the headers
            cik, name, state = [x.text_content() for x in row.findall('.//td')]
            cik = cik.lstrip('0') # official CIKs have leading zeroes, but they are painful for us
            yield None, {
                'cik': cik,
                'name': name,
                'state': state,
                'sic': sic}


if __name__ == '__main__':
    SICCorps.run()

