import csv

from os import listdir
from os.path import isfile, join

from elasticsearch import Elasticsearch, helpers
import requests


es = Elasticsearch([{'host':'localhost', 'port': 9200}])

FOLDER_PATH = './archive'


def read_folder(folder_path):
    filenames = [str(f) for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return filenames


def read_csv(folder, file):
    with open('{}/{}'.format(folder, file), newline='', encoding='utf8') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',')
        return_data = []

        # url, matchdatetime, station, show, showid, preview, Snippet
        
        for (index, data) in enumerate(csv_data):
            if index!=0:
                row_dict = dict()
                row_dict['filename'] = str(file)
                row_dict['url'] = data[0]
                row_dict['datetime'] = data[1]
                row_dict['station'] = data[2]
                row_dict['show'] = data[3]
                row_dict['showid'] = data[4]
                row_dict['preview'] = data[5]
                row_dict['snippet'] = data[6]

                return_data.append(row_dict)
    
    return return_data  


if __name__ == "__main__":
    
    delete_all_query_param = {
        "query": {
            "match_all": {}
        }
    }
    es.delete_by_query(index="news", body=delete_all_query_param)
    
    all_csv_data = []
    file_paths = read_folder(FOLDER_PATH)
    for file in file_paths:
        file_data = read_csv(FOLDER_PATH, file)
        for row in file_data:
            all_csv_data.append(row)

    helpers.bulk(es, all_csv_data, index='news',doc_type='_doc', request_timeout=200)
    

    

    
    