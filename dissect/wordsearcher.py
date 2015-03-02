from score_filings import MRScoreFiles, normalize_text
import codecs
from collections import defaultdict


class MrMatchFiles(MRScoreFiles):
    '''
    Just
    '''
    SEARCHTERM_FILE='/tmp/searchterms.txt'
    THRESHOLD=0

    def mapper_init(self):
        ft = codecs.open(self.SEARCHTERM_FILE, 'r', 'utf-8')
        self.search_terms = [normalize_text(l) for l in ft.readlines()]

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

    def mapper(self, _, filepath):
        filetext = self.text_from_file(filepath)
        filetext = normalize_text(filetext)
        matches = self.greptext(filetext)
        score = len(matches)
        if score > self.THRESHOLD:
            output = {
                'score': score,
                'filepath': filepath,
                'positives': matches
                }
            output.update(self.country_names(filetext))
            output.update(self.snippet(filetext))
            yield None, output


if __name__ == '__main__':
    MrMatchFiles.run()
