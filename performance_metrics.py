from flask import Flask
from flask import request
from flask import jsonify
from flask import url_for
from flask import redirect
from flask import render_template
import json
import requests
import pickle
import pandas as pd
from generate_random_queries_2 import generate_queries
from query_ElastiSearch import elastic_search
from ranking_and_retrieval import tfidf_search
import wordembedding_search

app = Flask(__name__)

#df = pd.read_csv('Full_df.csv')

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
		elif i=='boolean' or i=='word_embedding':
			for j in dic[i]:
				if no <= number_of_results:
					temp.add(j['URL'])
					no += 1
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
	if FP!=0 or TP!=0:
		precision = TP/(TP+FP)
	else:
		precision = 0
	if TP!=0 or FN!=0:
		recall = TP/(TP+FN)
	else:
		recall = 0
	if precision!=0 or recall!=0:
		f1_score = (2*precision*recall)/(precision+recall)
	else:
		f1_score = 0
	accuracy = (TP+TN)/(TP+TN+FP+FN)
	return {"precision":precision,"recall":recall,"f1_score":f1_score,"accuracy":accuracy}

@app.route('/api/v1/performance_metrics', methods=['GET'])
def compare_performance_metrics():
	if(not(request.method=='GET')):
		return jsonify({}),405

	query_test_set = ['delaware','former french','shadow secretary','long-bailey','sarkozy','mike bloomberg','single barrier','president marginalised','infamine',
					  'degrogation','energize', 'relate', 'submerged', 'duncan', 'permafrost', 'nigel', 'offence', 'carly', 'fraught', 'cancelled', 'distract',
					  'northernmost', 'improved', 'aligned', 'unstoppable', 'establishing', 'worthy', 'fo', 'renowned', 'burke', 'scaring', 'disclosing', 'individually',
					  'abundance', 'galileo', 'circuit', 'amanda', 'spur', 'delicate', 'convenient', 'humidity', 'plagiarism', 'ofjust', 'welsh', 'cornwall', 'mineral',
					  'collusion', 'terminal', 'arthel', 'snowy', 'yorkers', 'immaterial','environmental catastrophe']

	results = []
	tfidf_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
	elastic_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}

	for i in query_test_set:
		# boolean_results =
		# embedding_results =

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
		tfidf_solr_metrics[i] /= len(query_test_set)
	for i in elastic_solr_metrics:
		elastic_solr_metrics[i] /= len(query_test_set)
	results.append({"comparison":"tfidf vs. solr","metrics":tfidf_solr_metrics})
	results.append({"comparison":"Elasticsearch vs. solr","metrics":elastic_solr_metrics})
	print(elastic_solr_metrics)

	tfidf_elastic_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}

	for i in query_test_set:
		tfidf_results = tfidf_search(i,20)
		elastic_results = elastic_search(i,20)
		cumulative_results = extract_urls({"tfidf":tfidf_results, "elasticsearch":elastic_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in tfidf_elastic_metrics:
			tfidf_elastic_metrics[j] += performance_metrics[j]

	for i in tfidf_elastic_metrics:
		tfidf_elastic_metrics[i] /= len(query_test_set)

	results.append({"comparison":"tfidf vs. Elasticsearch","metrics":tfidf_elastic_metrics})
	return jsonify(results), 200

@app.route('/', methods=['POST', 'GET'])
def index():
	if(request.method == 'POST'):
		query_term = request.form['query']
		search_option = request.form['searchOption']

		if (search_option == '1'):
			pass
		elif (search_option == '2'):
			pass
		elif (search_option == '3'):
			pass
		elif (search_option == '4'):
			search_results = elastic_search(query_term,5)
		elif (search_option == '5'):
			search_results = json.loads(requests.get("http://localhost:8983/solr/AIR_Project/select?q=snippet:\""+query_term+"\"&wt=json").text)

		return render_template('index.html', results=search_results, search=True)
	else:
		return render_template('index.html', search=False)

if __name__ == "__main__":
	app.run(debug=True)
