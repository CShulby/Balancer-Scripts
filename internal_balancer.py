import os
import shutil
import sys
import subprocess
from subprocess import Popen, PIPE
from operator import itemgetter
from datetime import datetime
import collections
import numpy as np
import itertools
import marisa_trie
import time
import math

def file_to_trie(lista):
    Dict = {}
    for line in lista:
        value, triphone = line.strip().split('|')
        triphone = unicode(triphone.strip(), 'utf-8')
        value = (float(value), )
        Dict[triphone] = value

    # return marisa_trie.BytesTrie(Dict.items())
    return marisa_trie.RecordTrie("<f", Dict.items())

def weight_sents(triphones_sentences, current_weights, saldo, isAutoMode):
    #print "weighing sentences in big corpus... "
    weighted_sents = []
    weighted_sents_ = []
    new_weighted_sents = []
    added_weights = []
    sentences = []

    if (isAutoMode == True):
        weightCompared = 0.02
    else:
        weightCompared = 0.0000000000000000000000000000001

    current_weights = file_to_trie(current_weights)
    saldo_small_ord = file_to_trie(saldo)

    with open('Files/candidate_corpus_file','r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            sentence = line.split('|')[0]
            transcription = line.split('|')[1]
            triphones_list = triphones_sentences[i]
            current_weight = 0
            for triphone in triphones_list:
                #print triphone
                try:
                    weight = current_weights[triphone][0][0]
                    saldo = saldo_small_ord[triphone][0][0]
                    #print triphone, weight

                    if (isAutoMode == True):
                        current_weight += weight# + (saldo*10.)
                    else:
                        current_weight += weight + 1.#(saldo * 10.)
                except KeyError:
                    pass
            added_weight = current_weight/ (len(triphones_list))

            if added_weight > weightCompared:
                weighted_sent = str(added_weight) + "|" + sentence + "|" + transcription
                weighted_sents_.append(weighted_sent)

    for x in sorted(weighted_sents_, key=lambda x: -float(x.split('|')[0])):
        weighted_sents.append(x)

    #print weighted_sents[1:10]

#    print "time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    if (isAutoMode == True):
    #########################################start auto balancing
        for i in range(0,len(weighted_sents)):
            sent=weighted_sents[i].strip().split('|')[1] +"|"+weighted_sents[i].strip().split('|')[2]
            sentences.append(sent)
            added_weight = float(weighted_sents[i].strip().split('|')[0])
            added_weights.append(added_weight)

        return added_weights, sentences

    #########################################end auto balancing
    else:
        #########################################start manual balacing
        print "\n------------------------\nCorpus has: " + str(len(weighted_sents)) + " sentences \n------------------------\n\n"
        num_sents = ''
        while not num_sents.isdigit() or int(num_sents) <= 0 or int(num_sents) > len(weighted_sents):
            num_sents = raw_input('\n' + "Please enter the number of sentences you would like to see (1 to " + str(len(weighted_sents)) + "): " + '\n')
        num_sents = int(num_sents)

        sents_to_print = '\n'.join(weighted_sents[:num_sents])
        count = 0
        print '\n\n' + '-----------------------    -----------------------------------------' + '\n'
        for h in range(0,num_sents):
            print str(count).ljust(8) + str(weighted_sents[h].strip().split('|')[0]).ljust(20) + weighted_sents[h].strip().split('|')[1]
            count = count + 1
        print '\n' + '-----------------------    -----------------------------------------' + '\n\n'
        selected_sent = ''
        while not selected_sent.isdigit() or int(selected_sent) < 0 or int(selected_sent) >= num_sents:
            selected_sent = raw_input('\n' + "Please select a number of the sentence you would like to accept or exclude (0 to " + str(num_sents-1) + "): " + '\n')
        selected_sent = int(selected_sent)
        valid = False
        while not valid:
            choice = raw_input('\n' + "1) (a)ccept or 2) (e)xclude? " + '\n')
            if choice in ['a', '1']:
                print "Sentence number " + str(selected_sent) + " accepted \n\n"
                accepted_sent = str(weighted_sents[int(selected_sent)]).strip().split('|')[1]+"|"+str(weighted_sents[int(selected_sent)]).strip().split('|')[2]
                #print ">>>>>>>>>>>>>>>>>>>>>>" + accepted_sent
                sentences.append(accepted_sent)
                added_weight = float(str(weighted_sents[int(selected_sent)]).strip().split('|')[0])
                added_weights.append(added_weight)
                for i in range(0,len(weighted_sents)):
                    if i != int(selected_sent):
                        sent=weighted_sents[i].strip().split('|')[1] +"|"+weighted_sents[i].strip().split('|')[2]
                        sentences.append(sent)
                        added_weight = float(weighted_sents[i].strip().split('|')[0])
                        added_weights.append(added_weight)
                        valid = True

            elif choice in ['e', '2']:
                print "Sentence number " + str(selected_sent) + " excluded \n\n"
                excluded_sent = str(weighted_sents[int(selected_sent)]).strip()
                sentences.append("excluded_sent|"+excluded_sent)
                for i in range(0,len(weighted_sents)):
                    if i != int(selected_sent):
                        sent=weighted_sents[i].strip().split('|')[1] +"|"+weighted_sents[i].strip().split('|')[2]
                        sentences.append(sent)
                        added_weight = float(weighted_sents[i].strip().split('|')[0])
                        added_weights.append(added_weight)
                        valid = True

            else:
                print "not a valid choice... \n"

        return added_weights, sentences
    #########################################end manual balacing
