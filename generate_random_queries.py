"""
Sample usage:
python3 generate_random_queries.py --num_queries 2 --length 7
# Will generate 2 queries of length 7
"""
import argparse
import pickle
import numpy as np

parser = argparse.ArgumentParser(description="Generates random queries")
parser.add_argument('--num_queries', help="Number of queries to generate", default=1, type=int)
parser.add_argument('--length', help="Number of words in queries", default=5, type=int)

def generate_queries(words, word_counts, num_queries, length):
    queries = list()

    total_counts = sum(word_counts)
    word_counts = [x/total_counts for x in word_counts]
    word_indices = list(range(0,len(words)))

    queries = list()
    for i in range(num_queries):
        queries.append("")
        for j in range(length):
            if j!=length-1:
                random_word_index = np.random.choice(word_indices, p=word_counts)
                queries[-1] += words[random_word_index]+" "
            else:
                random_word_index = np.random.choice(word_indices, p=word_counts)
                queries[-1] += words[random_word_index]

    return queries


if(__name__ == "__main__"):
    args = parser.parse_args()

    with open('word_count_dict.pkl', 'rb') as f:
        word_count_dict = pickle.load(f)

    words = list(word_count_dict.keys())
    word_counts = list(word_count_dict.values())
    query_test_set = generate_queries(words, word_counts, args.num_queries, args.length)
    print(query_test_set)