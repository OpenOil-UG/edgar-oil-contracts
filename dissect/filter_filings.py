import argparse
import os, gzip, logging
import codecs
import glob
logging.basicConfig(level=logging.DEBUG)

# monkeypatch gzip to ignore badly-terminated gz files

def _read_eof(self): pass
gzip.GzipFile._read_eof = _read_eof

def cik_list(args):
    ciks = set()
    for line in open(args.company_list):
        ciks.add(line.split('\t')[0])
    return ciks


def filter_company_filings(fn):
    try:
        with gzip.open(fn) as fh:
            while '--------------------------------------' not in fh.readline():
                pass # remove header bumf
            for line in fh:
                items = line.split('|')
                cik = items[0]
                if cik in CIKS:
                    yield line
    except (EOFError, IOError):
        os.unlink(fn)
        logging.error('file %s is incomplete' % fn)
        
def process_file(args, fn):
    outfn = '%s/%s' % (args.output_dir, fn.replace('.gz', '_filtered.txt'))
    if os.path.exists(outfn):
        return
    logging.info('processing ' + fn)
    with open(outfn, 'w') as outf:
        fpath = '/'.join([args.input_dir, fn])
        outf.writelines(filter_company_filings(fpath))

def process_all(args):
    for fn in glob.glob1(args.input_dir, '*gz'):
        process_file(args, fn)
        #return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir',
                        help='directory containing the EDGAR index files (look like master_2013_2.gz')
    parser.add_argument('--output_dir',
                        help='where to put the results')
    parser.add_argument('--company_list',
                        help='file with basic company info (tsv format, as extracted from SEDAR indices')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    CIKS = cik_list(args)
    process_all(args)
