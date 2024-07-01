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

wv = load_model('glove-twitter-50')

# Extract parameters with default values if they don't exist
user_words = st.query_params.get("user_words", ["default_value"])
user = st.query_params.get("user", ["default_value"])
foo = st.query_params.get("foo", ["default_value"])
bar = st.query_params.get("bar", ["default_value"])


def seenonim(user_response):
    today = foo.split(',')
    nu_list = []
    for num in range(5):
        try:
            if today[num] == user_response[num].lower() or  user_response[num] == '_':
                nu_list.append(json.dumps(str(0)))
            if engine.plural(today[num]) == user_response[num].lower() or  today[num] == engine.plural(user_response[num].lower()):
                nu_list.append(json.dumps(str(0)))
            elif difflib.SequenceMatcher(None, today[num], user_response[num].lower()).ratio() > 0.75:
                nu_list.append(json.dumps(str(0.05)))
            else:
                score = wv.similarity(today[num],user_response[num].lower())
                nu_list.append(json.dumps(str((score))))
        except Exception as e:
            # nu_list.append({'word':today[num], 'score': 0, 'scores': 0, 'synonym': user_response[num]})
            nu_list.append(json.dumps(str(0)))
    return nu_list

def get_transcript(topic, transcript):
    ratings = abs(1-wv.wmdistance(topic,transcript))
    ratings = json.dumps(str(ratings))
    return ratings


if bar == st.secrets['BAR_1']:
    user_words_ = user_words.split(',')
    url = st.secrets['WEB']
    myobj = {'today_words': seenonim(user_words_), 'user':user, 'foo':foo, 'user_words': user_words}
    requests.post(url, json = myobj)

if bar == st.secrets['BAR_2']:
    url = st.secrets['WEB_2']
    foo = foo.replace(',',' ').lower()
    user_words = user_words.replace(',',' ').lower()
    myobj = {'score': get_transcript(user_words, foo), 'user':user}
    requests.post(url, json = myobj)
