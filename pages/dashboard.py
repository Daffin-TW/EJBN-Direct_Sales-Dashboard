from modules import init_sidebar, init_content
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

def initialization():
    st.set_page_config(
        page_title='EJBN RCE Dashboard',
        page_icon='images/logo.png',
        initial_sidebar_state='collapsed',
        layout='wide'
    )
    check_login_state()
    
    ss.navigation = 'dashboard'
    init_content()
    init_sidebar()


initialization()

st.write('WORK IN PROGRESS')