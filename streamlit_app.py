from mysql.connector.abstracts import MySQLCursorAbstract as CursorAbstract
from modules import login_page, db_connect
import streamlit as st


def check_login_state():
    if not st.session_state.get('login_state', False):
        _, login_columns, _ = st.columns((1, 2, 1))
        login_page(login_columns)
        return False
    else:
        return True

@st.cache_data(show_spinner=False)
def fetch_data(_db_cursor: CursorAbstract, table: str):
    _db_cursor.execute(f'SELECT * FROM {table}')
    result = _db_cursor.fetchall()
    for row in result:
        st.write(row)


st.set_page_config(
    page_title='EJBN RCE Dashboard',
    page_icon='images/logo.png',
    layout='wide'
)

if check_login_state():
    db_connection = db_connect()
    db_cursor = db_connection.cursor()
    fetch_data(db_cursor, 'Agent')
    st.write('# Aman')
