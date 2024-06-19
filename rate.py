import streamlit as st
import gensim.downloader
import json
import requests

@st.cache_resource
def load_model(name):
    model_wiki = gensim.downloader.load(name)
    return model_wiki

wv = load_model('glove-twitter-50')

topic = st.query_params.get("topic", ["default_value"])
user = st.query_params.get("user", ["default_value"])
trans = st.query_params.get("trans", ["default_value"])




@st.cache_resource
def get_transcript(topic, transcript):
    ratings = abs(1-wv.wmdistance(topic,transcript))
    #lazy model :)
    return ratings


url = st.secrets['WEB']
myobj = {'score': get_transcript(topic, trans), 'user': user}
requests.post(url, json = myobj)