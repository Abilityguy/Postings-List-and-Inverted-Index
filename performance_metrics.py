from flask import Flask
from flask import request
from flask import jsonify
from flask import url_for
from flask import redirect
from flask import render_template
import json
import requests
import pickle
from generate_random_queries import generate_queries
from query_ElastiSearch import elastic_search
from ranking_and_retrieval import tfidf_search

app = Flask(__name__)

def extract_urls(dic, number_of_results):
	res = []
	for i in dic:
		temp = set()
		no = 0
		if i=="tfidf":
			for j in dic[i]:
				if no<=number_of_results:
					temp.add(j[1])
					no += 1
			res.append(temp)
		elif i=="elasticsearch":
			for j in dic[i]:
				if no<=number_of_results:
					temp.add(j["url"])
					no += 1
			res.append(temp)
		else:
			for j in dic[i]["response"]["docs"]:
				if no<=number_of_results:
					temp.add(j["url"][0])
					no += 1
			res.append(temp)
	print(res)
	return res

def calculate_metrics(cumulative_results):
	TP = 0
	with open('document_words_count.pkl', 'rb') as f:
		document_words_count = pickle.load(f)
	TN = len(document_words_count)
	FP = 0
	FN = 0
	for i in cumulative_results[0]:
		if i in cumulative_results[1]:
			TP += 1
		elif i not in cumulative_results[1]:
			FP += 1
		TN -= 1
	for i in cumulative_results[1]:
		if i not in cumulative_results[0]:
			FN += 1
			TN -= 1
	precision = TP/(TP+FP)
	recall = TP/(TP+FN)
	f1_score = (2*precision*recall)/(precision+recall)
	accuracy = (TP+TN)/(TP+TN+FP+FN)
	return {"precision":precision,"recall":recall,"f1_score":f1_score,"accuracy":accuracy}

@app.route('/api/v1/performance_metrics', methods=['GET'])
def compare_performance_metrics():
	if(not(request.method=='GET')):
		return jsonify({}),405

	with open('word_count_dict.pkl', 'rb') as f:
		word_count_dict = pickle.load(f)

	words = list(word_count_dict.keys())
	word_counts = list(word_count_dict.values())

	query_test_set = generate_queries(words, word_counts, 20, 1)

	results = []
	tfidf_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
	elastic_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}

	for i in query_test_set:
		tfidf_results = tfidf_search(i,20)
		solr_results = json.loads(requests.get("http://localhost:8983/solr/AIR_Project/select?q=snippet:\""+i+"\"&wt=json").text)
		cumulative_results = extract_urls({"tfidf":tfidf_results, "solr":solr_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in tfidf_solr_metrics:
			tfidf_solr_metrics[j] += performance_metrics[j]

		elastic_results = elastic_search(i,20)
		solr_results = json.loads(requests.get("http://localhost:8983/solr/AIR_Project/select?q=snippet:\""+i+"\"&wt=json").text)
		cumulative_results = extract_urls({"elasticsearch":elastic_results, "solr":solr_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in elastic_solr_metrics:
			elastic_solr_metrics[j] += performance_metrics[j]

	for i in tfidf_solr_metrics:
		tfidf_solr_metrics[i] /= 20
	for i in elastic_solr_metrics:
		elastic_solr_metrics[i] /= 20
	results.append({"comparison":"tfidf vs. solr","metrics":tfidf_solr_metrics})
	results.append({"comparison":"Elasticsearch vs. solr","metrics":elastic_solr_metrics})
	print(elastic_solr_metrics)

	for i in generate_queries(words, word_counts, 20, 2):
		query_test_set.append(i)

	for i in generate_queries(words, word_counts, 10, 3):
		query_test_set.append(i)

	tfidf_elastic_metrics = {"precision":0,"recall":0,"f1_score":0,"accurancy":0}

	for i in query_test_set:
		tfidf_results = tfidf_search(i,20)
		elastic_results = elastic_search(i,20)
		cumulative_results = extract_urls({"tfidf":tfidf_results, "elasticsearch":elastic_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in tfidf_elastic_metrics:
			tfidf_elastic_metrics[j] += performance_metrics[j]

	for i in tfidf_elastic_metrics:
		tfidf_elastic_metrics[i] /= 50

	results.append({"comparison":"tfidf vs. Elasticsearch","metrics":tfidf_elastic_metrics})
	return jsonify(results), 200

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)
