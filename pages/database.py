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


@st.dialog('Filter Tanggal', width='large')
def tanggal_input():
    st.logo('images/horizontal_long_logo.png', icon_image='images/logo.png',
            size='large')
    st.date_input('filter.date', label_visibility='collapsed')

    apply = st.button('Apply', key='tanggal_apply_button')

    if apply:
        st.rerun()


initialization()

tab_agent, tab_target, tab_activation = st.tabs(
    ('Agent', 'Target', 'Daily Activation'))

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
    tanggal_button = st.button('Edit Filter', 'tanggal_button',
                               use_container_width=True)
    if tanggal_button:
        tanggal_input()
    
    st.markdown('### Status')
    status_opt = ('All', 'Active', 'Inactive')
    st.segmented_control(
        'filter.status', options=status_opt,
        default=status_opt[1], label_visibility='collapsed')

with tab_agent:
    st.write('Halo Deck')

check_connection()