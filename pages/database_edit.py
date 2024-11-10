from modules import (
    init_configuration, init_content,
    connect_db, check_connection, update_channel, execute_sql_query)
from streamlit import session_state as ss
from datetime import datetime
import streamlit as st
import pandas as pd


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

def apply_button(sql):
    result = execute_sql_query(sql)
    ss.done_editing = True

    if result[0]:
        st.toast('Perubahan Berhasil disimpan')
    else:
        ss.error_editing = True
        st.error(result[1])
        


initialization()

col_channel, col_rce, col_agent = st.columns(3)
col1, col2 = st.columns((1, 3))

col_channel.button(
    'Channel', key='button_channel',
    use_container_width=True, on_click=current_table)
col_rce.button(
    'RCE', key='button_rce',
    use_container_width=True, on_click=current_table)
col_agent.button(
    'Agent', key='button_agent', 
    use_container_width=True, on_click=current_table)

with col1:
    st.markdown('### Filter')

with col2:
    st.markdown(f'### Tabel {ss.edit_selection}')

    if ss.edit_selection == 'Channel':
        if ss.get('error_editing', False):
            ss.error_editing = False
            st.stop()

        sql = update_channel()
        
        if sql and not ss.get('invalid_edit', False) and not ss.get('done_editing', False):
            st.button(
                'Simpan Perubahan', key='apply_button',
                on_click=lambda: apply_button(sql)
            )