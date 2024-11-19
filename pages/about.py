from modules import (
    init_configuration, init_sidebar, init_content
)
from streamlit import session_state as ss
import streamlit as st


def initialization():
    init_configuration()

    ss.navigation = '🖊 about'
    init_content()
    init_sidebar()


initialization()

st.write('WORK IN PROGRESS')