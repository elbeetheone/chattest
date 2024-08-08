import streamlit as st
import difflib
# from gensim.models.keyedvectors import KeyedVectors
import gensim.downloader
import json
import requests
import inflect

engine = inflect.engine()


@st.cache_resource
def load_model(name):
    model_wiki = gensim.downloader.load(name)
    return model_wiki

wv = load_model("glove-wiki-gigaword-50")

# Extract parameters with default values if they don't exist
user_words = st.query_params.get("user_words", ["default_value"])
user = st.query_params.get("user", ["default_value"])
foo = st.query_params.get("foo", ["default_value"])
bar = st.query_params.get("bar", ["default_value"])
played = st.query_params.get("played", ["default_value"])

def get_adverb(word):
    # Basic rule to convert adjective to adverb
    if word.endswith('y'):
        return word[:-1] + 'ily'
    elif word.endswith('le'):
        return word[:-1] + 'y'
    elif word.endswith('ic'):
        return word + 'ally'
    else:
        return word + 'ly'

def seenonim(user_response):
    today = foo.split(',')
    nu_list = []
    for num in range(5):
        try:
            response_lower = user_response[num].lower()
            if today[num] == response_lower or  user_response[num] == '_':
                nu_list.append(json.dumps(str(0)))
            elif engine.plural(today[num]) == response_lower or  today[num] == engine.plural(response_lower):
                #control for plurals
                nu_list.append(json.dumps(str(0)))
            elif today[num] == get_adverb(response_lower) or get_adverb(today[num]) == response_lower:
                nu_list.append(json.dumps(str(0)))
                #control for adverbs
            elif difflib.SequenceMatcher(None, today[num], response_lower).ratio() > 0.9:
                nu_list.append(json.dumps(str(0.05)))
                #control for words that are too similarly spelt
            else:
                score = wv.similarity(today[num],response_lower)
                nu_list.append(json.dumps(str((score))))
        except Exception as e:
            # nu_list.append({'word':today[num], 'score': 0, 'scores': 0, 'synonym': user_response[num]})
            nu_list.append(json.dumps(str(0)))
    return nu_list

def get_transcript(topic, transcript, controls):
    ratings = abs(1-wv.wmdistance(topic,transcript))
    ratings = ratings - controls
    if ratings < 0.5:
        ratings = 0.5
    ratings = json.dumps(str(ratings))
    return ratings


if bar == st.secrets['BAR_1']:
    user_words_ = user_words.split(',')
    url = st.secrets['WEB']
    myobj = {'today_words': seenonim(user_words_), 'user':user, 'foo':foo, 'user_words': user_words, 'played': played}
    requests.post(url, json = myobj)

if bar == st.secrets['BAR_2']:
    url = st.secrets['WEB_2']
    foo = foo.replace(',',' ').lower()
    user_words_ = user_words.split(',')
    controls = (user_words_.count('um') + user_words_.count('uh')) * 0.25
    user_words = user_words.replace(',',' ').lower()
    myobj = {'score': get_transcript(user_words, foo, controls), 'user':user}
    requests.post(url, json = myobj)
