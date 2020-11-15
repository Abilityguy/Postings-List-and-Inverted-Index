import urllib3
import json

http = urllib3.PoolManager()

def search(search_string):

    search_terms = search_string.strip().split(" ")
    
    search_terms = ['snippet:"{}"'.format(i) for i in search_terms]

    search_query = ' AND '.join(search_terms) 
    print('search_query ', search_query)

    #connection = http.request('GET', 'http://localhost:8983/solr/AIR_Project/select?q=snippet:"cathedral" AND snippet:"climate"&wt=json')
    connection = http.request('GET', 'http://localhost:8983/solr/AIR_Project/select?q={}&wt=json'.format(search_query))


    response = json.loads(connection.data)

    #print('Response ', response)
    print(response['response']['numFound'], "documents found.")

    # Print the name of each document.

    return_list = []
    for document in response['response']['docs']:
        temp_dict = dict()
        temp_dict['filename'] = str(document['filename'][0])
        temp_dict['url'] = str(document['url'][0])
        temp_dict['datetime'] = str(document['datetime'][0])
        temp_dict['station'] = str(document['station'][0])
        temp_dict['show'] = str(document['show'][0])
        temp_dict['showid'] = str(document['showid'][0])
        temp_dict['preview'] = str(document['preview'][0])
        temp_dict['snippet'] = str(document['snippet'][0])
        return_list.append(temp_dict)


    # print(return_list)
    return return_list


# Sample usage. ApacheSolr sorted all results for query 'cathedral climate'. 
print(search('cathedral climate'))