from modules import check_login_state, init_sidebar, init_content
from streamlit import session_state as ss
import streamlit as st


def initialization():
    st.set_page_config(
        page_title='EJBN RCE Dashboard',
        page_icon='images/logo.png',
        initial_sidebar_state='collapsed',
        layout='wide'
    )
    check_login_state()

    ss.navigation = '📊 dashboard'
    init_content()
    init_sidebar()


initialization()

st.write('WORK IN PROGRESS')