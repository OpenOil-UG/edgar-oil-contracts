import os, urllib2, logging
import argparse

logging.basicConfig(level=logging.INFO)

def urls():
    for year in range(1993, 2015):
        for qtr in [1,2,3,4]:
            url = 'ftp://ftp.sec.gov/edgar/full-index/%s/QTR%s/master.gz' % (year, qtr)
            filename = 'master_%s_%s.gz' % (year, qtr)
            yield url, filename

def dl(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for (url, filename) in urls():
        logging.info('downloading %s' % url)
        fp = '%s/%s' %(output_dir, filename)
        if os.path.exists(fp):
            continue
        with open(fp, 'w') as f:
            f.write(urllib2.urlopen(url).read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='./company_listings',
                        help='where to put the edgar index files')
    args = parser.parse_args()
    dl(args.output_dir)


