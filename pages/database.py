from modules import (check_login_state, init_sidebar, init_content, connect_db,
    check_connection)
from datetime import datetime
from streamlit import session_state as ss
import streamlit as st


def initialization():
    st.set_page_config(
        page_title='EJBN RCE Dashboard',
        page_icon='images/logo.png',
        initial_sidebar_state='collapsed',
        layout='wide'
    )
    check_login_state()

    ss.navigation = '💾 database'
    init_content()
    init_sidebar()

    if not ss.get('db_connection', False):
        ss.db_connection = connect_db()
    check_connection()


initialization()

with st.sidebar.expander('Filter', expanded=True, icon='🔍'):
    st.markdown('### Nama')
    st.text_input(
        'filter.name',
        placeholder='Filter berdasarkan nama',
        label_visibility='collapsed'
    )
    
    # rce_options = fetch_rce_names(_db_cursor).index
    # st.markdown('### RCE')
    # filter_input['RCE'] = st.multiselect(
    #     'Nama RCE', options=rce_options, default=None,
    #     placeholder='Filter berdasarkan RCE',
    #     label_visibility='collapsed')
    
    st.markdown('### Tanggal')
    st.date_input('filter.date', label_visibility='collapsed')
    
    st.markdown('### Status')
    status_opt = ('All', 'Active', 'Inactive')
    st.segmented_control(
        'filter.status', options=status_opt,
        default=status_opt[1], label_visibility='collapsed')

check_connection()