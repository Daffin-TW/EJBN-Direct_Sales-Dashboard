
from modules import (
    init_configuration, init_content, init_sidebar, edit_database,
    execute_sql_query, preprocessing_daily_activation, filter_edit
)
from streamlit import session_state as ss
import streamlit as st
import pandas as pd


def initialization():
    init_configuration()
    
    ss.navigation = '💾 database'
    init_content()
    init_sidebar()

    if not ss.get('edit_selection', False):
        ss.edit_selection = 'Channel'

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

def apply_button(sql: str, dialog=False):
    if (sql and not ss.get('invalid_edit', False) and
            not ss.get('done_editing', False)):
        return st.button(
            'Simpan Perubahan', key='apply_button',
            on_click=lambda: apply_button_click(sql, dialog)
        )

@st.dialog('Unggah File', width='large')
def upload_file():
    upload_file = st.file_uploader(
        'Unggah File Excel', key='uploaded_file',
        type=['xlsx'],
        label_visibility='collapsed'
    )

    if upload_file is None:
        st.markdown("""
            **Masukkan data dengan kolom berikut:**  
            - activation_date
            - Package_Rev
            - order_type
            - tenure
            - dealer_id
            - nik_sales
            - salesperson_nm
            - RCM
            - Tactical/Regular
            - Guaranteed Revenue (Mio)
        """)
        return None
    else:
        ss.done_editing = False
    
    df = pd.read_excel(upload_file)
    df = preprocessing_daily_activation(df)
    tanggal = [df['Date'].min(), df['Date'].max()]
    
    st.write(df)

    if ss.get('invalid_edit', False):
        st.stop()

    st.warning(
        f'Perubahan akan menghapus data dari tanggal **{tanggal[0]}** ' +
        f'sampai dengan **{tanggal[1]}**', icon='⚠'
    )
    
    sql = edit_database('Daily Activation', '', df)
    
    if apply_button(sql, dialog=True):
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

col1, col2 = st.columns((1, 5))
col1.markdown('#### Filter')

match ss.edit_selection:
    case 'Daily Activation':        
        with col1:
            filter_query = filter_edit(ss.edit_selection)

            st.markdown('Unggah File **Daily Activation**')
            st.button(
                'Unggah File Daily Activation', key='button_upload_file',
                use_container_width=True, on_click=upload_file
            )

        with col2:
            is_encounter_an_error()
            sql = edit_database(ss.edit_selection, filter_query)
            
            if sql:
                apply_button(sql)
    
    case _:
        with col1:
            filter_query = filter_edit(ss.edit_selection)
        with col2:
            is_encounter_an_error()
            sql = edit_database(ss.edit_selection, filter_query)
            
            if sql:
                apply_button(sql)