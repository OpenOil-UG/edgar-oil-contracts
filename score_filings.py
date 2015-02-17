import argparse
import codecs
import re, math, string
from urlparse import urljoin
from unicodedata import normalize as ucnorm, category
from collections import defaultdict

from util.pdftext import pdf2text
from util.findcountries import countries_from_text

from mrjob.job import MRJob, JSONProtocol
from mrjob.protocol import JSONValueProtocol

DOCS = re.compile(r'^<DOCUMENT>$(.*)^</DOCUMENT>$', re.I | re.M | re.S)
SIC_EXTRACT = re.compile(r'<ASSIGNED-SIC> *(.*)', re.I)
AN_EXTRACT = re.compile(r'<ACCESSION-NUMBER> *(.*)', re.I)
CIK_EXTRACT = re.compile(r'<CIK> *(.*)', re.I)
FILENAME_EXTRACT = re.compile(r'<FILENAME> *(.*)', re.I)
CN_EXTRACT = re.compile(r'<CONFORMED-NAME> *(.*)', re.I)
TYPE_EXTRACT = re.compile(r'<TYPE> *(.*)', re.I)
REMOVE_SPACES = re.compile(r'\s+')

URL = 'http://www.sec.gov/Archives/edgar/data/%s/%s/%s-index.htm'


SCORES = {}

def makesearchregex(fn='searches.txt'):
    for line in open(fn).readlines():
        term, score = line.rsplit(',', 1)
        term = term.lower().strip()
        if term.startswith('#'):
            continue
        SCORES[term] = re.compile(term), float(score)

    searches = re.compile(' (%s) ' % '|'.join(SCORES.keys()))
    return searches



def normalize_text(text):
    if not isinstance(text, unicode):
        text = unicode(text)
    chars = []
    # http://www.fileformat.info/info/unicode/category/index.htm
    for char in ucnorm('NFKD', text):
        cat = category(char)[0]
        if cat in ['C', 'Z', 'S']:
            chars.append(u' ')
        elif cat in ['M', 'P']:
            continue
        else:
            chars.append(char)
    text = u''.join(chars)
    text = REMOVE_SPACES.sub(' ', text)
    return text.strip().lower()


def get_tokens(text):
    tokens = []
    for token in text.split():
        if token in STOPWORDS:
            continue
        if string.digits in token:
            continue
        tokens.append(token)
    return tokens


def compute_score(doc):
    text = normalize_text(doc)
    terms = defaultdict(int)
    pos_terms = set()
    score = 0.0

    tokens = max(1, len(get_tokens(text)))

    # bias for longer documents:
    #tokens = tokens / 10
    
    textlen = float(max(1, len(text)))
    if textlen > 100:
        for match in SEARCHES.finditer(text):
            term = match.group(1)
            weight = None
            if term in SCORES:
                _, weight = SCORES[term]
            else:
                for term_, (rex, weight_) in SCORES.items():
                    if rex.match(term):
                        weight = weight_
                        term = term_
                        break

            if weight is None:
                continue

            if weight > 0:
                pos_terms.add(term)
            
            pos = float(match.start(1)) / textlen
            score += (weight * (math.log(pos) * -1.0)) + weight
            #print weight, score
            #print match.group(1), weight, score
            terms[term] += 1

    #print score, terms
    # weight for variety:
    #score = ((score * len(pos_terms)) / tokens)
    # score = score
    return score, tokens, len(pos_terms), dict(terms)


class MRScoreFiles(MRJob):
    """
    input a list of filepaths
    output a list of filepaths which score above the threshold
    """
    THRESHOLD=10
    OUTPUT_PROTOCOL = JSONValueProtocol

    def country_names(self, text):
        text = normalize_text(text) # XXX avoid this repetition
        return {'country_names': countries_from_text(text)}

    def text_from_file(self, filepath):
        return codecs.open(filepath, 'r', 'utf-8').read()

    def mapper(self, _, filepath):
        filetext = self.text_from_file(filepath)
        score, tokens, numpositive, dictpositive = compute_score(filetext)
        if True or score > self.THRESHOLD:
            output = {
                'score': score,
                'filepath': filepath,
                'positives': dictpositive
                }

            output.update(self.country_names(filetext))
            yield None, output

class MRScorePDFs(MRScoreFiles):
    def text_from_file(self, filepath):
        return pdf2text(filepath)

class MRScoreFilings(MRJob):

    INPUT_PROTOCOL = JSONProtocol
    OUTPUT_PROTOCOL = JSONProtocol

    def mapper(self, fn, data):
        raw_score, tokens, pos_terms, terms = compute_score(data.get('doc'))
        score = (raw_score * pos_terms) / (tokens / 2)
        if score <= 0:
            return
        an = AN_EXTRACT.findall(data.get('header'))
        if len(an) != 1:
            return
        an = an.pop()
        man = an.replace('-', '')
        sic = SIC_EXTRACT.findall(data.get('header')).pop()
        cik = CIK_EXTRACT.findall(data.get('header')).pop()
        url = URL % (int(cik), man, an)
        doc_url = None
        fnames = FILENAME_EXTRACT.findall(data.get('doc'))
        if len(fnames):
            doc_url = fnames.pop()
        if doc_url is not None and len(doc_url.strip()):
            doc_url = urljoin(url, doc_url)
        yield url, {
            #'number': an,
            #'cik': cik,
            'sic': sic,
            'filing_type': TYPE_EXTRACT.findall(data.get('header')).pop(),
            'doc_type': TYPE_EXTRACT.findall(data.get('doc')).pop(),
            'doc_url': doc_url,
            'name': CN_EXTRACT.findall(data.get('header')).pop(),
            'raw_score': raw_score,
            'tokens': tokens,
            'score': score,
            'positive_terms': pos_terms,
            'terms': terms
        }

    def reducer(self, url, files):
        max_score, file_data = 0, None
        for data in files:
            if data.get('score', 0) > max_score:
                max_score = data.get('score', 0)
                file_data = data
        if file_data is not None:
             yield url, file_data


if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument("--stopwords", default="stopwords.txt", help="file containing stopwords")
    #parser.add_argument("--watershed", default="watershed_list.txt", help="file containing watershed file")
    #ARGS = parser.parse_args()
    class ARGS:
        stopwords = 'stopwords.txt'
        watershed = 'watershed_list_licenses.txt'

    STOPWORDS = set(open(ARGS.stopwords).read().lower().split())
    SEARCHES = makesearchregex(ARGS.watershed)
    #MRScoreFilings.run()
    #MRScoreFiles.run()
    MRScorePDFs.run()
