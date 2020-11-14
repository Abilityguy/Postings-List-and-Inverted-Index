"""
Sample usage:
python3 spell_checker.py --word Innovation 
# Will check for word innovation in corpus
"""

import argparse
import pickle
from nltk.corpus import stopwords
import enchant

parser = argparse.ArgumentParser(description="Spelling checker")
parser.add_argument('--word', help="Word to check corpus with", default="modi")

stopwords = set(stopwords.words('english'))

def spell_checker(word, word_count_dict):
    word = word.lower()

    if word in word_count_dict:
        return (word, 0, True)

    elif word in stopwords:
        return (word, 0, True)

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

if(__name__ == "__main__"):
    args = parser.parse_args()

    with open('word_count_dict.pkl', 'rb') as f:
        word_count_dict = pickle.load(f)

    print(spell_checker(args.word, word_count_dict))

