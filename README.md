This is the Triphone Balancer built by Christopher Shulby

Date: 01.12.2014


----Introduction-----

The purpose of this program is to phonetically balance sentences in a small corpus against sentences taken from a large text corpus.
In order to balance sentences three seperate files are needed:
1. a small corpus (could be empty if you have no sentences to start)
2. a large corpus
3. a histogram of triphones from the large corpus

all corpora must be given in the following format:
	"sentence to be balanced|## ss ee nn tt ee nn ss tt uu bb ii bb aa ll ae nn ss tt ##"

*note that there can be no empty line and each line must have at least one triphone
if there is only one phone then sentence delimiters like '##' would be accepted.
for example ## aa ## would be a valid triphone.

The histogram must be structured in a similar way as well and given as:
	12|ss aw nn
	10|pp aw ll
	 4|aw ll oo
	 2|nn aw nn
	 1|## aa ##

----Use-----

The program can be run by the following command:

	"python balance.py <small_corpus> <big_corpus> <path to store files>"

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

----Dependencies-----

This program requires

1. python
2. marisa trie which can be found at https://pypi.python.org/pypi/marisa-trie
