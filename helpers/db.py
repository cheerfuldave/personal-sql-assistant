import os

import pandas as pd
import psycopg2


def load_schema():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    cur.execute(
        """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, column_name
    """
    )
    raw_schema = cur.fetchall()
    conn.close()

    # Organize schema information
    schema = {}
    for table_name, column_name, data_type in raw_schema:
        if table_name not in schema:
            schema[table_name] = []
        schema[table_name].append((column_name, data_type))

    return schema


def execute_sql(sql):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    df = pd.read_sql(sql, conn)
    conn.close()
    return df
