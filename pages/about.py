from modules import (
    check_login_state, init_configuration, init_sidebar,
    init_content, connect_db, check_connection)
from streamlit import session_state as ss
import streamlit as st


def initialization():
    init_configuration()

    ss.navigation = '🖊 about'
    init_content()
    init_sidebar()


initialization()

st.write('WORK IN PROGRESS')