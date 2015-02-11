'''
Bayesian classification to find contracts in edgar
'''
import langid
import argparse
import codecs
import os
import sklearn
import sklearn.datasets
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

from training import watershed

DIRS = {'positive': 'training/data_bayes/positive',
        'negative': 'training/data_bayes/negative'}

def load(dirpath):
    files = sklearn.datasets.load_files(dirpath, encoding='utf-8', decode_error='ignore')
    return files

def process():
    dirpath = 'training/data_bayes'
    files = load(dirpath)
    cv = CountVectorizer(ngram_range=(1,3))
    trained_counts = cv.fit_transform(files.data)
    tftrans = TfidfTransformer().fit_transform(trained_counts)
    clf = MultinomialNB().fit(tftrans, files.target)
    return locals()

def bag_of_text(directory):
    norms = []
    for fn in os.listdir(directory):
        fn = os.path.join(directory, fn)
        with open(fn, 'r') as fh:
            text = fh.read()
            try:
                text = text.decode('utf-8')
                norms.append(watershed.normalize_text(text))
            except Exception:
                pass
    return '\n'.join(norms)

def build_classifier():
    y_train = ('positive','negative')
    train_set = [bag_of_text(DIRS['positive']), bag_of_text(DIRS['negative'])]
    #train_set = ("new york nyc big apple london", "london uk great britain")
    test_set = ('nice day in nyc','london town','hello welcome to the big apple. enjoy it here and london too')
    count = CountVectorizer(ngram_range=(1,3))
    x_train = count.fit_transform(train_set).todense()
    clf = MultinomialNB().fit(x_train, y_train)
    return (clf, count)

def classify(text, classifier, vectorizer):
    THRESHOLD=0.2
    x_test  = vectorizer.transform([text]).todense()
    prob_neg, prob_pos = classifier.predict_proba(x_test)[0]
    if (prob_pos - prob_neg) > THRESHOLD:
        return 'positive'
    else:
        return 'negative'

def is_english(text, threshold=0.5):
    ranks = dict(langid.rank(text))
    return ranks.get('en', 0) >= threshold
        

def classify_dir(directory, cl=None, vect=None):
    if cl is None:
        (cl, vect) = build_classifier()
    print('INFO:classifier built')
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            fn = os.path.join(dirpath, filename)
            with open(fn, 'r') as fh:
                text = fh.read()
                text = text.decode('utf-8')
                normed = watershed.normalize_text(text)
                if not is_english(text):
                    print('INFO: skipping junk file %i' % fn)
                    continue
                print('INFO: classifying %i' % fn)
                result = classify(normed, cl, vect)                
                if result == 'positive':
                    print(fn)       

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--filingdir", default='/data/filings', help="directory with the files to classify")
    args = parser.parse_args()
    classify_dir(args.filingdir)



