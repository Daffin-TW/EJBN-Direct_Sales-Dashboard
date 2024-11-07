from streamlit import session_state as ss
import streamlit as st


def init_sidebar():
    with st.sidebar:
        st.html('<h1 style="text-align: center">EJBN Direct Sales Dashboard</h1>')
        st.divider()
        st.markdown('## Navigasi')