import json
import streamlit as st
from helpers.llm import getAssistantResponse

st.title("Dr Abhishek Shukla")
st.write(
    "Dr Abhishek Shukla is a General Practitioner with over 20 years of experience. He is a member of the Indian Medical Association and has been awarded the 'Best Doctor' award for 5 consecutive years."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


@st.experimental_dialog("Generate Report")
def generateReport():
    st.write("Generating Your Report")


if "balloons" not in st.session_state:
    st.session_state["balloons"] = True

if st.session_state["balloons"]:
    st.balloons()
    st.session_state["balloons"] = False

if prompt := st.chat_input("Ask your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        assistantResponse = getAssistantResponse(st.session_state.messages)
        response = st.write_stream(assistantResponse)

    st.session_state.messages.append({"role": "assistant", "content": response})

    if "Generating Your Report" in response:
        with st.chat_message("assistant"):
            reportResponse = getAssistantResponse(
                st.session_state.messages[:-1], makeReport=True
            )
            report = st.write_stream(reportResponse)

        st.session_state.messages.append({"role": "assistant", "content": report})
