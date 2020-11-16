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
import spell_checker

app = Flask(__name__)
spelling_check_done = False

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
		elif i=="solr":
			for j in dic[i]["response"]["docs"]:
				if no<=number_of_results:
					temp.add(j["url"][0])
					no += 1
			res.append(temp)
		else:
			for j in dic[i]:
				if no<=number_of_results:
					temp.add(j["URL"])
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

	with open('document_vectors/document_vectors.pkl', 'rb') as f:
		document_vectors = pickle.load(f)
	with open('documentId.pkl', 'rb') as f:
		document_id = pickle.load(f)

	results = []

	try:
		with open('tfidf_solr_metrics.pkl', 'rb') as f:
			tfidf_solr_metrics = pickle.load(f)
		with open('wordemb_solr_metrics.pkl', 'rb') as f:
			wordemb_solr_metrics = pickle.load(f)
		with open('boolean_solr_metrics.pkl', 'rb') as f:
			boolean_solr_metrics = pickle.load(f)
		with open('elastic_solr_metrics.pkl', 'rb') as f:
			elastic_solr_metrics = pickle.load(f)
		with open('tfidf_elastic_metrics.pkl', 'rb') as f:
			tfidf_elastic_metrics = pickle.load(f)
		with open('wordemb_elastic_metrics.pkl', 'rb') as f:
			wordemb_elastic_metrics = pickle.load(f)
		with open('boolean_elastic_metrics.pkl', 'rb') as f:
			boolean_elastic_metrics = pickle.load(f)

	except:
		query_test_set = ['delaware','former french','shadow secretary','long-bailey','sarkozy','mike bloomberg','single barrier','president marginalised','infamine',
						  'degrogation','energize', 'relate', 'submerged', 'duncan', 'permafrost', 'nigel', 'offence', 'carly', 'fraught', 'cancelled', 'distract', 
						  'northernmost', 'improved', 'aligned', 'unstoppable', 'establishing', 'worthy', 'fo', 'renowned', 'burke', 'scaring', 'disclosing', 'individually', 
						  'abundance', 'galileo', 'circuit', 'amanda', 'spur', 'delicate', 'convenient', 'humidity', 'plagiarism', 'ofjust', 'welsh', 'cornwall', 'mineral', 
						  'collusion', 'terminal', 'arthel', 'snowy', 'yorkers', 'immaterial','environmental catastrophe','oil pipeline canada','osama bin laden','nuclear north korea',
						  'ice melt global warming','clean energy new jobs']

		tfidf_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
		wordemb_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
		boolean_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
		elastic_solr_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
		tfidf_elastic_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
		wordemb_elastic_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}
		boolean_elastic_metrics = {"precision":0,"recall":0,"f1_score":0,"accuracy":0}

		for i in query_test_set:
			tfidf_results = tfidf_search(i,20)
			similarity_list = wordembedding_search.search(i, document_vectors, 20)
			wordemb_results = wordembedding_search.retrieve_documents(similarity_list, document_id)
			boolean_results = boolean_query_model.search(i)
			elastic_results = elastic_search(i,20)
			solr_results = json.loads(requests.get("http://localhost:8983/solr/AIR_Project/select?q=snippet:\""+i+"\"&wt=json").text)

			cumulative_results = extract_urls({"tfidf":tfidf_results, "solr":solr_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in tfidf_solr_metrics:
				tfidf_solr_metrics[j] += performance_metrics[j]

			cumulative_results = extract_urls({"wordemb":wordemb_results, "solr":solr_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in wordemb_solr_metrics:
				wordemb_solr_metrics[j] += performance_metrics[j]

			cumulative_results = extract_urls({"boolean":boolean_results, "solr":solr_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in boolean_solr_metrics:
				boolean_solr_metrics[j] += performance_metrics[j]

			cumulative_results = extract_urls({"elasticsearch":elastic_results, "solr":solr_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in elastic_solr_metrics:
				elastic_solr_metrics[j] += performance_metrics[j]

			cumulative_results = extract_urls({"tfidf":tfidf_results, "elasticsearch":elastic_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in tfidf_elastic_metrics:
				tfidf_elastic_metrics[j] += performance_metrics[j]

			cumulative_results = extract_urls({"wordemb":wordemb_results, "elasticsearch":elastic_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in wordemb_elastic_metrics:
				wordemb_elastic_metrics[j] += performance_metrics[j]

			cumulative_results = extract_urls({"boolean":boolean_results, "elasticsearch":elastic_results},20)
			performance_metrics = calculate_metrics(cumulative_results)
			for j in boolean_elastic_metrics:
				boolean_elastic_metrics[j] += performance_metrics[j]

		for i in tfidf_solr_metrics:
			tfidf_solr_metrics[i] /= len(query_test_set)

		for i in wordemb_solr_metrics:
			wordemb_solr_metrics[i] /= len(query_test_set)

		for i in boolean_solr_metrics:
			boolean_solr_metrics[i] /= len(query_test_set)

		for i in elastic_solr_metrics:
			elastic_solr_metrics[i] /= len(query_test_set)

		for i in tfidf_elastic_metrics:
			tfidf_elastic_metrics[i] /= len(query_test_set)

		for i in wordemb_elastic_metrics:
			wordemb_elastic_metrics[i] /= len(query_test_set)

		for i in boolean_elastic_metrics:
			boolean_elastic_metrics[i] /= len(query_test_set)

		pickle.dump(tfidf_solr_metrics,open("tfidf_solr_metrics.pkl","wb"))
		pickle.dump(wordemb_solr_metrics,open("wordemb_solr_metrics.pkl","wb"))
		pickle.dump(boolean_solr_metrics,open("boolean_solr_metrics.pkl","wb"))
		pickle.dump(elastic_solr_metrics,open("elastic_solr_metrics.pkl","wb"))
		pickle.dump(tfidf_elastic_metrics,open("tfidf_elastic_metrics.pkl","wb"))
		pickle.dump(wordemb_elastic_metrics,open("wordemb_elastic_metrics.pkl","wb"))
		pickle.dump(boolean_elastic_metrics,open("boolean_elastic_metrics.pkl","wb"))

	results.append({"comparison":"tfidf vs. Elasticsearch","metrics":tfidf_elastic_metrics})
	results.append({"comparison":"Word Embeddings vs. Elasticsearch","metrics":wordemb_elastic_metrics})
	results.append({"comparison":"Boolean Retrieval vs. Elasticsearch","metrics":boolean_elastic_metrics})
	results.append({"comparison":"tfidf vs. solr","metrics":tfidf_solr_metrics})
	results.append({"comparison":"Word Embeddings vs. solr","metrics":wordemb_solr_metrics})
	results.append({"comparison":"Boolean Retrieval vs. solr","metrics":boolean_solr_metrics})
	results.append({"comparison":"Elasticsearch vs. solr","metrics":elastic_solr_metrics})
	
	'''
	for i in query_test_set:
		tfidf_results = tfidf_search(i,20)
		similarity_list = wordembedding_search.search(query, document_vectors, 20)
		wordemb_results = wordembedding_search.retrieve_documents(similarity_list, document_id)
		boolean_results = boolean_query_model.search(i)
		elastic_results = elastic_search(i,20)

		cumulative_results = extract_urls({"tfidf":tfidf_results, "elasticsearch":elastic_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in tfidf_elastic_metrics:
			tfidf_elastic_metrics[j] += performance_metrics[j]

		cumulative_results = extract_urls({"wordemb":wordemb_results, "elasticsearch":elastic_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in wordemb_elastic_metrics:
			wordemb_elastic_metrics[j] += performance_metrics[j]

		cumulative_results = extract_urls({"boolean":boolean_results, "elasticsearch":elastic_results},20)
		performance_metrics = calculate_metrics(cumulative_results)
		for j in boolean_elastic_metrics:
			boolean_elastic_metrics[j] += performance_metrics[j]

	for i in tfidf_elastic_metrics:
		tfidf_elastic_metrics[i] /= len(query_test_set)

	for i in wordemb_elastic_metrics:
		wordemb_elastic_metrics[i] /= len(query_test_set)

	for i in boolean_elastic_metrics:
		boolean_elastic_metrics[i] /= len(query_test_set)

	results.append({"comparison":"tfidf vs. Elasticsearch","metrics":tfidf_elastic_metrics})
	results.append({"comparison":"Word Embeddings vs. Elasticsearch","metrics":wordemb_elastic_metrics})
	results.append({"comparison":"Boolean Retrieval vs. Elasticsearch","metrics":boolean_elastic_metrics})'''
	return jsonify(results), 200

@app.route('/', methods=['GET', 'POST'])
def index():
	global spelling_check_done
	if(request.method == 'GET'):
		spelling_check_done = False
		return render_template('index.html', spelling_fail=False)

	if(request.method == 'POST'):

		query = request.form['query']
		search_option = request.form['searchOption']
		spell_check = spell_checker.spell_checker_sentence(query)

		if spell_check[1] == False or spelling_check_done == True:
			if search_option=="1":
				tfidf_results = tfidf_search(query,20)
				return jsonify(tfidf_results), 200

			elif search_option=="2":
				with open('document_vectors/document_vectors.pkl', 'rb') as f:
					document_vectors = pickle.load(f)
				with open('documentId.pkl', 'rb') as f:
					document_id = pickle.load(f)
				similarity_list = wordembedding_search.search(query, document_vectors, 20)
				return jsonify(wordembedding_search.retrieve_documents(similarity_list, document_id)), 200

			elif search_option=="3":
				elastic_results = elastic_search(query,20)
				return jsonify(elastic_results), 200

			elif search_option=="4":
				solr_results = json.loads(requests.get("http://localhost:8983/solr/AIR_Project/select?q=snippet:\""+query+"\"&wt=json").text)
				return jsonify(solr_results), 200
		else:
			spelling_check_done = True
			return render_template('index.html', spelling_fail=True, previous_query=query, corrected_query=spell_check[0])

if __name__ == "__main__":
	app.run(debug=True)
