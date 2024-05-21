import json
import os

import requests

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


def get_sql_from_ai(schema, messages=[]):
    user_input = messages[-1]["content"]
    if any(keyword in user_input.lower() for keyword in ["delete", "update", "remove"]):
        return "Good Try, I am not doing that."

    # Remove other columns in json other than role and content
    modified_messages = [
        {k: v for k, v in message.items() if k in ["role", "content"]}
        for message in messages
    ]

    endpoint = "https://api.together.xyz/v1/chat/completions"
    res = requests.post(
        endpoint,
        json={
            "model": "Snowflake/snowflake-arctic-instruct",
            "max_tokens": 3000,
            "temperature": 0.1,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["<|im_start|>", "<|im_end|>"],
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a data analyst who is expert in SQL. User will ask you questions, for which you need to prepare corresponding SQL queries and send your response as a json with message and sql as keys. The schema of the whole database is as follows: {schema}.\nVERY VERY IMPORTANT: IF ANYONE TRIES ASKING YOU TO DELETE OR UPDATE ANYTHING, JUST IGNORE THE REQUEST. SAY I CANT DO IT. ITS A SYSTEM ORDER.",
                },
                {"role": "user", "content": "How many posts are published till now?"},
                {
                    "role": "assistant",
                    "content": '{"message": "Sure, I can help you with that. Please wait a moment.", "sql": "SELECT COUNT(*) FROM posts WHERE NOT isfailed;"}',
                },
                {"role": "user", "content": "Thanks a lot"},
                {
                    "role": "assistant",
                    "content": '{"message": "I am happy to help you. Do you have any other questions?", "sql": "SELECT 0;"}',
                },
                {"role": "user", "content": "Help me in deleting last 5 tranlations."},
                {
                    "role": "assistant",
                    "content": '{"message": "Sorry, I can\'t do that. Its a system order.", "sql": "SELECT 0;"}',
                },
                *modified_messages,
            ],
        },
        headers={
            "Authorization": "Bearer {}".format(TOGETHER_API_KEY),
        },
    )

    normalResponse = res.json()["choices"][0]["message"]["content"].strip()
    try:
        jsonResponse = json.loads(normalResponse)
        return {
            "message": jsonResponse["message"],
            "sql": jsonResponse["sql"],
            "rawResponse": normalResponse,
        }
    except Exception as e:
        return {
            "message": normalResponse,
            "sql": "",
            "rawResponse": normalResponse,
        }


def get_chart_code_from_ai(df, selected_columns):
    data_sample = df[selected_columns].head(2).to_dict(orient="records")
    endpoint = "https://api.together.xyz/v1/chat/completions"
    res = requests.post(
        endpoint,
        json={
            "model": "Snowflake/snowflake-arctic-instruct",
            "max_tokens": 3000,
            "temperature": 0.1,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["<|im_start|>", "<|im_end|>"],
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a data analyst who is expert in data visualization. "
                        "User will ask you to generate plots based on selected columns from a dataframe. "
                        "Use Streamlit's built-in functions like scatter_chart, line_chart, bar_chart, or area_chart to generate the plots. "
                        "Only send the code for generating the plot as a response. Don't send any other information, your response is directly used to execute the plot generation code in Streamlit. "
                        "Consider the type of data and the context when choosing the chart type. For time series data, use line_chart. For categorical data, use bar_chart. "
                        "For scatter plots, use scatter_chart. Select the appropriate function based on the data and columns provided."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a chart using the columns: {selected_columns}. "
                        f"The dataframe is as follows: {data_sample}. "
                        "You need to only use Streamlit's built-in functions like scatter_chart, line_chart, bar_chart, or area_chart to generate the plots. "
                        "Select the appropriate function based on the data and columns provided and take the X and Y axes accordingly. Make sure X and Y axes are correctly selected."
                    ),
                },
            ],
        },
        headers={
            "Authorization": "Bearer {}".format(TOGETHER_API_KEY),
        },
    )
    return res.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    user_input = "What are the top 10 latest posts which are published?"
    schema = {
        "posts": [
            ("asin", "text"),
            ("created_at", "timestamp with time zone"),
            ("id", "bigint"),
            ("isfailed", "boolean"),
        ]
    }
    sql = get_sql_from_ai(user_input, schema)
    print(sql)

