# -*- coding: iso-8859-15 -*-
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
import argparse
import signal
import internal_balancer

def makedirs():
    #print "making dirs if they don't already exist... "
    cmd="mkdir -p ./Files; mkdir -p ./tmp"
    p=subprocess.Popen(cmd,   shell=True, stdout=subprocess.PIPE)
    output, errors = p.communicate()


def menu():
    help= False
    var = raw_input('\n' + "please enter the current corpus file or \"help\": " + '\n')
    print '\n' + "    you entered", var + '\n'
    if var == "help":
        help= True
        print "Three arguments expected: " +'\n\n'+ "1. current_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line" + '\n' + "2. candidate_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line" + '\n'+ "3. <tmp_folder_name>" +  '\n\n'

    if not help:
        current_corpus_file= var
        var1 = raw_input('\n' + "please enter the big corpus file or \"help\": " + '\n')
        print '\n' + "    you entered", var1 + '\n'
        candidate_corpus_file= var1
        print "exectuting verification process on " + current_corpus_file + " as current_corpus_file and " + candidate_corpus_file + " as candidate_corpus_file " + '\n'

def copy_input(curCorpus,bigCorpus,excludedSentencesFile):
    current_corpus_file = curCorpus
    candidate_corpus_file = bigCorpus
    excluded_sentences_file = excludedSentencesFile
    shutil.copy('../' + current_corpus_file, 'Files/current_corpus_file')
    shutil.copy('../' + candidate_corpus_file, 'Files/candidate_corpus_file')
    shutil.copy('../' + excluded_sentences_file, 'Files/excluded_sentences_file')

def order_triphones(file_name):
    #print "grouping monophones to triphones in each sentence... "
    with open(file_name, "r") as corpus_file:
        lines = corpus_file.readlines()

    lines_phones = [line.split("|", 1)[1].strip() for line in lines]
    #triphones_sentences = [[phones[i:i+8] for i in range(0, len(phones) - 7, 3)] for phones in lines_phones]
    lines_phones_split=[phones.split() for phones in lines_phones]
    triphones_sentences = [[" ".join(phones_split[i:i+3]) for i in range(0, len(phones_split) - 2)] for phones_split in lines_phones_split]
    triphones = list(itertools.chain(*triphones_sentences))
    return triphones, triphones_sentences

def make_orig_hists(triphones):
    #print "currently on loop: " + str(loop) + '\n' + "making histogram... "
    with open('tmp/hist_small_orig', 'w') as f1:
        b = collections.Counter(triphones)
        for line in b.items():
            line_=str(line)
            line_=line_.replace("'","")
            line_=line_.replace(', ', '|')
            line_=line_.replace('(','')
            line_=line_.replace(')','')
            line=line_.strip()
            number=line.split('|')[1]
            phones=line.split('|')[0]
            line = number + "|" + phones
            f1.write(line +'\n')


def reordena_hists():
    f = open('../hist_big_orig', 'r')
    lines_orig = f.readlines()
    f.close

    f = open('tmp/hist_small_orig', 'r')
    lines_final = f.readlines()
    f.close

    f1 = open('tmp/hist_small_ord', 'w')
    f2 = open('tmp/saldo_small_ord', 'w')

    dict_final = {}
    for line in lines_final:
        line = line.strip()
        partes = line.split('|')
        if len(partes) == 2:
            dict_final[partes[1]] = partes[0]

    for line in lines_orig:
        line = line.strip()
        partes = line.split('|')
        if len(partes) == 2:
            if partes[1] in dict_final:
                numero = float(dict_final[partes[1]]) + 0.01
                #print line, float(dict_final[partes[1]])
            else:
                numero = 0.01
            number_to_get = 1.01 - int(numero)
            #print line, numero, number_to_get
            if number_to_get < 0:
                number_to_get = 0.01
            #print number_to_get, line
            f1.write(str(numero) + "|" + str(partes[1]) + '\n')
            f2.write(str(number_to_get) + "|" + str(partes[1]) + '\n')


def get_percents_big():

    #print "getting percentages of triphones from the original and final histograms... "

    with open('../hist_big_orig', 'r') as f:

        phones_percents_big_dict = {}

        lines = f.readlines()
        percents_big = np.zeros(len(lines), dtype=np.float)

        for line in lines:
            #print line
            attribs = line.strip().split("|")
            phones_percents_big_dict[attribs[1]] = float(attribs[0])

        values = []
        for key, value in phones_percents_big_dict.items():
            #  compute phone values
            values.append(value)

        return values


def get_percents_small(qtd_rels_big):
    #print "getting percents small... "
#
    current_weights = []
    saldo = []
    phones_rels_small_dict = {}
    with open('tmp/hist_small_ord', 'r') as f:
        lines = f.readlines()
        for line in lines:
            attribs = line.strip().split("|")
            phones_rels_small_dict[attribs[1]] = float(attribs[0])

        cont = 0
        for key, value in phones_rels_small_dict.items():
            #  compute phone values

            prop_big_small = math.log(qtd_rels_big[cont] + 1, 2) - value
            cont = cont + 1

            current_weights_line = str(str(prop_big_small) + "|" + key)
            current_weights.append(current_weights_line)

    with open('tmp/saldo_small_ord', 'r') as f1:
        lines_1 = f1.readlines()
        for line_1 in lines_1:
            line_1 = line_1.strip()
            saldo.append(line_1)

    return current_weights, saldo


def richest(weights, sentences):
    #print "sorting by richest sentences... "

    with open('Files/current_corpus_file', 'a') as f1, open('Files/excluded_sentences_file', 'a') as f_x:
        if "excluded_sent" not in "\n".join(sentences[:1]):
            f1.write("\n".join(sentences[:1]) +'\n')
        else:
            f_x.write("\n".join(sentences[:1]) +'\n')

    with open('Files/new_corpus_file', 'a') as f1:
        if "excluded_sent" not in "\n".join(sentences[:1]):
            f1.write("\n".join(sentences[:1]) +'\n')
        else:
            pass

    sentences = sentences[1:]
    weights = weights[1:]

    with open('Files/candidate_corpus_file', 'w') as f1:
        f1.write("\n".join(sentences) + '\n')

def processBalancing(current_corpus, big_corpus, automode):
    signal.signal(signal.SIGINT, signal_handler)

    global currentCorpus
    global candidateCorpus
    currentCorpus = current_corpus
    candidateCorpus = big_corpus

    if not os.path.exists(currentCorpus):
        sys.exit("Error: " + currentCorpus + " file not found.")

    if not os.path.exists(candidateCorpus):
        sys.exit("Error: " + candidateCorpus + " file not found.")

    global loop
    loop = 1
    if (automode == True):
        loop_parameter = 10001
    else:
        loop_parameter = 4001
    #print "start time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #sys.argv[1:] = [current_corpus, big_corpus, foldername]

    current_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    current_corpus_path = current_corpus.split("/")
    length_current_corpus_path = len(current_corpus_path)
    excluded_sentences_file = ""
    if (length_current_corpus_path == 1):
        if not os.path.exists("./excluded_sentences_file"):
            print "create excluded files"
            os.mknod("./excluded_sentences_file")
        excluded_sentences_file="excluded_sentences_file"
    else:
        excluded_sentences_path = ''.join(current_corpus_path[:length_current_corpus_path-1])
        excluded_sentences_file = excluded_sentences_path + "/excluded_sentences_file"
        if not os.path.exists(excluded_sentences_file):
            print "create excluded files"
            os.mknod(excluded_sentences_file)

    temp_path = current_path+"/temp"
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    os.chdir(temp_path)
    makedirs()
    #print "Iteration number: " + str(loop) + '\n'
    copy_input(current_corpus, big_corpus, excluded_sentences_file)
    qtd_rels = get_percents_big()
    while loop < loop_parameter:
        try:
            print "Iteration number: " + str(loop) + '\n'
            print "time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            triphones, triphones_sentences = order_triphones('Files/current_corpus_file')
            make_orig_hists(triphones)
            reordena_hists()
            current_weights, saldo = get_percents_small(qtd_rels)
            triphones, triphones_sentences = order_triphones('Files/candidate_corpus_file')
            weights, sentences = internal_balancer.weight_sents(triphones_sentences, current_weights, saldo, automode)
            richest(weights, sentences)
            loop = loop +1
            #print "time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        except RuntimeError as err:
            print (err.args)
            shutil.copy('Files/candidate_corpus_file' , '../' + candidateCorpus)
            shutil.copy('Files/current_corpus_file' , '../' + currentCorpus)
            shutil.copy('Files/excluded_sentences_file' , '../' + excluded_sentences_file)
            sys.exit(1)
        except:
            print "Abnormal behaviour..."
    if loop == loop_parameter:
            #print "end time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print "exiting... "
            exit

def signal_handler(signal, frame):
    raise RuntimeError('Exit with CTRL+C pressed!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is the Triphone Balancer.')
    parser.add_argument('-c','--current', help='Current_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line)', required=True)
    parser.add_argument('-d','--candidate', help='Candidate_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line)', required=True)
    parser.add_argument('--auto', dest='auto', help='Run in automatic mode', action='store_true')
    parser.add_argument('--no-auto',dest='auto',help='Run in manual mode (Default Mode)', action='store_false')
    parser.set_defaults(auto=False)

    if len(sys.argv[1:])==0:
        parser.print_help()
        sys.exit(1)
    args = vars(parser.parse_args())

    processBalancing(args["current"], args["candidate"], args["auto"])
