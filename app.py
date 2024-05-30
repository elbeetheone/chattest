from gensim.models import Word2Vec, KeyedVectors
from english_words import get_english_words_set

from english_words import get_english_words_set

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



st.title(' '.join(paste_budz))

# from openai import OpenAI
# import streamlit as st


# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

# client = OpenAI(api_key= st.secrets['OPENAI_API_KEY'])

# # Extract the 'foo' parameter
# foo = st.query_params.get("foo", ["default_value"])

# if "messages" not in st.session_state:
#     st.session_state["messages"] = [
#         {
#             "role": "system",
#             "content": st.secrets['PROMPT'],
#         }
#     ]

# st.title("🗣️ Ari's Here to help")
# # for message in st.session_state.messages:
# #     st.chat_message(message["role"]).markdown(message["content"])

# prompt = foo
# if prompt:
#     # st.chat_message("user").markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=st.session_state.messages,
#         stream=True,
#     )

#     complete_response = ""
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         for chunk in response:
#             if chunk.choices[0].delta.content is not None:
#                 complete_response += chunk.choices[0].delta.content
#                 message_placeholder.markdown(complete_response + "▌")
#                 message_placeholder.markdown(complete_response)
#     st.session_state.messages.append(
#         {"role": "assistant", "content": complete_response}
#     )
