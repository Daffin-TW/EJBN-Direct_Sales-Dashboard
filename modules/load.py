from streamlit import session_state as ss
import streamlit as st


st.cache_data(show_spinner=False)
def load_image(image):
    return st.image(image)