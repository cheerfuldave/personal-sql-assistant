import base64
import datetime
import time
import json

import pandas as pd
import streamlit as st

from helpers.db import execute_sql, load_schema
from helpers.llm import get_sql_from_ai

st.title("Personal SQL Assistant")
st.write(
    "This app helps you generate SQL queries using Natural Language. You can ask what you want to get from the database and the AI will generate and run the SQL query for you."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant"):
            messageContent = json.loads(message["content"])
            st.markdown(messageContent["message"])
            if messageContent["sql"] != "SELECT 0;":
                st.markdown(f"```sql\n{messageContent['sql']}\n```")
    elif message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Load schema
if "schema" not in st.session_state:
    schema = load_schema()
    st.session_state["schema"] = schema

if "views" not in st.session_state:
    st.session_state["views"] = [
        {
            "name": "Get 5 Random Posts",
            "sql": "SELECT * FROM posts ORDER BY RANDOM() LIMIT 5;",
        }
    ]


def run_query(in_message=False):
    # Check if SQL query exists in session state
    if "sql" in st.session_state:
        sql = st.session_state["sql"]
        if sql == "SELECT 0;":
            return
        try:
            if in_message:
                with st.chat_message("assistant"):
                    df = execute_sql(sql)
                    st.dataframe(df)
            else:
                df = execute_sql(sql)
                st.dataframe(df)
            st.session_state["df"] = df
        except Exception as e:
            st.error(f"Error executing SQL: {e}")


st.sidebar.header("❄ Saved Views ❄")
for view in st.session_state["views"]:
    if st.sidebar.button(view["name"]):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "message": f'Showing saved view {view["name"]}',
                        "sql": view["sql"],
                    }
                ),
            }
        ]
        st.session_state["sql"] = view["sql"]
        run_query(in_message=True)


@st.experimental_dialog("Save Your View")
def save_view(sql):
    st.write("Would you like to save this view?")
    viewName = st.text_input("View Name", value="My View")
    if st.button("Save"):
        # Green color
        st.session_state["views"].append({"name": viewName, "sql": sql})
        st.markdown(":green[View saved successfully!]")
        st.rerun()


if st.session_state.get("save-view"):
    save_view(st.session_state["sql"])

if "snow" not in st.session_state:
    st.session_state["snow"] = True

if st.session_state["snow"]:
    st.snow()
    st.session_state["snow"] = False

if prompt := st.chat_input("What do you want to get from the database?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    aiMessage, sql, rawResponse = get_sql_from_ai(
        st.session_state["schema"], st.session_state["messages"]
    ).values()

    with st.chat_message("assistant"):
        st.markdown(aiMessage)
        if sql != "SELECT 0;":
            st.markdown(f"```sql\n{sql}\n```")

    if sql != "SELECT 0;":
        st.button("Save View", key="save-view")
        with st.spinner("Running SQL..."):
            st.session_state["sql"] = sql
            run_query(in_message=True)

    st.session_state.messages.append({"role": "assistant", "content": rawResponse})
