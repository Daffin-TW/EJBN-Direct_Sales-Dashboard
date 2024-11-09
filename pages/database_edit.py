from modules import (
    init_configuration, init_content,
    connect_db, check_connection, fetch_channel)
from datetime import datetime
from streamlit import session_state as ss
import streamlit as st


def initialization():
    init_configuration()
    
    ss.navigation = '⚙ database edit'
    init_content()

    with st.sidebar:
        st.markdown('')

    if not ss.get('edit_selection', False):
        ss.edit_selection = 'Channel'
        
    if not ss.get('db_connection', False):
        ss.db_connection = connect_db()
    check_connection()

def current_table():
    button_edit_database = {
    'Channel': ss.button_channel,
    'RCE': ss.button_rce,
    'Agent': ss.button_agent
}

    ss.edit_selection = ''.join([
    key for key, value in button_edit_database.items() if value == True
])


initialization()

col_channel, col_rce, col_agent = st.columns(3)
col1, col2 = st.columns((1, 3))

col_channel.button('Channel', key='button_channel', use_container_width=True, on_click=current_table)
col_rce.button('RCE', key='button_rce', use_container_width=True, on_click=current_table)
col_agent.button('Agent', key='button_agent', use_container_width=True, on_click=current_table)

st.divider()

with col1:
    st.markdown('### Filter')

with col2:
    st.markdown(f'### Tabel {ss.edit_selection}')
    st.button('Random Things')
    