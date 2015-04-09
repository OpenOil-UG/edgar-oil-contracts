
def filename_to_s3path(fn):
    fn = fn.replace('/data/sedar/mining/', 'https://sedar.openoil.net.s3.amazonaws.com/')
    fn = fn.replace('/data/sedar/', 'https://sedar.openoil.net.s3.amazonaws.com/')
    fn = fn.replace('/data/oil', 'https://sec-edgar.openoil.net.s3.amazonaws.com/oil')
    fn = fn.replace('s3://sec-edgar.openoil.net', 'https://sec-edgar.openoil.net.s3.amazonaws.com')
    return fn
