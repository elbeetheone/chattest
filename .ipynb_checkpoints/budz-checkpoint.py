import streamlit as st
import difflib
# from gensim.models.keyedvectors import KeyedVectors
import gensim.downloader
import json
import requests


@st.cache_resource
def load_model(name):
    model_wiki = gensim.downloader.load(name)
    return model_wiki

wv = load_model('glove-wiki-gigaword-50')

# Extract parameters with default values if they don't exist
user_words = st.query_params.get("user_words", ["default_value"])
user = st.query_params.get("user", ["default_value"])
foo = st.query_params.get("foo", ["default_value"])



foo_ = foo.split(',')
user_words_ = user_words.split(',')



def seenonim(user_response):
    nu_list = []
    today = foo_
    for num in range(5):
        try:
            if today[num] == user_response[num].lower() or  user_response[num] == '_':
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


st.write(seenonim(user_words_))

# url = st.secrets['WEB']
# myobj = {'today_words': seenonim(user_words_), 'user':user, 'foo':foo, 'user_words': user_words}
# requests.post(url, json = myobj)
