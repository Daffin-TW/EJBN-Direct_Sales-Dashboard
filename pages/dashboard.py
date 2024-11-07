from streamlit import session_state as ss
from modules import init_sidebar
import streamlit as st


def check_login_state():
    if not ss.get('login_state', False):
        ss.login_message = True
        st.switch_page('main.py')
    elif ss.get('login_message', False):
        st.toast('Berhasil untuk login...', icon='👍')
        ss.login_message = False

def initialization():
    st.set_page_config(
        page_title='EJBN RCE Dashboard',
        page_icon='images/logo.png',
        layout='wide'
    )
    check_login_state()


initialization()

st.write('WORK IN PROGRESS')

init_sidebar()