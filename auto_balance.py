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

def makedirs():
	#print "making dirs if they don't already exist... "
	cmd="mkdir -p ./Files; mkdir -p ./tmp"																	   
	p=subprocess.Popen(cmd,   shell=True, stdout=subprocess.PIPE)							  
	output, errors = p.communicate()


def menu():
	help= False
	var = raw_input('\n' + "please enter the current corpus file or \"help\": " + '\n')
	print '\n' + "	you entered", var + '\n'
	if var == "help":
		help= True
		print "Two arguments expected: " +'\n\n'+ "1. current_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line" + '\n' + "2. candidate_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line" + '\n' +'\n\n' 
	
	if not help:
		current_corpus_file= var
		var1 = raw_input('\n' + "please enter the big corpus file or \"help\": " + '\n')
		print '\n' + "	you entered", var1 + '\n'
		candidate_corpus_file= var1
		print "exectuting verification process on " + current_corpus_file + " as current_corpus_file and " + candidate_corpus_file + " as candidate_corpus_file " + '\n'

def copy_input():	
	current_corpus_file = sys.argv[1]
	candidate_corpus_file = sys.argv[2]
	shutil.copy('../' + current_corpus_file, 'Files/current_corpus_file')
	shutil.copy('../' + candidate_corpus_file, 'Files/candidate_corpus_file')

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



def file_to_trie(lista):
	Dict = {}
	for line in lista:
		value, triphone = line.strip().split('|')
		triphone = unicode(triphone.strip(), 'utf-8')
		value = (float(value), )
		Dict[triphone] = value
	
	# return marisa_trie.BytesTrie(Dict.items())
	return marisa_trie.RecordTrie("<f", Dict.items())

# busca
def weight_sents(triphones_sentences, current_weights, saldo):
	#print "weighing sentences in big corpus... "
	weighted_sents = []
	weighted_sents_ = []
	new_weighted_sents = []
	added_weights = []
	sentences = []

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

					current_weight += weight# + (saldo*10.)
				except KeyError:
					pass
			added_weight = current_weight/ (len(triphones_list))

			if added_weight > 0.02:
				weighted_sent = str(added_weight) + "|" + sentence + "|" + transcription
				weighted_sents_.append(weighted_sent)

	for x in sorted(weighted_sents_ , reverse=True):
		weighted_sents.append(x)

#	print "time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#########################################start auto balancing

	for i in range(0,len(weighted_sents)):
		sent=weighted_sents[i].strip().split('|')[1] +"|"+weighted_sents[i].strip().split('|')[2]
		sentences.append(sent)
		added_weight = float(weighted_sents[i].strip().split('|')[0])
		added_weights.append(added_weight)

	return added_weights, sentences

#########################################end auto balancing
#########################################start manual balacing
'''

	valid_total = False
	while not valid_total:
		print "\n------------------------\nCorpus has: " + str(len(weighted_sents)) + " sentences \n------------------------\n\n"
		num_sents = raw_input('\n' + "please enter the number of sentences you would like to see: " + '\n')
		if int(num_sents) >= 0 and int(num_sents) < len(weighted_sents):
			valid_total = True
			sents_to_print = '\n'.join(weighted_sents[:int(num_sents)])
			count = 0
			print '\n\n' + '-----------------------    -----------------------------------------' + '\n'
			for h in range(0,int(num_sents)):
				print str(count).ljust(8) + str(weighted_sents[h].strip().split('|')[0]).ljust(20) + weighted_sents[h].strip().split('|')[1]
				count = count + 1
			print '\n' + '-----------------------    -----------------------------------------' + '\n\n'
			valid_0 = False
			while not valid_0:
				selected_sent = raw_input('\n' + "please select a NUMBER of a sentence you would like to accept or exclude: " + '\n')
				if int(selected_sent) >= 0 and int(selected_sent) < int(num_sents):
					valid_0 = True
					valid = False
					while not valid:
						choice = raw_input('\n' + "1) (a)ccept or 2) (e)xclude? " + '\n')
						accept = set(['a','1', ''])
						exclude = set(['e','2'])
						if choice == 'a':
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

						elif choice == 'e' :
							print "Sentence number " + str(selected_sent) + " excluded \n\n"
							sentences.append("excluded_sent|## ## ##")
							for i in range(0,len(weighted_sents)):
								if i != int(selected_sent):
									sent=weighted_sents[i].strip().split('|')[1] +"|"+weighted_sents[i].strip().split('|')[2]
									sentences.append(sent)
									added_weight = float(weighted_sents[i].strip().split('|')[0])
									added_weights.append(added_weight)
									valid = True

						else:
							print "not a valid choice... "
							valid = False
				else:
					"sentence number not valid\n\nplease enter a valid number\n"
					valid_0 = False
		else:
			"not a valid number for the size of this corpus\n\nplease enter a valid number\n"
			valid_total = False

	return added_weights, sentences

#########################################end manual balacing	
'''


def richest(weights, sentences):
	#print "sorting by richest sentences... "
																		 
	with open('Files/current_corpus_file', 'a') as f1:
		if "excluded_sent" not in "\n".join(sentences[:1]):
			f1.write("\n".join(sentences[:1]) +'\n')
		else:
			pass

	with open('Files/new_corpus_file', 'a') as f1:
		if "excluded_sent" not in "\n".join(sentences[:1]):
			f1.write("\n".join(sentences[:1]) +'\n')
		else:
			pass

	sentences = sentences[1:]
	weights = weights[1:]

	with open('Files/candidate_corpus_file', 'w') as f1:
		f1.write("\n".join(sentences) + '\n')

def processBalancing(current_corpus, big_corpus, foldername):
 	global loop
	loop = 1
	#print "start time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	sys.argv[1:] = [current_corpus, big_corpus, foldername]

	os.chdir(sys.argv[3]) #TODO: remove this

	makedirs()
	if len(sys.argv) != 4:
		print "Three arguments expected: " +'\n\n'+ "1. current_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line" + '\n' + "2. candidate_corpus_file (This file should contain two columns separated by a \"|\", the first should sentences (orthography), and second should contain the corresponding phonetic transcription, for example \"Programe sua viagem|pp rd oo gg rd an mm ic ss uu ac vv ic aa zh en\", one sentence per line" + '\n' +"3. A folder to save the files, you can name it anything you would like, <folder_a> for example." +'\n\n' 
	else:
		#print "Iteration number: " + str(loop) + '\n'	
		copy_input()
		qtd_rels = get_percents_big()
		while loop < 10001: 
			print "Iteration number: " + str(loop) + '\n'
			print "time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			triphones, triphones_sentences = order_triphones('Files/current_corpus_file')
			make_orig_hists(triphones)
			reordena_hists()
			current_weights, saldo = get_percents_small(qtd_rels)
			triphones, triphones_sentences = order_triphones('Files/candidate_corpus_file')
			weights, sentences = weight_sents(triphones_sentences, current_weights, saldo)
			richest(weights, sentences)
			loop = loop +1
			#print "time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		if loop == 10001:
				#print "end time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				print "exiting... "
				exit

if __name__ == "__main__":
	processBalancing(sys.argv[1], sys.argv[2], sys.argv[3])

