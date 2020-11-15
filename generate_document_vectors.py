import gensim.downloader as api
import pandas as pd
import pickle
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import numpy as np

def remove_stop_words(x, stop_words):
    return [word for word in x if word not in stop_words]

def lemmatize_words(x):
    return [lemmatizer.lemmatize(word) for word in x]

def generate_document_vector(model, text):
        doc_vector = np.zeros(model.vector_size)
        for word in text:
            if word in model:
                doc_vector += model[word]
        doc_vector/len(text)
        return doc_vector

def process_text(text):
    text = text.lower()
    text = tokenizer.tokenize(text)
    text = remove_stop_words(text, stop_words)
    text = lemmatize_words(text)
    return text

tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


if __name__ == "__main__":

    model = api.load('glove-wiki-gigaword-50')

    with open('documentId.pkl', "rb") as f:
        documentId = pickle.load(f)

    inverse_document_id = {v: k for k, v in documentId.items()}

    document_vector = dict()

    for file in os.listdir('archive/TelevisionNews/'):
        if (file == 'CNN.200910.csv'):
            print("Empty file")
            continue

        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join('archive/TelevisionNews/', file), index_col=None, header=0)

            df['Snippet'] = df["Snippet"].apply(lambda x: x.lower())
            df['Snippet'] = df['Snippet'].apply(lambda x: tokenizer.tokenize(x))
            df['Snippet'] = df['Snippet'].apply(lambda x: remove_stop_words(x, stop_words))
            df['Snippet'] = df['Snippet'].apply(lambda x: lemmatize_words(x))

            docId = inverse_document_id[file]

            for row in range(len(df)):
                Id = docId*10000 + row
                document_vector[Id] = generate_document_vector(model, df.iloc[row]["Snippet"])

    with open('document_vectors/document_vectors.pkl', 'wb') as f:
        pickle.dump(document_vector, f)
