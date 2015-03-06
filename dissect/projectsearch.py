
from score_filings import MRScoreFiles, normalize_text
import codecs
from collections import defaultdict
import re


class MrMatchFiles(MRScoreFiles):
    '''
    Just
    '''

    def configure_options(self):
        pass

    def mapper_init(self):
        self.search_terms = ['Project']
        pass

    def getcontext(self, needle, haystack):
        wingers = 19 # how many chars of context to include each side
        start = max(0, haystack.index(needle) - wingers)
        end = start + len(needle) + wingers
        return haystack[start:end]

    def greptext(self, filetext):
        matches  = defaultdict(list)
        for term in self.search_terms:
            if term in filetext:
                matches[term].append(self.getcontext(term, filetext))
        return matches

    def get_company(self, filepath):
        # company id
        return filepath.split('/')[-2]
    
    def mapper(self, _, filepath):
        filetext = self.text_from_file(filepath)
        filetext = normalize_text(filetext)
        matches = self.greptext(filetext)
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
            yield self.company, output


if __name__ == '__main__':
    MrMatchFiles.run()
