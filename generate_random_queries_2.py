"""
Sample usage:
python3 generate_random_queries.py --num_queries 2 --length 7
# Will generate 2 queries of length 7
"""
import argparse
import pandas as pd
import nltk
from nltk.tokenize import RegexpTokenizer

df = pd.read_csv('Full_df.csv')

parser = argparse.ArgumentParser(description="Generates random queries")
parser.add_argument('--num_queries', help="Number of queries to generate", default=2, type=int)
parser.add_argument('--length', help="Number of words in queries", default=5, type=int)

def length_sentence(sentence):
    tokenizer = RegexpTokenizer(r'\w+')

    return len(tokenizer.tokenize(sentence))

def generate_queries(num_queries, query_length, df=df):
    queries = list()

    for i in range(len(df)):
        sentences = nltk.sent_tokenize(df.iloc[i]["Snippet"])
        for sentence in sentences:
            if(length_sentence(sentence) == query_length):
                queries.append(sentence)
                if(len(queries) == num_queries): return queries

    return queries


if(__name__ == "__main__"):
    args = parser.parse_args()

    query_test_set = generate_queries(df, args.num_queries, args.length)
    print(query_test_set)
