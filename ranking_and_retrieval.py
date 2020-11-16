'''
Run $python3 ranking_and_retrieval.py --query "query"
'''

import pickle
import math
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import pandas as pd
import argparse
import re

parser = argparse.ArgumentParser(description="Ranking and retrieval")
parser.add_argument('--query', help="Enter query", default="", type=str)

tokenizer = RegexpTokenizer(r'\w+') #It retains only words and eliminates punctuations in words
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def remove_stop_words(x, stop_words):
    return [word for word in x if word not in stop_words]

def lemmatize_words(x):
    return [lemmatizer.lemmatize(word) for word in x]

with open('postings_list.pkl', 'rb') as f:
    postings_list = pickle.load(f)

with open('inverted_index.pkl', 'rb') as f:
    inverted_index = pickle.load(f)

with open('documentId.pkl', 'rb') as f:
    document_ids = pickle.load(f)

try:
    with open('document_words_count.pkl', 'rb') as f:
        document_words_count = pickle.load(f)
except:
    document_words_count = {}
    for i in postings_list:
        for j in postings_list[i]:
            if j[0] not in document_words_count:
                document_words_count[j[0]] = j[1]
            else:
                document_words_count[j[0]] += j[1]
    pickle.dump(document_words_count, open("document_words_count.pkl","wb"))

try:
    with open('tf_dic.pkl', 'rb') as f:
        tf_dic = pickle.load(f)
except:
    tf_dic = {}
    for i in postings_list:
        for j in postings_list[i]:
            tf_dic[(i,j[0])] = (j[1]/document_words_count[j[0]])
    pickle.dump(tf_dic, open("tf_dic.pkl","wb"))

try:
    with open('idf_dic.pkl', 'rb') as f:
        idf_dic = pickle.load(f)
except:
    num_docs = len(document_words_count)
    idf_dic = {}
    for i in inverted_index:
        idf_dic[i] = 1 + math.log(num_docs/len(inverted_index[i]))
    pickle.dump(idf_dic, open("idf_dic.pkl","wb"))

try:
    with open('tf_idf_dic.pkl', 'rb') as f:
        tf_idf_dic = pickle.load(f)
except:
    tf_idf_dic = {}
    for i in tf_dic:
        tf_idf_dic[i] = tf_dic[i]*idf_dic[i[0]]
    pickle.dump(tf_idf_dic, open("tf_idf_dic.pkl","wb"))

def tfidf_search(search_string, number_of_results):
    query = search_string
    querywc = []
    query = query.lower()
    query = query.split()
    for word in query:
        if '*' in word:
            querywc.append(word)
            query.remove(word)
    query = ' '.join(query)
    query = tokenizer.tokenize(query)
    query = remove_stop_words(query, stop_words)
    query = lemmatize_words(query)

    count_dic = {}
    for i in query:
        if i not in count_dic:
            count_dic[i] = 1
        else:
            count_dic[i] += 1

    num_query_words = len(query + querywc)
    tfidf_query_dic = {}

    for k in querywc:
            r = '^'+k.replace('*', '.*')+'$'
            corr = []
            for j in idf_dic:


                if re.search(r, j):


                    corr.append(j)
            l = 1/len(corr)
            for j in corr:
                if j not in count_dic:
                    count_dic[j] = l
                else:
                    count_dic[j] += l

    for i in count_dic:

        tfidf_query_dic[i] = (count_dic[i]/num_query_words)*(idf_dic[i])

    sum_of_squares1 = 0
    for i in tfidf_query_dic:
        sum_of_squares1 += pow(tfidf_query_dic[i],2)
    modulus1 = pow(sum_of_squares1,0.5)
    if modulus1 == 0:
        modulus1 = 1

    matching_docs = []
    dot_product = 0
    nums = []

    for i in document_words_count.keys():
        dot_product = 0
        nums = []
        for j in count_dic:
            if (j,i) in tf_idf_dic:

                dot_product += tfidf_query_dic[j]*tf_idf_dic[(j,i)]
                nums.append(tf_idf_dic[(j,i)])

        sum_of_squares2 = 0
        for j in nums:
            sum_of_squares2 += pow(j,2)
        modulus2 = pow(sum_of_squares2, 0.5)
        if modulus2 == 0:
            modulus2 = 1
        if dot_product!=0:
            if dot_product/(modulus1*modulus2)>0.1:
                matching_docs.append((i, dot_product/(modulus1*modulus2)))

    matching_docs.sort(key = lambda x: x[1], reverse = True)

    search_results = []
    for j in matching_docs[:number_of_results]:
        i = j[0]
        csv_id = i//10000
        row_id = i%10000
        df = pd.read_csv("data/"+document_ids[csv_id])
        row = df.iloc[row_id]
        search_results.append([document_ids[csv_id],row['URL'],row['Snippet']])
    # for result in search_results:
    #     print('\n'.join(result))
    #     print('-'*10, '*', '-'*10)
    pickle.dump(search_results, open("search_results.pkl","wb"))
    return search_results

if __name__=="__main__":
    args = parser.parse_args()
    print(tfidf_search(args.query,20))
