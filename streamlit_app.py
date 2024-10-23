from modules import login_page
from time import sleep
import streamlit as st


def initialization():
    if 'login_state' not in st.session_state:
        st.session_state.login_state = 0
    else:
        pass

def check_login_state():
    if not st.session_state.login_state:
        login_page()
    else:
        pass


initialization()
check_login_state()