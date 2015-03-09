
from score_filings import MRScoreFiles, normalize_text
from mrjob.protocol import JSONProtocol, RawProtocol
import codecs
from collections import defaultdict
import re
import logging

class MRProjectSearch(MRScoreFiles):
    THRESHOLD=0
    OUTPUT_PROTOCOL = RawProtocol

    def mapper_init(self):
        self.search_terms = map(re.compile, [
                r'([A-Z][a-z]+ +)+Project', # any number of capitalized words, then project
                                ])

    def getcontext(self, needle, haystack):
        wingers = 19 # how many chars of context to include each side
        start = max(0, haystack.index(needle) - wingers)
        end = start + len(needle) + wingers
        return haystack[start:end]

    def greptext_plain(self, filetext):
        matches  = defaultdict(list)
        for term in self.search_terms:
            if term in filetext:
                print('found %s' % term)
                matches[term].append(self.getcontext(term, filetext))
        return matches

    def greptext(self, filetext, filepath):
        matches  = defaultdict(list)
        for term in self.search_terms:
            match = term.search(filetext)
            if match:
                matches[term].append(
                    {'match': match.group(),
                     'context': self.getcontext(match.group(), filetext),
                     'filepath': filepath})
        return matches


    def get_company(self, filepath):
        # company id
        return filepath.split('/')[-2]
    
    def mapper(self, _, filepath):
        try:
            filetext = self.text_from_file(filepath)
        except Exception:
            logging.error('unable to open file %s' % filepath)
            raise StopIteration
        matches = self.greptext(filetext, filepath)
        for (label, matchgroup) in matches.items():
            for term in matchgroup:
                yield self.get_company(filepath), term
        """                                     
        score = len(matches)
        if score > self.THRESHOLD:
            output = {
                'company': self.get_company(filepath),
                'score': score,
                'filepath': filepath,
                'positives': matches
                }
            output.update(self.country_names(filetext))
            output.update(self.snippet(filetext))
            logging.warn('yielding')
            yield output['company'], output
        """
    
    def reducer(self, company, termresults):
        resultcount = defaultdict(int)
        resultcontext = defaultdict(list)
        resultfiles = defaultdict(list)
        for matchdict in termresults:
            term = matchdict['match']
            resultcount[term] += 1
            resultcontext[term].append(matchdict['context'])
            resultfiles[term].append(matchdict['filepath'])
        for match, cnt in resultcount.items():
            contexts = '"%s"' % '; '.join(resultcontext[match])
            filepaths = '"%s"' % '; '.join(resultfiles[match])
            output = ','.join([match, str(cnt), contexts, filepaths])
            #output = '%s,%s' % (match,cnt,)
            yield company, output


if __name__ == '__main__':
    MRProjectSearch.run()
