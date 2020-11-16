"""
Sample usage:
python3 spell_checker.py --word Innovation
# Will check for word innovation in corpus
"""

import argparse
import pickle
import nltk
from nltk.corpus import stopwords
import enchant
import re

parser = argparse.ArgumentParser(description="Spelling checker")
parser.add_argument('--word', help="Word to check corpus with", default="Climate change")

stopwords = set(stopwords.words('english'))

with open('word_count_dict.pkl', 'rb') as f:
	word_count_dict = pickle.load(f)

def spell_checker_word(check_word, word_count_dict=word_count_dict):
    word = re.sub(r'[^\w\s]', '', check_word)
    if word in word_count_dict:
        return (check_word, 0, True)

    elif word in stopwords:
        return (check_word, 0, True)

    else:
        best_word = '';
        best_word_count = 0
        best_word_ed = float('inf')

        for key_word in word_count_dict.keys():
            ed = enchant.utils.levenshtein(word, key_word)

            if(ed < best_word_ed):
                best_word_ed = ed
                best_word = key_word
                best_word_count = word_count_dict[key_word]

            elif(ed == best_word_ed):
                if(word_count_dict[key_word] > best_word_count):
                    best_word_ed = ed
                    best_word = key_word
                    best_word_count = word_count_dict[key_word]

        return (best_word, best_word_ed, False)

def spell_checker_sentence(sentence, word_count_dict=word_count_dict):
	spelling_fail = False
	correct_spelling = list()
	for word in nltk.word_tokenize(sentence.lower()):
		check = spell_checker_word(word, word_count_dict)
		if check[2] == False:
			spelling_fail = True
		correct_spelling.append(check[0])
	corrected_query = ' '.join(correct_spelling)
	return (corrected_query, spelling_fail)

if(__name__ == "__main__"):
    args = parser.parse_args()

    print(spell_checker_sentence(args.word, word_count_dict))
