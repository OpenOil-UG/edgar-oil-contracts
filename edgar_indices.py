import os, urllib2, logging

OUTPUT_DIR='./company_listings'
logging.basicConfig(level=logging.INFO)

def urls():
    for year in range(1993, 2015):
        for qtr in [1,2,3,4]:
            url = 'ftp://ftp.sec.gov/edgar/full-index/%s/QTR%s/master.gz' % (year, qtr)
            filename = 'master_%s_%s.gz' % (year, qtr)
            yield url, filename

def dl():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    for (url, filename) in urls():
        logging.info('downloading %s' % url)
        fp = '%s/%s' %(OUTPUT_DIR, filename)
        if os.path.exists(fp): continue
        with open(fp, 'w') as f:
            f.write(urllib2.urlopen(url).read())


if __name__ == '__main__':
    dl()


