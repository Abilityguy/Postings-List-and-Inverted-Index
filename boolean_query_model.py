from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pickle
import pandas as pd

stop_words = set(stopwords.words('english')) - {'and', 'or', 'not'}
lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer(r'\w+')

boolean_operator_priority = {'and':1, 'or':1, 'not':2}

with open('inverted_index_set.pkl', 'rb') as f:
    inverted_index = pickle.load(f)

def remove_stop_words(x, stop_words):
    return [word for word in x if word not in stop_words]

def lemmatize_words(x):
    return [lemmatizer.lemmatize(word) for word in x]

def process_query(text):
    text = text.lower()
    text = tokenizer.tokenize(text)
    text = remove_stop_words(text, stop_words)
    text = lemmatize_words(text)

    return text

def infix_to_postfix(query):
    operator_stack = ['#']
    postfix_query = list()

    for word in query:
        if word in boolean_operator_priority:
            if ((operator_stack[-1] == '#') or (boolean_operator_priority[operator_stack[-1]] <  boolean_operator_priority[word])):
                operator_stack.append(word)
            else:
                while((operator_stack[-1] != '#') and (boolean_operator_priority[operator_stack[-1]] >= boolean_operator_priority[word])):
                    postfix_query.append(operator_stack.pop())
                operator_stack.append(word)
        else:
            postfix_query.append(word)

    while(operator_stack[-1] != '#'):
        postfix_query.append(operator_stack.pop())

    return postfix_query

def return_word_set(word, inverted_index):
    if word in inverted_index:
        return inverted_index[word]
    else:
        return set()

def search(query):
    query_list = process_query(query)

    postfix_query = infix_to_postfix(query_list)

    stack = list()

    for word in postfix_query:
        if word in boolean_operator_priority:
            if word == 'and':
                op1 = stack.pop()
                op2 = stack.pop()
                result = op1.intersection(op2)

                stack.append(result)

            elif word == 'or':
                op1 = stack.pop()
                op2 = stack.pop()
                result = op1.union(op2)

                stack.append(result)

            else:
                op1 = stack.pop()
                result = inverted_index['$'] - op1

                stack.append(result)

        else:
            stack.append(return_word_set(word, inverted_index))

    with open('documentId.pkl', 'rb') as f:
        document_ids = pickle.load(f)

    search_results = []
    for i in stack.pop():
        csv_id = i//10000
        row_id = i%10000
        df = pd.read_csv("data/"+document_ids[csv_id])
        row = df.iloc[row_id]
        search_results.append({'csv_file_name':document_ids[csv_id],'URL':row['URL'],'snippet':row['Snippet']})

    return search_results


if __name__ == "__main__":
    query = input()
    print(search(query))
