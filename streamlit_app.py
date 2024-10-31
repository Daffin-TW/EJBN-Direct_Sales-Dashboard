from modules import login_page, load_dataset
import streamlit as st


def check_login_state():
    if not st.session_state.get('login_state', False):
        login_page()
        return False
    else:
        return True


st.set_page_config(
    page_title='EJBN RCE Dashboard',
    page_icon='images/logo.png'
)

if check_login_state():
    df = load_dataset()
    rcm = df['RCM'].unique()

    st.sidebar.multiselect('RCM', rcm, rcm[0],
                           placeholder='Pilih RCM yang ingin ditampilkan')
    