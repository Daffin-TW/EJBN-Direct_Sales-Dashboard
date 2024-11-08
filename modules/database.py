from mysql.connector.abstracts import MySQLCursorAbstract as db_cur
from streamlit import session_state as ss
import mysql.connector
import streamlit as st
import pandas as pd


st.cache_resource(show_spinner=False, ttl=300)
def connect_db():
    db_connection = mysql.connector.connect(
        host=st.secrets.db_credentials.host,
        user=st.secrets.db_credentials.username,
        password=st.secrets.db_credentials.password,
        database=st.secrets.db_credentials.database
    )

    return db_connection

def check_connection():
    if not ss.db_connection.is_connected():
        st.toast('Database tidak terhubung. Mencoba untuk menghubung kembali',
                 icon='⛔')
        st.cache_resource.clear()
        ss.db_connection = connect_db()

@st.cache_data(show_spinner=False, ttl=300)
def sql_to_dataframe(sql: str):
    check_connection()
    cursor: db_cur = ss.db_connection.cursor()
    cursor.execute(sql)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = [i[0] for i in cursor.description]
    return df.set_index(cursor.description[0][0])

def fetch_channel():
    sql = 'SELECT `code` AS `Code`, area AS "Area" FROM Channel;'
    return sql_to_dataframe(sql)