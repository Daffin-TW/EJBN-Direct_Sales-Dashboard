from modules import login_page, load_dataset
import streamlit as st


def initialization():
    if 'login_state' not in st.session_state:
        st.session_state.login_state = False
    else:
        pass

def check_login_state():
    if not st.session_state.get('login_state', False):
        login_page()
    else:
        pass


initialization()
check_login_state()

if st.session_state.get('login_state', False):
    df = load_dataset()
    rcm = df['RCM'].unique()

    st.sidebar.multiselect('RCM', rcm, rcm[0],
                           placeholder='Pilih RCM yang ingin ditampilkan')
    