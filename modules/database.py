from streamlit import session_state as ss
import mysql.connector
import streamlit as st


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