import streamlit as st


# Create an empty container
placeholder = st.empty()

# Declare username and password
actual_username = st.secrets.user_credentials['USERNAME']
actual_password = st.secrets.user_credentials['PASSWORD']

# Insert a form in the container
with placeholder.form("login"):
    st.markdown("#### Enter your credentials")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit and username == actual_username and password == actual_password:
    # If the form is submitted and the username and password are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    st.success("Login successful")
elif submit and username != actual_username and password != actual_password:
    st.error("Login failed")
else:
    pass

