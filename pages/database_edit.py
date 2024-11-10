from modules import (
    init_configuration, init_content,
    connect_db, check_connection, fetch_channel)
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

def table_input(data):
    pass


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
        # changes = table_input(fetch_channel())
        df_original = fetch_channel().reset_index()
        
        df_modified = st.data_editor(
            df_original.copy(), num_rows='dynamic', use_container_width=True,
            column_config={
                'Code': st.column_config.TextColumn(
                    default='DS00', max_chars=5,
                    required=True, validate='[A-Za-z]+[0-9]+'
                )
            }
        )

        if any(df_modified['Code'].duplicated()):
            st.error('Kode tidak boleh duplikat', icon='❗')
        df_modified['Code'] = df_modified['Code'].drop_duplicates()
        
        changes = df_modified.merge(
            df_original, indicator = True, how='outer',
        ).loc[lambda x : x['_merge'] != 'both']

        changes = changes.dropna(subset=['Code'])
        changes.rename(columns={'_merge': 'Difference'}, inplace=True)
        changes.drop_duplicates(subset=['Code', 'Difference'], inplace=True)
        changes['Update'] = changes.duplicated(subset=['Code'], keep=False)

        
        st.write(changes)