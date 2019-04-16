Description
===========
This is the Triphone Balancer built by Christopher Shulby for his PhD Thesis

Original Date:

    01/12/2014

Updates:

    25/04/2018: - fix related to relative paths;
    24/05/2018: - keep current_corpus_file / candidate_corpus_file records when script execution is aborted;
                - created excluded_sentences_file to store sentences excluded;
                - created a single script;
    15/04/2019: - added a version for python 3.5


Introduction
------------

The purpose of this program is to phonetically balance sentences in a small corpus against sentences taken from a large text corpus.
In order to balance sentences three seperate files are needed:
1. a small corpus (could be empty if you have no sentences to start)
2. a large corpus
3. a histogram of triphones from the large corpus

all corpora must be given in the following format:

    "sentence to be balanced|## ss ee nn tt ee nn ss tt uu bb ii bb aa ll ae nn ss tt ##"

* note that there can be no empty line and each line must have at least one triphone
if there is only one phone then sentence delimiters like '##' would be accepted.
for example ## aa ## would be a valid triphone.

The histogram must be structured in a similar way as well and given as:

    12|ss aw nn
    10|pp aw ll
     4|aw ll oo
     2|nn aw nn
     1|## aa ##

Usage
-----
The program can be run by the following command:

    balance.py [-h] -c CURRENT -d CANDIDATE [--auto] [--no-auto]

    This is the Triphone Balancer.

    optional arguments:
    -h, --help            show this help message and exit
    -c CURRENT, --current CURRENT
                          Current_corpus_file (This file should contain two
                          columns separated by a "|", the first should sentences
                          (orthography), and second should contain the
                          corresponding phonetic transcription, for example
                          "Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac
                          vv ic aa zh en", one sentence per line)
    -d CANDIDATE, --candidate CANDIDATE
                          Candidate_corpus_file (This file should contain two
                          columns separated by a "|", the first should sentences
                          (orthography), and second should contain the
                          corresponding phonetic transcription, for example
                          "Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac
                          vv ic aa zh en", one sentence per line)
    --auto                Run in automatic mode
    --no-auto             Run in manual mode (Default Mode)


The program will then display the number of sentences in the corpus (some may be discarded if they have no statistical significance)
and then promt the user to respond how many sentences they would like to see on the screen at a time.
If the user selects "10" he/she will see something like this:

    -----------------------    -----------------------------------------
    0       9.99963607788       makeup
    1       9.99518718719       rolling
    2       9.99479675293       repeat
    3       9.99214506149       absorb
    4       9.99209594727       vaccine
    5       9.98358974457       derive
    6       9.9833876746        backyard
    7       9.98123283386       ideal
    8       9.98123283386       ideal
    9       9.98092041016       adjust
    -----------------------    -----------------------------------------

Here the sentence ID is given in the first column, the score in the second and the sentence itself in the third.

The user will then be asked to select one of the sentences, in the case above valid annswers would fronge from 0-9.
One the user has made a selection he may either accept the sentence 
(in this case it will be recorded in Files/new_corpus_file and Files/current_corpus_file)
or exclude the sentence (in this case it will be discarded and will no longer be an option)

This process will loop for as long as the user wishes until he/she has designed a full balanced corpus.

Dependencies
-----------
This program requires:

1. python
2. marisa trie which can be found at https://pypi.python.org/pypi/marisa-trie
3. argparse
4. argcomplete

Module dependencies are summarized in requirements.txt

Run:

    sudo pip install -r requirements.txt
    sudo activate-global-python-argcomplete # open a new terminal window and run balance.py
