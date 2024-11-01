from streamlit.delta_generator import DeltaGenerator
import streamlit as st


def login_page(st_columns: DeltaGenerator):
    st.session_state.login_state = False

    actual_username: str = st.secrets.user_credentials.username
    actual_password: str = st.secrets.user_credentials.password

    container = st_columns.container(border=False)
    placeholder = container.empty()
    state_placeholder = container.empty()

    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit and username == actual_username and password == actual_password:
        # clear the form/container and display a success message
        st.session_state.login_state = True
        placeholder.empty()
        state_placeholder.success("Login successful")
        st.rerun()

    elif submit and (username != actual_username or password != actual_password):
        state_placeholder.error("Login failed, Username/Password is incorrect")
    else:
        pass