import csv
from os import listdir
from os.path import isfile, join
from elasticsearch import Elasticsearch, helpers
import requests
import argparse
import ElastiSearch_build_index


es = Elasticsearch([{'host':'localhost', 'port': 9200}])
FOLDER_PATH = 'data'
parser = argparse.ArgumentParser(description="Ranking and retrieval")
parser.add_argument('--query', help="Enter query", default="", type=str)


def elastic_search(search_string, number_results):
    global es
    search_param = {
        'query': {
            'match': {
                'snippet': '{}'.format(search_string)
            }
        }
    }

    res = es.search(index="news", body=search_param, size=number_results)
    # print("Got %d Hits:" % res['hits']['total']['value'])

    return_list = []
    for hit in res['hits']['hits']:
        return_list.append(hit['_source'])

    return return_list

if __name__=="__main__":
    # Sample usage. ElastiSearch sorted top 20 results for query 'cathedral climate'. 
    args = parser.parse_args()
    search_results = elastic_search(args.query, 20)
    print(search_results)
