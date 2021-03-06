# stemmers
Storing code for running large batches of stemmed topic models and their
evaluations on HTCondor with Mallet.

## Files

### Stemmers

Stemmers/conflation treatments are included in the stemmers/ directory
for the following:

1. nostemmer (just tokenization),
2. krovetz (Krovetz stemmer),
3. lemmatizer (WordNet Lemmatizer with Stanford POS tagging),
4. lovins (Lovins stemmer),
5. paicehusk (Paice/Husk or Lancaster stemmer),
6. porter (Porter stemmer),
7. porter2 (Porter2/Snowball stemmer),
8. sstemmer (Harman S-stemmer),
9. trunc4 (4-truncation), and
10. trunc5 (5-truncation).

These will output files with the path
    '[original file basename]-[stemmer].txt]'
with each line having the Mallet one-document-per-line three-column format. To
change this format or general behavior of all lemmatizers, modify
stemmers/abstractstemmer.py; to modify any of the actual stemmers, edit
stemmers/[stemmer].py.

### Useful scripts

**prepdirs.sh**: Creates all the useful output directories necessary for the
different types of output and evaluation these scripts produce.

**finddiffs.py**: First writes out the resulting vocabulary size of every
stemming treatment, then prints out examples of short pieces of text that
maximize how different they are between stemmers. Helpful for generating tables
for the figure.

**stopwords.py**: With a given corpus and train/test as inputs, aligns all
files and removes stopwords from them based on an unstemmed stoplist (at
present, 'en.txt' stolen from Mallet).

**average_token_length.py**: Looks at the training set for each corpus and
treatment and computes the average token length for the set.

**VariationOfInformation.java**: Written by David Mimno. Compares two state
files and uses assignments of words to topics to compute variation of
information (VOI), a distance metric between clusterings (Meila, 2003).

**combine_states.py**: Takes a state file from the normal states and rewrites
it to have the unstemmed tokens again. This allows the production of more
comparable coherence measures with new PMI scores via Mallet (via Newman and
Mimno).

**join_vois.sh**: Takes the outputs of voi.sh/condor and joins them into one
file per corpus, topic count pair. (You probably should not need a script for
this but the cat command takes less effort than the Python alternative).

**generate_wordweights.py**: Generates the word-topic count files needed for
word_entropy.py. This should not be necessary to use but was helpful when
previous versions of train.sh did not generate these files. If it needs to
be done in bulk, generate_wordweights.condor is also available.

### Core HTCondor queue jobs

**import-datasets.[sh,condor]**: Converts existing datasets to Mallet .seq
files, using the training data as the vocabulary source for the test data.

**train.[sh,condor]**: Trains lots of topic models using Mallet. These
arguments allow adaptive hyperparameters with asymmetric alpha and writes out a
whole bunch of types of output for later use. Topic models go in states/,
evaluators in evaluators/, keys in keys/, and diagnostics in diagnostics/.
The printed text from the Mallet run that would usually go to stderr goes to
outs/.

**pull_out_betas.[py,condor]**: Finds the probability on the test set of a
single-topic training set, useful for normalizing across different corpora when
looking at held-out likelihood. The relevant outputs are the total likelihoods
stored in oneoutprobs/.

**runevals.[sh,condor]**: Computes the held-out likelihood of each topic model
on a test set with Mallet using left-to-right estimation (Wallach, 2009). This
includes total likelihoods as well as per-document and per-token likelihoods.
Outputs go to outprobs/, docprobs/, and wordprobs/, respectively.

**voi.[sh,condor]**: Uses the VariationOfInformation script to compute pairwise
variations of information across all stemmers for each choice of topic count
and corpus. The voi files go into vois/.

**redo_states.[sh,condor]**: Uses the combine_states script to create unstemmed
versions of all state files one by one. Unlike other setups, where one would
submit one condor job, redo_states.sh creates and submits a separate job for
each state file, recreating a condor file from redo_states.condor and extra
lines in special.condor. This hinders job tracking but makes choosing the file
for each job easier. The resulting states go to modstates/.

**coherences.[sh,condor]**: Takes the states redone with redo_states and
uses Mallet to generate coherence scores for the resulting topics on the
untreated corpus, outputting diagnostics files to coherences/.

**word_entropy.[py,condor]**: Computes the average change in entropy
between stemmed and unstemmed versions of words for the stemmed treatments
(only seven of the ten total treatments). Lists of the top and bottom words
by entropy difference are put in wordlists/.

**word_probability.[py,condor]**: Computes the average change in held-out
log probability for each unstemmed word form, weighted by the idf of the
word. Lists of top and bottom words by probability difference are put in
wordlistsidf/.

### Sanity checks

In order for these experiments to work, it is necessary for the sequence files
generated by Mallet to have their tokens aligned across different treatments.
While stopwords.py and the import-datasets files should ensure that this
happens, problems with the treatment, the tokenizer regular expressions, and
the system can prevent this from occurring, leading to invalid or potentially
uncomputable later metrics. To ensure that input files do not disgree on the
number of tokens in each document, it is a good idea to verify that the files
match before continuing.

**sanitycheckers/check_corpora.sh**: Checks all corpus outputs using the wc
bash tool to ensure that they have the same number of lines and tokens but
different numbers of characters (as sometimes broken tokenization treatments
fail simply by not changing any tokens). If an inconsistent token count arises,
it indicates the corpus affected and the line, word, and character counts of
each treated file from that corpus.

**sanitycheckers/check_states.sh**: Checks the topic model progress files in
outs/ to ensure that all topics with the same corpus have the same number of
total tokens in sequence file format. This catches errors caused by any
inconsistency in the Mallet file import process in cases where the regular
expression for file import tokenization is more conservative for creating
Mallet files than for creating the original corpus. For example, if a stemmer
converts '1980s' to '1980' and the tokenization regular expression only allows
letter characters, the former will produce one token and the latter none.

### Charts

**gather_ptlls.py**: Looks through the evaluator outputs and the single-topic
evaluator outputs to compute normalized per-token log likelihoods for every
state file, then aggregating them into bar charts split by corpus and topic
count. This saves as llplots.png.

**gather_coherences.py**: Looks through the diagnostic file outputs and builds
bar charts of topic coherence for each treatment much like those output by
gather_ptlls. Requires BeautifulSoup, and saves as diagnostics.png.

**gather_vois.py**: Takes the voi outputs (combined into single files with the
join_vois.sh script) and uses them to build a heatmap of variation of
information between corpora for each corpus, topic count pair with numbers
superimposed on each square. Saves as vois_all.png.
