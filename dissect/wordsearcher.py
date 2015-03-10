from score_filings import MRScoreFiles, normalize_text
import codecs
from collections import defaultdict
import re
import logging


class MrMatchFiles(MRScoreFiles):
    '''
    Just
    '''
    THRESHOLD=0


    def configure_options(self):
        super(MrMatchFiles, self).configure_options()
        self.add_passthrough_option(
            '--searchterm-file', default='/tmp/searchterms.txt',
            help='File containing regexes to search for, one per line')
        self.add_passthrough_option(
            '--regex', default=False, action='store_true',
            help='Search regexes, instead of plain matches')


    def mapper_init(self):
        corptypes = re.compile(r'\b(limited|ltd|inc|sarl|plc)\b', re.I)
        self.search_terms = []
        ft = codecs.open(self.options.searchterm_file, 'r', 'utf-8')
        for l in ft.readlines():
          pattern = corptypes.sub('', l)
          pattern = pattern.strip().lower()
          #pattern = normalize_text(pattern)
          if pattern:
              if self.options.regex:
                  pattern = re.compile(pattern)
              self.search_terms.append(pattern)

    def getcontext(self, needle, haystack):
        wingers = 19 # how many chars of context to include each side
        start = max(0, haystack.index(needle) - wingers)
        end = start + len(needle) + wingers
        return haystack[start:end]

    def greptext_regex(self, filetext):
        matches  = defaultdict(list)
        for term in self.search_terms:
            matched = term.search(filetext)
            if matched:
                matches[term.pattern].append(self.getcontext(matched.group(0), filetext))
        return matches

    def greptext(self, filetext):
        if self.options.regex:
            return self.greptext_regex(filetext)
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
