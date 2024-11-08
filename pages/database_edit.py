from modules import (
    init_configuration, init_sidebar, init_content,
    connect_db, check_connection, fetch_channel)
from datetime import datetime
from streamlit import session_state as ss
import streamlit as st


def initialization():
    init_configuration()
    
    ss.navigation = '⚙ database edit'
    init_content()
    # init_sidebar()

    if not ss.get('db_connection', False):
        ss.db_connection = connect_db()
    check_connection()


initialization()
