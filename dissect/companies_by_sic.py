import requests
from lxml import html
from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol, RawValueProtocol
import logging

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

    OUTPUT_PROTOCOL = RawValueProtocol

    # how many companies on each page in the SEC listing site
    # nb this site 
    PERPAGE = 100

    def dl_one_page(self, sic, offset):
        companies_found = set()
        url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC=%s&owner=include&match=&start=%s&count=%s&hidefilings=0' % (sic, offset, self.PERPAGE)
        r = requests.get(url)
        doc = html.fromstring(r.text)
        rows = doc.findall('.//tr')
        for row in rows[1:]: # ditch the headers
            cik, name, state = [x.text_content() for x in row.findall('.//td')]
            cik = cik.lstrip('0') # official CIKs have leading zeroes, but they are painful for us
            companies_found.add("\t".join([cik, name, state, sic]))
        return companies_found

    def mapper(self, _, sic):
        downloaded = set()
        for offset in range(0,10000, self.PERPAGE):
            new_companies = self.dl_one_page(sic, offset)
            if new_companies.issubset(downloaded):
                break
            downloaded.update(new_companies)
        for item in sorted(downloaded):
            yield None, item

if __name__ == '__main__':
    SICCorps.run()

