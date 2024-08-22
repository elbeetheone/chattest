import streamlit as st
import gensim.downloader
from english_words import get_english_words_set
import random
import json
import requests


league = st.query_params.get("league", ["default_value"])
length = st.query_params.get("length", ["default_value"])
bar = st.query_params.get("bar", ["default_value"])

@st.cache_resource
def load_model(name):
    model_wiki = gensim.downloader.load(name)
    return model_wiki

wv = load_model("glove-wiki-gigaword-50")
words = list(wv.key_to_index.keys())
web2lowerset = get_english_words_set(['web2'], lower=True)

def paste_budz():
    def has_more_than_five_similars(word, web2lowerset, wv):
        similar_words = [similar_word[0] for similar_word in wv.most_similar(word, topn=10)]
        return len([sw for sw in similar_words if sw in web2lowerset]) > 5

    # Filter words by length and presence in web2lowerset
    ran_letter = [num for num in words if len(num) >= 5 and num in web2lowerset]

    # Ensure today_words has 5 words that meet the condition
    today_words = []
    while len(today_words) < 5:
        candidate = random.choice(ran_letter)  # Choose a random word from ran_letter
        # Add the candidate if it meets the condition and isn't already in today_words
        if has_more_than_five_similars(candidate, web2lowerset, wv) and candidate not in today_words:
            today_words.append(candidate)



list_to_pass = []
for num in range(length):
    list_to_pass.append(paste_budz())


if bar == st.secrets['BAR_1']:
    user_words_ = user_words.split(',')
    url = st.secrets['WEB']
    myobj = {'user_words': list_to_pass, 'league': league}
    requests.post(url, json = myobj)
