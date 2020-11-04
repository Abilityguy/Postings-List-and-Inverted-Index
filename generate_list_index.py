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

inverted_index = dict()
count_dict = dict()
count = 0

counter = 1
for document in os.listdir('archive/TelevisionNews/'):
    documentId[document] = counter
    counter += 1
    
for file in os.listdir('archive/TelevisionNews/'): #Change this to the directory with all csv files
    if file.endswith(".csv"):
        try:
            df = pd.read_csv(os.path.join('archive/TelevisionNews/', file), index_col=None, header=0)
            
            df['Snippet'] = df["Snippet"].apply(lambda x: x.lower())
            df['Snippet'] = df['Snippet'].apply(lambda x: tokenizer.tokenize(x))
            df['Snippet'] = df['Snippet'].apply(lambda x: remove_stop_words(x, stop_words))
            df['Snippet'] = df['Snippet'].apply(lambda x: lemmatize_words(x))
            
            for doc in range(len(df)):
                for row in range(len(df.iloc[doc]["Snippet"])):
                    try:
                        if(inverted_index[df.iloc[doc]["Snippet"][row]][-1] == documentId[file]):
                            continue
                        inverted_index[df.iloc[doc]["Snippet"][row]].append(documentId[file])

                        count_dict[df.iloc[doc]["Snippet"][row]] += 1
                    except:
                        inverted_index[df.iloc[doc]["Snippet"][row]] = [documentId[file]]
                        count_dict[df.iloc[doc]["Snippet"][row]] = 1
        except:
            print("Skipped file: ", file) #Some error in the file, maybe it is empty
    else:
        print("Invalid file: ", file)
        
postings_lists_list = [0]*(len(list(documentId.keys()))+1)
count_dict = dict()

for file in os.listdir('archive/TelevisionNews/'): #Change this to the directory with all csv files
    if (file == 'CNN.200910.csv'):
        continue
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join('archive/TelevisionNews/', file), index_col=None, header=0)
            
        df['Snippet'] = df["Snippet"].apply(lambda x: x.lower())
        df['Snippet'] = df['Snippet'].apply(lambda x: tokenizer.tokenize(x))
        df['Snippet'] = df['Snippet'].apply(lambda x: remove_stop_words(x, stop_words))
        df['Snippet'] = df['Snippet'].apply(lambda x: lemmatize_words(x))

        postings_list = dict()
        for doc in range(len(df)):
            for row in range(len(df.iloc[doc]["Snippet"])):
                try:
                    if(postings_list[df.iloc[doc]["Snippet"][row]][-1][-1][0] == doc):
                        postings_list[df.iloc[doc]["Snippet"][row]][-1][-1][-1].append(row)
                    else:
                        postings_list[df.iloc[doc]["Snippet"][row]][-1].append([doc, [row]])

                    postings_list[df.iloc[doc]["Snippet"][row]][0] += 1

                except:
                    postings_list[df.iloc[doc]["Snippet"][row]] = [1, [[doc, [row]]]]
                    
            postings_lists_list[documentId[file]] = postings_list
    else:
        print("Invalid file: ", file)
        
for key in postings_list.keys():
    inverted_index[key] = [count_dict[key], postings_list[key]]

with open(os.path.join(args.dst, 'postings_lists_list.pkl'), 'wb') as f:
    print("Saving list of posting lists")
    pickle.dump(postings_lists_list, f)
    del postings_lists_list

with open(os.path.join(args.dst, 'inverted_index.pkl'), 'wb') as f:
    print("Saving inverted index")
    pickle.dump(inverted_index, f)
    del inverted_index
