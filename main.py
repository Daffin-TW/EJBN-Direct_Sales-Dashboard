from streamlit import session_state as ss
import streamlit as st


def authentication():
    actual_username: str = st.secrets.user_credentials.username
    actual_password: str = st.secrets.user_credentials.password

    placeholder = st.empty()
    with placeholder.form('login'):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit and username == actual_username and password == actual_password:
        # clear the form/container and display a success message
        ss.login_message = True
        ss.login_state = True
        placeholder.empty()
        st.success("Login berhasil")
        st.rerun()

    elif submit and (username != actual_username or password != actual_password):
        st.error("Login gagal, Username/Password tidak sesuai")
    else:
        pass

def check_login_state():
    if not ss.get('login_state', False):
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