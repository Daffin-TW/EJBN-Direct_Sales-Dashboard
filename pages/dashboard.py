from modules import (
    init_configuration, init_sidebar, init_content, filter_dashboard,
    fetch_data, visualization as vis, filter_peragent
)
from streamlit import session_state as ss
import streamlit as st
import pandas as pd


def initialization():
    init_configuration(sidebar='expanded')

    ss.navigation = '📊 dashboard'
    init_content()
    init_sidebar()

def d1_first_row(data: pd.DataFrame):
    col1, col2 = st.columns(2)
    
    with st.container():
        with col1.container(border=True):
            vis.general.ordertype_linechart(data)

        with col2.container(border=True):
            vis.general.revenue_areachart(data)


def d1_second_row(data: tuple[pd.DataFrame]):
    col1, col2, col3 = st.columns(3)
    
    with st.container():
        with col1.container(border=True):
            vis.general.gacpp_barchart(data)

        with col2.container(border=True):
            vis.general.revenue_barchart(data)

        with col3.container(border=True):
            vis.general.product_barchart(data[0])

def d2_first_row(data: pd.DataFrame, agent_filter: bool = False):
    col1, col2 = st.columns(2)
    
    with st.container():
        with col1.container(border=True):
            vis.rce_comparison.ordertype_linechart(data, agent_filter)

        with col2.container(border=True):
            vis.rce_comparison.revenue_linechart(data, agent_filter)

def d2_second_row(data: pd.DataFrame):
    col1, col2 = st.columns(2)

    with st.container():
        with col1.container(border=True):
            vis.rce_comparison.product_barchart(data[0])
        
        with col2.container(border=True):
            vis.rce_comparison.achieve_barchart(data)


initialization()

dashboard_options = (
    'Umum', 'Perbandingan RCE'
)

with st.sidebar:
    st.markdown('## Pilihan Dashboard')
    st.selectbox(
        'SelectBox Dashboard', dashboard_options, key='dashboard_selection',
        placeholder='Pilih opsi dashboard', label_visibility='collapsed'
    )

st.markdown(f'### Dashboard {ss.dashboard_selection}')

match ss.dashboard_selection:
    case 'Umum':
        with st.spinner('Menghubungi database, mohon ditunggu...'):
            expander = st.sidebar.expander(
                '**Filter**', icon='🔍', expanded=True
            )
            with expander:
                filter_query = filter_dashboard('General')

        activation_data = fetch_data('Activation', filter_query['act']).reset_index()
        target_data = fetch_data('RCE Target', filter_query['tar']).reset_index()

        if not activation_data.empty:
            ss.data_is_empty = False
            d1_first_row(activation_data)
            d1_second_row((activation_data, target_data))
            
        else:
            ss.data_is_empty = True
            
    case 'Perbandingan RCE':
        with st.spinner('Menghubungi database, mohon ditunggu...'):
            expander = st.sidebar.expander(
                '**Filter**', icon='🔍', expanded=True
            )
            with expander:
                filter_query = filter_dashboard('General')

        activation_data = fetch_data('Activation', filter_query['act']).reset_index()
        target_data = fetch_data('RCE Target', filter_query['tar']).reset_index()

        if not activation_data.empty:
            ss.data_is_empty = False

            with expander:
                agent = filter_peragent()

            d2_first_row(activation_data, agent)
            d2_second_row((activation_data, target_data))

        else:
            ss.data_is_empty = True

    case _:
        f'Tidak ada pilihan dashboard {ss.dashboard_selection}'

if ss.get('data_is_empty', False):
    message = f"""
        Tidak ditemukan data pada database. Silahkan mengisi data
        di halaman database pada tabel **Daily Activation**.
    """
    st.warning(message, icon='⚠')