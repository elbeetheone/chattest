
import streamlit
import difflib
from gensim.models.keyedvectors import KeyedVectors

foo = st.query_params.get("foo", ["default_value"])
user = st.query_params.get("user", ["default_value"])

wv = KeyedVectors.load('google_50_vectors.kv')

def seenonim(user_response):
    nu_list = []
    row = app_tables.users.get(username='OLaoluwa.i#&12')
    today = foo
    for num in range(5):
        try:
            if today[num] == user_response[num].lower():
                nu_list.append(0)
            elif difflib.SequenceMatcher(None, today[num], user_response[num].lower()).ratio() > 0.8:
                nu_list.append(0.05)
            else:
                nu_list.append(wv.similarity(today[num],user_response[num].lower()))
        except Exception as e:
            nu_list.append(0)
    return nu_list

seenonim(user)
