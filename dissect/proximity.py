from wordsearcher import MrMatchFiles
from score_filings import OOMRJob
import re

class ProximitySearch(MrMatchFiles):
    pass
    flags=re.DOTALL
    ignorecase=False

    def mapper_init(self):
        self.options.regex = True
        OOMRJob.mapper_init(self)
        pattern1 = '\W[123]P\W'
        context = '.{0,200}'
        pattern2 = '(barrel|Barrel|BARREL)'
        self.search_terms = []
        self.search_terms.append(re.compile(pattern1 + context + pattern2, flags=self.flags))
        self.search_terms.append(re.compile(pattern2 + context + pattern1, flags=self.flags))
    
    


    


if __name__ == '__main__':
    ProximitySearch.run()
