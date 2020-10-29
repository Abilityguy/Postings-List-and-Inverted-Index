"""
A program to preprocess text and generate postings list and inverted index

Sample usage:
python3 generate_list_index.py --lemmatize --stop_words data/saved.csv .
"""

import argparse
import os
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import pickle

parser = argparse.ArgumentParser(description="Process data and generate postings list and inverted index")
parser.add_argument('src', help="Path to csv file")
parser.add_argument('dst', help="Destination folder to save the postings list and inverted index")
parser.add_argument('--stem', default=False, action="store_true", help="Stem the words before generating index")
parser.add_argument('--lemmatize', default=False, action="store_true", help="Lemmatize words before generating index")
parser.add_argument('--stop_words', default=False, action="store_true", help="Remove stop words from the corpus")
args = parser.parse_args()

df = pd.read_csv(args.src)
tokenizer = RegexpTokenizer(r'\w+') #It retains only words and eliminates punctuations in words
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
postings_list = dict()
inverted_index = dict()
count_dict = dict()

def remove_stop_words(x, stop_words):
    return [word for word in x if word not in stop_words]

def lemmatize_words(x):
    return [lemmatizer.lemmatize(word) for word in x]

df['Snippet'] = df["Snippet"].apply(lambda x: x.lower())
df['Snippet'] = df['Snippet'].apply(lambda x: tokenizer.tokenize(x))

if (args.stop_words):
    print("Removing stop words")
    df['Snippet'] = df['Snippet'].apply(lambda x: remove_stop_words(x, stop_words))

if (args.stem):
    print("Stemming")
    df['Snippet'] = df['Snippet'].apply(lambda x: tokenizer.tokenize(x))

if (args.lemmatize):
    print("Lemmatizing")
    df['Snippet'] = df['Snippet'].apply(lambda x: lemmatize_words(x))

for i in range(len(df)):
    for j in range(len(df.iloc[i]["Snippet"])):
        try:
            if(postings_list[df.iloc[i]["Snippet"][j]][-1][0] == i):
                postings_list[df.iloc[i]["Snippet"][j]][-1][1].append(j)
            else:
                postings_list[df.iloc[i]["Snippet"][j]].append([i,[j]])

            count_dict[df.iloc[i]["Snippet"][j]] += 1
        except:
            postings_list[df.iloc[i]["Snippet"][j]] = [[i,[j]]]
            count_dict[df.iloc[i]["Snippet"][j]] = 1

for key in postings_list.keys():
    inverted_index[key] = [count_dict[key], postings_list[key]]

with open(os.path.join(args.dst, 'postings_list.pkl'), 'wb') as f:
    print("Saving posting list")
    pickle.dump(postings_list, f)
    del postings_list

with open(os.path.join(args.dst, 'inverted_index.pkl'), 'wb') as f:
    print("Saving inverted index")
    pickle.dump(inverted_index, f)
    del inverted_index
