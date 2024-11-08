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

    if not ss.get('db_connection', False):
        ss.db_connection = connect_db()
    check_connection()


initialization()

col1, col2 = st.columns((1, 4))

with col1:
    st.markdown('### Pilihan Tabel')
    st.button('Channel', key='button_channel', use_container_width=True)
    st.button('RCE', key='button_rce', use_container_width=True)
    st.button('Agent', key='button_agent', use_container_width=True)
    
    ss.button_edit_database = {
        'Channel': ss.button_channel,
        'RCE': ss.button_rce,
        'Agent': ss.button_agent}

    if ss.get('is_firsttime', False):
        ss.button_edit_database['Channel'] = True
        ss.is_firsttime = False

    st.divider()

with col2:
    for table, value in ss.button_edit_database.items():
        if value:
            ss.edit_selection = table
            st.markdown(f'### Tabel {table}')
            break