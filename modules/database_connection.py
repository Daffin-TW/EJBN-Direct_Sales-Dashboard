import mysql.connector
import streamlit as st


@st.cache_resource()
def db_connect():
    db = mysql.connector.connect(
        host=st.secrets.db_credentials.host,
        user=st.secrets.db_credentials.username,
        password=st.secrets.db_credentials.password,
        database=st.secrets.db_credentials.database
    )

    return db.cursor()