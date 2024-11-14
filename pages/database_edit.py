from modules import (
    init_configuration, init_content, connect_db, check_connection,
    edit_channel, edit_rce, edit_agent, edit_rce_target, edit_agent_target,
    edit_activation, execute_sql_query, preprocessing_daily_activation
)
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
        'Agent': ss.button_agent,
        'RCE Target': ss.button_rce_target,
        'Agent Target': ss.button_agent_target,
        'Daily Activation': ss.button_activation
    }

    ss.edit_selection = ''.join([
        key for key, value in button_edit_database.items() if value == True
    ])

def apply_button_click(sql: list, dialog: bool = False):
    result = execute_sql_query(sql)
    ss.done_editing = True

    if dialog:
        return None

    if result[0]:
        st.toast('Perubahan Berhasil disimpan')
    else:
        ss.error_editing = True
        st.toast("""
            Mengalami kendala? Hubungi [Daffin_TW](https://wa.me/6282332232896)
            untuk bertanya atau perbaikan.
        """, icon='🚨')
        st.error(result[1])

def is_encounter_an_error():
    if ss.get('error_editing', False):
        ss.error_editing = False
        st.stop()

def apply_button(sql: str):
    if (sql and not ss.get('invalid_edit', False) and
            not ss.get('done_editing', False)):
        st.button(
            'Simpan Perubahan', key='apply_button',
            on_click=lambda: apply_button_click(sql)
        )

@st.dialog('Unggah File', width='large')
def upload_file():
    upload_file = st.file_uploader(
        'Unggah File Excel', key='uploaded_file',
        type=['xlsx'],
        label_visibility='collapsed'
    )

    if upload_file is None:
        return None
    else:
        ss.done_editing = False
    
    df = pd.read_excel(upload_file)
    df = preprocessing_daily_activation(df)
    tanggal = [df['Date'].min(), df['Date'].max()]
    
    st.write(df)
    st.markdown(
        f'#### Perubahan akan menghapus data dari tanggal {tanggal[0]} ' +
        f'sampai dengan {tanggal[1]}'
    )
    
    sql = edit_activation(df)
    on_click = st.button(
        'Simpan Perubahan', key='apply_button',
        on_click=lambda: apply_button_click(sql, True)
    )

    if on_click:
        st.rerun()


initialization()

columns = st.columns(6)

columns[0].button(
    'Channel', key='button_channel',
    use_container_width=True, on_click=current_table)
columns[1].button(
    'RCE', key='button_rce',
    use_container_width=True, on_click=current_table)
columns[2].button(
    'Agent', key='button_agent', 
    use_container_width=True, on_click=current_table)

columns[3].button(
    'RCE Target', key='button_rce_target',
    use_container_width=True, on_click=current_table)
columns[4].button(
    'Agent Target', key='button_agent_target', 
    use_container_width=True, on_click=current_table)

columns[5].button(
    'Daily Activation', key='button_activation', 
    use_container_width=True, on_click=current_table)

st.markdown(f'### Tabel {ss.edit_selection}')

match ss.edit_selection:
    case 'Channel':
        is_encounter_an_error()
        sql = edit_channel()

        if sql:
            apply_button(sql)

    case 'RCE':
        sql = edit_rce()
        is_encounter_an_error()
        
        if sql:
            apply_button(sql)

    case 'Agent':
        is_encounter_an_error()
        sql = edit_agent()
        
        if sql:
            apply_button(sql)

    case 'RCE Target':
        is_encounter_an_error()
        sql = edit_rce_target()
        
        if sql:
            apply_button(sql)

    case 'Agent Target':
        is_encounter_an_error()
        sql = edit_agent_target()
        
        if sql:
            apply_button(sql)

    case 'Daily Activation':
        col1, col2 = st.columns((2, 5))
        
        with col1:
            st.markdown('Unggah File **Daily Activation**')
            st.button(
                'Unggah File Daily Activation', key='button_upload_file',
                use_container_width=True, on_click=upload_file
            )

        with col2:
            is_encounter_an_error()
            sql = edit_activation()
            
            if sql:
                apply_button(sql)
    
    case _:
        pass