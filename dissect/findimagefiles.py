'''
Find PDFs containing only images
'''

from score_filings import MRScoreFilings
from mrjob.job import MRJob
import mrjob

from dissect.util.pdftext import pdf2text
from dissect.util import filename_to_s3path

import logging

class ImagePDFs(MRJob):
    OUTPUT_PROTOCOL = mrjob.protocol.RawValueProtocol

    def mapper(self, _, filepath):
        filepath = filepath.strip('\n').strip()
        filetext = pdf2text(filepath)
        if not filetext.strip():
            yield None, filepath

    def reducer(self, _, filepaths):
        for filepath in filepaths:
            url = filename_to_s3path(filepath)
            yield None, url


if __name__ == '__main__':
    ImagePDFs.run()
