from modules import login_page, get_dataset
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

if st.session_state.login_state:
    df = get_dataset()
    st.write(df)