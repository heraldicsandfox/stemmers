#!/usr/bin/python
import gzip
import codecs
from collections import defaultdict
from nltk.tokenize import WordPunctTokenizer
import re
import sys


class AbstractStemmer(object):
    def __init__(self):
        super(AbstractStemmer, self).__init__()
        self.tokenizer = WordPunctTokenizer()
        self.vocab = set()
        self.basename = 'nostemmer'

    def stem(self, files):
        # We write files to a -[stemmer].txt file
        filename_mod = files[0].split('.')[0]
        wf = codecs.open('{1}-{0}.txt'.format(self.basename, filename_mod), 'w', encoding='utf-8')
        isword = re.compile('[a-z0-9]+')

        # We can work with both gzip and non-gzip
        for fname in files:
            if fname.endswith('gz'):
                f = gzip.open(fname, 'r')
            else:
                f = open(fname)
            for no, line in enumerate(f):
                line = line.decode('utf-8')
                # We drop empty lines
                if len(line.strip()) == 0:
                    continue

                # Clean and process words
                curr_words = self.tokenizer.tokenize(line)
                clean_words = [word.lower() for word in curr_words]
                processed_words = self.process(clean_words)

                # Keep track of vocab size
                self.vocab.update(processed_words)

                # We output according to the one-doc-per-line format for Mallet
                current_line = u' '.join(processed_words)
                line_fmt = '{0}-{1}\t{0}\t{2}\n'.format(self.basename, no, current_line)
                wf.write(line_fmt)
            f.close()

        print 'Resulting vocab size: {0}'.format(len(self.vocab))
        wf.close()

    def process(self, words):
        raise NotImplementedError("No stemmer here!")
