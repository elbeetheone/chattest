from openai import OpenAI
import streamlit as st


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

client = OpenAI(api_key= st.secrets['OPENAI_API_KEY'])

# Extract the 'foo' parameter
foo = st.query_params.get("foo", ["default_value"])

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": st.secrets['PROMPT'],
        }
    ]

st.title("🗣️ Ari's Here to help")
# for message in st.session_state.messages:
#     st.chat_message(message["role"]).markdown(message["content"])

prompt = foo
if prompt:
    # st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages,
        stream=True,
    )

    complete_response = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                complete_response += chunk.choices[0].delta.content
                message_placeholder.markdown(complete_response + "▌")
                message_placeholder.markdown(complete_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": complete_response}
    )
