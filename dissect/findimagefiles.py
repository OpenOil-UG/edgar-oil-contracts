'''
Find PDFs containing only images
'''

from score_filings import MRScoreFilings
from mrjob.job import MRJob

from dissect.util.pdftext import pdf2text
import logging

class ImagePDFs(MRJob):
    
    def mapper(self, _, filepath):
        filepath = filepath.strip('\n').strip()
        filetext = pdf2text(filepath)
        if not filetext.strip():
            yield None, filepath


if __name__ == '__main__':
    ImagePDFs.run()
