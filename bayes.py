'''
Bayesian classification to find contracts in edgar
'''

import sklearn

def load(dirpath):
    files = sklearn.datasets.load_fileS(dirpath, encoding='utf-8', decode_error='ignore')
    return files



if __name__ == '__main__':
    pass
