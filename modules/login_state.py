from streamlit import session_state as ss
import streamlit as st


# Check wether the user has a permission to access the dashboard
def check_login_state():
    if not ss.get('login_state', False):
        ss.login_message = True
        st.switch_page('main.py')
    elif ss.get('login_message', False):
        st.toast('Berhasil untuk login...', icon='👍')
        ss.login_message = False