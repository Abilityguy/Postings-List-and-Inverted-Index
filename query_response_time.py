import generate_random_queries_2
from query_ElastiSearch import elastic_search
from tfidf_model import tfidf_search
import wordembedding_search
import boolean_query_model
import pickle
import requests
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english')) - {'and', 'or', 'not'}
from timeit import default_timer as timer

def avg_time(queries, query_length, method=1):
    if(method == 1):
        times_list = list()
        for query in queries:
            start = timer()
            tfidf_results = tfidf_search(query,20)
            end = timer()
            times_list.append(end-start)
        print("Avg time taken for method", method, "at query length ", query_length, ": ", sum(times_list)/len(times_list), "seconds")

    elif(method == 2):
        with open('document_vectors/document_vectors.pkl', 'rb') as f:
            document_vectors = pickle.load(f)
        with open('documentId.pkl', 'rb') as f:
            document_id = pickle.load(f)

        times_list = list()
        for query in queries:
            start = timer()
            similarity_list = wordembedding_search.search(query, document_vectors, 20)
            wordembedding_search.retrieve_documents(similarity_list, document_id)
            end = timer()
            times_list.append(end-start)
        print("Avg time taken for method", method, "at query length ", query_length, ": ", sum(times_list)/len(times_list), "seconds")

    elif(method == 3):
        times_list = list()
        counter = 0
        for query in queries:
            boolean_query = list()
            for word in query.lower().split():
                if word not in ('and','or','not'):
                    boolean_query.append(word)
                    boolean_query.append('and')

            boolean_query.pop() #remove the last 'and'
            boolean_query = ' '.join(boolean_query)

            start = timer()
            boolean_results = boolean_query_model.search(query)
            end = timer()
            times_list.append(end-start)
            counter += 1
        print("Avg time taken for method", method, "at query length ", query_length, ": ", sum(times_list)/len(times_list), "seconds")

    elif(method == 4):
        times_list = list()
        for query in queries:
            start = timer()
            elastic_results = elastic_search(query, 20)
            end = timer()
            times_list.append(end-start)
        print("Avg time taken for method", method, "at query length ", query_length, ": ", sum(times_list)/len(times_list), "seconds")

    elif(method == 5):
        times_list = list()
        for query in queries:
            start = timer()
            requests.get("http://localhost:8983/solr/AIR_Project/select?q=snippet:\""+query+"\"&wt=json").text
            end = timer()
            times_list.append(end-start)
        print("Avg time taken for method", method, "at query length ", query_length, ": ", sum(times_list)/len(times_list), "seconds")

if __name__ == "__main__":
    for query_length in range(5,11):
        queries = generate_random_queries_2.generate_queries(50, query_length)
        avg_time(queries, query_length, method=3)
