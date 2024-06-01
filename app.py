import streamlit as st
from gensim.models import Word2Vec, KeyedVectors
from english_words import get_english_words_set
import random
import requests

wv = KeyedVectors.load('google_50_vectors.kv')
words = list(wv.key_to_index.keys())
web2lowerset = get_english_words_set(['web2'], lower=True)

foo = st.query_params.get("foo", ["default_value"])

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
    return today_words

if foo == st.secrets['CODE']:
    url = 'https://speakeasi.app/_/api/savevideo'
    myobj = {'today_words': paste_budz()}
    requests.post(url, json = myobj)
