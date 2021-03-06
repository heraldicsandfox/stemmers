import sys
from itertools import combinations

corp = sys.argv[1]
ty = sys.argv[2]

def rootdir(str):
    if str == 'krovetz' or str == 'lemmatized':
        basedir = 'corpora/'
    else:
        basedir = '../stemround2/corpus/'
    return basedir

stoplist = set([line.strip() for line in open('/home/aks249/Mallet/stoplists/en.txt')])

stemmers = ['nostemmer', 'krovetz', 'sstemmer', 'lemmatized', 'porter', 'porter2', 'lovins', 'paicehusk', 'trunc5', 'trunc4']
readfiles = [open('{}/{}-{}-{}.txt'.format(rootdir(stemmer), corp, ty, stemmer)) for stemmer in stemmers]
writefiles = [open('corpora/{}-{}-{}-stopped.txt'.format(corp, ty, stemmer), mode='w') for stemmer in stemmers]
with open('corpora/{}-{}-nostemmer.txt'.format(corp, ty)) as readref:
    with open('corpora/{}-{}-nostemmer.txt'.format(corp, ty)) as writeref:
        for line in readref:
            readlines = [f.readline() for f in readfiles]
            if not any(readlines):
                continue
            readchunks = [l.split('\t', 2) for l in readlines]
            wordlists = [c[2].split() for c in readchunks]
            for i in range(len(stemmers)):
                while len(wordlists[i]) == 0:
                    readlines[i] = readfiles[i].readline()
                    readchunks[i] = readlines[i].split('\t', 2)
                    wordlists[i] = readchunks[i][2].split()

            # check that all documents are the same length
            for wl in wordlists[1:]:
                if len(wordlists[0]) != len(wl):
                    raise Exception('Misaligned sentences:\n{}\n{}'.format(wordlists[0], wl))

            # Figure out which words to delete from each and delete 'em
            stopwordmask = [any([ch.isdigit() for ch in wd]) or wd in stoplist for wd in wordlists[0]]
            writelists = [[wd for wd, mask in zip(wl, stopwordmask) if not mask] for wl in wordlists]

            # Reformat into lines of text and write out
            writelines = ['{}\t{}\t{}\n'.format(rc[0], rc[1], ' '.join(wl)) for rc, wl in zip(readchunks, writelists)]
            for wf, wn in zip(writefiles, writelines):
                wf.write(wn)

for file in readfiles:
    file.close()
for file in writefiles:
    file.close()
