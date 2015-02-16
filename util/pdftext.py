'''
pull text from a PDF file
'''
import subprocess

def pdf2text(fn):
    bytestr = subprocess.check_output(['pdftotext', fn, '-'])
    return bytestr.decode('utf-8', errors='ignore')
