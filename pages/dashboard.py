from modules import (
    init_configuration, init_sidebar, init_content, filter_dashboard,
    fetch_data, visualization as vis
)
from streamlit import session_state as ss
import streamlit as st
import pandas as pd


def initialization():
    init_configuration()

    ss.navigation = '📊 dashboard'
    init_content()
    init_sidebar()

def first_row(data: pd.DataFrame):
    col1, col2, col3 = st.columns(3)
    
    with st.container():
        with col1.container(border=True):
            vis.ordertype_linechart(data)

        with col2.container(border=True):
            vis.revenue_areachart(data)

        with col3.container(border=True):
            vis.product_barchart(data)

def second_row(data: tuple[pd.DataFrame]):
    col1, col2 = st.columns((2))
    
    with st.container():
        with col1.container(border=True):
            vis.gacpp_barchart(data)

        with col2.container(border=True):
            vis.revenue_barchart(data)


initialization()

with st.sidebar.expander('**Filter**', icon='🔍', expanded=True):
    filter_query = filter_dashboard('Daily Activation')

activation_data = fetch_data('Activation', filter_query['act']).reset_index()
target_data = fetch_data('RCE Target', filter_query['tar']).reset_index()

if not activation_data.empty:
    first_row(activation_data)
    second_row((activation_data, target_data))
else:
    message = """
        Tidak ditemukan data pada database aktivasi. Silahkan mengisi data
        di halaman database pada tabel **Daily Activation**.
    """
    st.warning(message, icon='⚠')