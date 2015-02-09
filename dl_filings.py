'''
Given a listing like this:
1015647|ALMADEN MINERALS LTD|6-K|2014-05-14|edgar/data/1015647/0001102624-14-000792.txt

download it to:
OUTPUT_DIR/1015647/6-K_2014-05-14_0001102624-14-000792.txt
'''
import ftplib
import sys
import os
try:
    from urllib import urlretrieve
except ImportError: #using py3
    from urllib.request import urlretrieve
from Queue import Queue
from threading import Thread

from multiprocessing import Pool

config = {
    'threads': 20,
    }


OUTPUT_DIR = '/data/edgar_filings'

def get_paths(line):
    (cik, name,filetype,date,url) = line.split('|')
    filename = url.split('/')[-1]
    filetype = filetype.replace('/', '')
    dirpath = '%s/%s' % (OUTPUT_DIR, cik)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    outfn = '%s/%s_%s_%s' % (dirpath, filetype, date, filename)
    print(url, outfn)
    return url, outfn

def dl_ftp_worker(i,q):
    ftp = ftplib.FTP('ftp.sec.gov')
    ftp.login('anonymous', '@anonymous')
    ftp.cwd('/')
    while True:
        print('%s pulling from q' % i)
        line = q.get()
        url, outfn = get_paths(line)
        if os.path.exists(outfn):
            q.task_done()
            continue
        with open(outfn, 'wb') as outfh:
            ftp.retrbinary('RETR ' + url, outfh.write)
        print('got %s' % url)
        q.task_done()


def dl_one(line):
    url, outfn = get_paths(line)
    fullurl = 'ftp://ftp.sec.gov/%s' % url
    try:
        #open(outfn, 'w').write(urllib2.urlopen(fullurl).read())
        urlretrieve(fullurl, outfn)
    except Exception:
        if os.path.exists(outfn):
            os.unlink(fn)
    return True

def dl_worker(i, q):
    while True:
        print('%s pulling from q' % i)
        line = q.get()
        dl_one(line)
        q.task_done()




def dl_queue(fh):
    workqueue = Queue()
    workers = []
    for i in range(5):
        worker = Thread(target = dl_ftp_worker, args = (i, workqueue))
        worker.setDaemon(True) ## why?
        worker.start()
        workers.append(worker)
    for line in fh:
        workqueue.put(line.strip())
        print('line queued')
    workqueue.join()

if __name__ == '__main__':
    dl_queue(sys.stdin)
