import csv

from os import listdir
from os.path import isfile, join

from elasticsearch import Elasticsearch, helpers
import requests

import ElastiSearch_build_index


es = Elasticsearch([{'host':'localhost', 'port': 9200}])

FOLDER_PATH = './archive'


def search(es, search_string, number_results):
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



# Sample usage. ElastiSearch sorted top 10 results for query 'cathedral climate'. 
print(search(es, 'cathedral climate', 10))
