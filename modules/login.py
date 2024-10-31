from time import sleep
import streamlit as st


def login_page():
    # Create an empty container
    placeholder = st.empty()
    state_placeholder = st.empty()

    # Declare username and password
    actual_username = st.secrets.user_credentials.username
    actual_password = st.secrets.user_credentials.password

    # Insert a form in the container
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit and username == actual_username and password == actual_password:
        # clear the form/container and display a success message
        placeholder.empty()
        state_placeholder.success("Login successful")
        sleep(1)
        st.session_state.login_state = True
        state_placeholder.empty()

    elif submit and (username != actual_username or password != actual_password):
        state_placeholder.error("Login failed, Username/Password is incorrect")
    else:
        pass