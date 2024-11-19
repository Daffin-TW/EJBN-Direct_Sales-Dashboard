from modules import (
    init_configuration, init_sidebar, init_content,
    connect_db, check_connection, fetch_data)
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


initialization()

# Add a button to edit the database
with st.sidebar:
    st.button(
        '⚙ Edit Database', 'edit_button',
        use_container_width=True, type='primary'
    )
    if ss.edit_button:
        st.switch_page('pages/database_edit.py')

# Select database category
tab_agent, tab_target, tab_activation = st.tabs(
    ('Agent', 'Target', 'Daily Activation')
)

# Show agent database
with tab_agent:
    container = st.container()

    col1, col2 = container.columns((1, 2))
    
    with col1.container(border=True, height=300):
        st.markdown('#### Channel')
        st.dataframe(fetch_data('Channel'), use_container_width=True)
            
    with col2.container(border=True, height=300):
        st.markdown('#### RCE')
        st.dataframe(
            fetch_data('Rce'), use_container_width=True, hide_index=True,
            column_config={
                'Employment Date': st.column_config.DateColumn(
                    format='DD/MM/YYYY'),
                'End Date': st.column_config.DateColumn(
                    format='DD/MM/YYYY')}
        )
        
    with container.container(border=True):
        st.markdown('#### Agent')
        st.dataframe(
            fetch_data('Agent'), use_container_width=True, hide_index=True,
            column_config={
                'Employment Date': st.column_config.DateColumn(
                    format='DD/MM/YYYY'),
                'End Date': st.column_config.DateColumn(
                    format='DD/MM/YYYY')}
        )

with tab_target:
    col1, col2 = st.columns(2)

    with col1.container(border=True, height=700):
        st.markdown('#### Target RCE')
        st.dataframe(
            fetch_data('RCE Target'), use_container_width=True, height=600,
            hide_index=True, column_config={
                'Tahun': st.column_config.NumberColumn(
                    step=1, format='%i')}
        )

    with col2.container(border=True, height=700):
        st.markdown('#### Target Agent')
        st.dataframe(
            fetch_data('Agent Target'), use_container_width=True, height=600,
            hide_index=True, column_config={
                'Tahun': st.column_config.NumberColumn(
                    step=1, format='%i')}
        )

with tab_activation:
    with st.container(border=True, height=700):
        st.markdown('#### Daily Activation')
        st.dataframe(
            fetch_data('Activation'), use_container_width=True, height=600,
            hide_index=True, column_config={
                'Date': st.column_config.DateColumn(format='DD/MM/YYYY')}
        )

check_connection()