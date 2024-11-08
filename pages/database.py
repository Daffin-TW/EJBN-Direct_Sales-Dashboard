from modules import (
    init_configuration, init_sidebar, init_content,
    connect_db, check_connection, fetch_channel)
from datetime import datetime, timedelta
from streamlit import session_state as ss
import streamlit as st


def initialization():
    init_configuration()
    
    ss.navigation = '💾 database'
    init_content()
    init_sidebar()

    if not ss.get('db_connection', False):
        ss.db_connection = connect_db()
    check_connection()

# Show specific date filter
@st.dialog('Filter Tanggal', width='large')
def tanggal_input():
    st.logo('images/horizontal_long_logo.png', icon_image='images/logo.png',
            size='large')
    date_end = datetime.now()
    date_start = date_end - timedelta(days=30)

    col_start, col_end = st.columns(2)
    with col_start:
        st.markdown('### Date Start')
        st.date_input('filter_date_start', value=(date_start),
                      label_visibility='collapsed', format='DD/MM/YYYY')
    with col_end:
        st.markdown('### Date End')
        col_end.date_input('filter_date_start', value=(date_end),
                           label_visibility='collapsed', format='DD/MM/YYYY')

    apply = st.button('Apply', key='tanggal_apply_button')
    if apply:
        st.rerun()


initialization()

# Add a button to edit the database
st.button('⚙ Edit Database', 'edit_button', use_container_width=True)
if ss.edit_button:
    st.switch_page('pages/database_edit.py')

# Select database category
tab_agent, tab_target, tab_activation = st.tabs(
    ('Agent', 'Target', 'Daily Activation'))

# Add a filter function on the sidebar
with st.sidebar.expander('Filter', expanded=True, icon='🔍'):
    st.markdown('### Nama')
    st.text_input(
        'filter_name',
        placeholder='Filter berdasarkan nama',
        label_visibility='collapsed'
    )
    
    rce_options = ('Chentia Aisya Oktarina', 'Diaz Yusuf Zakaria', 'Ni Made Ayu Astariani Dewi')
    # rce_options = fetch_rce_names(_db_cursor).index
    st.markdown('### RCE')
    st.multiselect(
        'filter_rce', options=rce_options, default=None,
        placeholder='Filter berdasarkan RCE',
        label_visibility='collapsed')
    
    st.markdown('### Tanggal')
    tanggal_button = st.button('Edit Filter', 'tanggal_button',
                               use_container_width=True)
    if tanggal_button:
        tanggal_input()
    
    st.markdown('### Status')
    status_opt = ('All', 'Active', 'Inactive')
    st.segmented_control(
        'filter_status', options=status_opt,
        default=status_opt[1], label_visibility='collapsed')

# Show agent database
with tab_agent:
    container = st.container()

    col1, col2 = container.columns((1, 2))
    
    with col1.container(border=True, height=300):
        st.markdown('#### Channel')
        st.dataframe(fetch_channel(),
                     use_container_width=True)
            
    with col2.container(border=True, height=300):
        st.markdown('#### RCE')

        
    with container.container(border=True):
        st.markdown('#### Agent')
        
check_connection()