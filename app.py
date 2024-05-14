from openai import OpenAI
import streamlit as st

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="123",
)

# Extract the 'foo' parameter
foo = st.query_params.get("foo", ["default_value"])

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": """
                Assess the speech transcript below on the following five parameters.
                Format your response using bullet points for each parameter and provide specific
                feedback based on the transcript. Consider the use of filler words (e.g., "um", "uh"),
                and suggest ways to improve the speech's impact. Use examples from the content to support your assessment, and do not invent details.

                Your response should follow this structure with each parameter within an indented block:

                I. Interesting and Concise Introduction
                II. Content Quality and Organization
                III. Delivery Flow
                IV. Vocal Variety and Tone
                V. Engagement and Interaction
                VI. Summary

            """,
        }
    ]

st.title("🗣️ Ari's Here to help")
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

prompt = foo
if prompt:
    # st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama.cpp/models/mistral-7b-instruct-v0.1.Q4_0.gguf",
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
