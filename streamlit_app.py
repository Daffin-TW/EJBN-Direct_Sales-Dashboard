from modules import login_page, db_connect
import streamlit as st


def check_login_state():
    if not st.session_state.get('login_state', False):
        _, login_columns, _ = st.columns((1, 2, 1))
        login_page(login_columns)
        return False
    else:
        return True


st.set_page_config(
    page_title='EJBN RCE Dashboard',
    page_icon='images/logo.png',
    layout='wide'
)

if check_login_state():
    db_cursor = db_connect()
    st.write('# Aman')
