from streamlit import session_state as ss
from streamlit import secrets as sc
import streamlit as st


# Callback function when button is pressed
def submit_callback():
    if not ss.get('username', False):
        ss.username = ''
    if not ss.get('password', False):
        ss.password = ''

    user_credentials = sc.user_credentials
    credentials = [tuple(i.values()) for i in user_credentials]
    
    if (ss.username, ss.password) in credentials:
        ss.login_message = True
        ss.login_state = True
        
    else:
        ss.password = ''

# Makes a login form
def authentication():
    placeholder = st.empty()
    with placeholder.form('login'):
        st.markdown('#### Enter your credentials')
        st.text_input('Username', key='username')
        st.text_input('Password', key='password', type='password')
        submit = st.form_submit_button('Login', on_click=submit_callback)

    if submit and ss.login_state:
        placeholder.empty()
        st.rerun()

    elif submit:
        st.toast("Login gagal, Username/Password tidak sesuai", icon='⚠')

# Check wether the user has a permission to access the dashboard
def check_login_state():
    if not ss.get('login_state', False):
        ss.login_state = False
        authentication()
        
        if ss.get('login_message', False):
            st.toast('Dimohon untuk login agar dapat mengakses situs...',
                     icon='❗')
        return False
    
    else:
        return True

def initialization():
    st.set_page_config(
        page_title='EJBN RCE Dashboard',
        page_icon='images/logo.png',
    )


initialization()

if check_login_state():
    st.switch_page('pages/dashboard.py')