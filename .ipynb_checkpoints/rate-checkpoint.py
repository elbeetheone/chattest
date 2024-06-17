import streamlit as st
from gensim.models import Word2Vec, KeyedVectors
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize,word_tokenize
from gensim.models import Word2Vec, KeyedVectors
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import cohen_kappa_score
from keras.layers import Embedding, LSTM, Dense, Dropout, Lambda, Flatten
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, model_from_config
from keras import backend as K



topic = st.query_params.get("topic", ["default_value"])
user = st.query_params.get("user", ["default_value"])
trans = st.query_params.get("trans", ["default_value"])


def sent2word(x):
    stop_words = set(stopwords.words('english'))
    x=re.sub("[^A-Za-z]"," ",x)
    x.lower()
    filtered_sentence = []
    words=x.split()
    for w in words:
        if w not in stop_words:
            filtered_sentence.append(w)
    return filtered_sentence

def essay2word(essay):
    essay = essay.strip()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    raw = tokenizer.tokenize(essay)
    final_words=[]
    for i in raw:
        if(len(i)>0):
            final_words.append(sent2word(i))
    return final_words

def makeVec(words, model, num_features):
    vec = np.zeros((num_features,),dtype="float32")
    noOfWords = 0.
    index2word_set = set(model.index_to_key)
    for i in words:
        if i in index2word_set:
            noOfWords += 1
            vec = np.add(vec,model[i])
    vec = np.divide(vec,noOfWords)
    return vec

def getVecs(essays, model, num_features):
    c=0
    essay_vecs = np.zeros((len(essays),num_features),dtype="float32")
    for i in essays:
        essay_vecs[c] = makeVec(i, model, num_features)
        c+=1
    return essay_vecs

@st.cache_resource
def convertToVec(text):
    content=text
    if len(content) > 20:
        num_features = 300
        model = KeyedVectors.load_word2vec_format("word2vecmodel.bin", binary=True)
        clean_test_essays = []
        clean_test_essays.append(sent2word(content))
        testDataVecs = getVecs(clean_test_essays, model, num_features )
        testDataVecs = np.array(testDataVecs)
        testDataVecs = np.reshape(testDataVecs, (testDataVecs.shape[0], 1, testDataVecs.shape[1]))

        lstm_model = load_model("essay.h5")
        preds = lstm_model.predict(testDataVecs)
        return preds[0][0] * 10

@st.cache_resource
def get_transcript(topic, transcript):
    wv = load_model('glove-wiki-gigaword-50')
    ratings_1 = convertToVec(transcript) * 0.80
    ratings_2 = abs(1-wv.wmdistance(topic,transcript)) * 0.20
    Content_ratings = ratings_1 + ratings_2

    return Content_ratings


url = st.secrets['WEB']
myobj = {'score': get_transcript(topic, trans), 'user': user}
requests.post(url, json = myobj)