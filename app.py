from langchain_community.llms import Ollama 
import streamlit as st

llm = Ollama(model="llama3:70b")

st.title("Chatbot using Llama3")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": """
                You are an intelligent assistant. Help the user.

            """,
        }
    ]


prompt = st.text_area("Enter your prompt:")

if prompt:
    # st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=llm,
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
