import os
import pickle
from generate_document_vectors import process_text, generate_document_vector
import gensim.downloader as api
import numpy as np
import pandas as pd

def cosine_similarity(v1, v2):
    dotProduct = np.dot(v1,v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    s = norm1 * norm2

    if(s == 0): return 0
    else : return (dotProduct/(norm1 * norm2 ))

def search(query, document_vector, n_top=10):
    processed_query = process_text(query)
    query_vector = generate_document_vector(model, processed_query)

    similarity_list = list()
    for Id in document_vector.keys():
        similarity_list.append([Id, cosine_similarity(query_vector, document_vector[Id])])

    similarity_list = sorted(similarity_list, key=lambda x:x[1], reverse=True)

    return similarity_list[:n_top]

def retrieve_documents(similarity_list, document_id):
    result = list()

    for i in range(len(similarity_list)):
        result_dict = dict()

        id = similarity_list[i][0]
        csv_id = id // 10000
        row_id = id % 10000

        result_dict['Csv'] = document_id[csv_id]
        result_dict['Row'] = row_id

        df = pd.read_csv(os.path.join('archive/TelevisionNews/', document_id[csv_id]))

        result_dict['URL'] = df['URL'][row_id]
        result_dict['MatchDateTime'] = df['MatchDateTime'][row_id]
        result_dict['Station'] = df['Station'][row_id]
        result_dict['Show'] = df['Show'][row_id]
        result_dict['IAShowID'] = df['IAShowID'][row_id]
        result_dict['IAPreviewThumb'] = df['IAPreviewThumb'][row_id]
        result_dict['Snippet'] = df['Snippet'][row_id]

        result.append(result_dict)

    return result

if __name__ == "__main__":

    with open('document_vectors/document_vectors.pkl', 'rb') as f:
        document_vectors = pickle.load(f)

    with open('documentId.pkl', 'rb') as f:
        document_id = pickle.load(f)

    model = api.load('glove-wiki-gigaword-50')

    query = input("Enter search query: ")

    similarity_list = search(query, document_vectors)

    print(retrieve_documents(similarity_list, document_id))
