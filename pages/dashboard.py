from modules import (
    init_configuration, init_sidebar, init_content,
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
            vis.revenue_linechart(data)

        with col3.container(border=True):
            vis.product_barchart(data)

def second_row(data: pd.DataFrame):
    col1, col2, col3 = st.columns(3)
    
    with st.container():
        with col1.container(border=True):
            vis.gacpp_barchart(data, 'GA')

        with col2.container(border=True):
            vis.gacpp_barchart(data, 'CPP')

        with col3.container(border=True):
            vis.revenue_barchart(data)


initialization()

activation_data = fetch_data('Activation')

if not activation_data.empty:
    first_row(activation_data)
    second_row(activation_data)
else:
    message = """
        Tidak ditemukan data pada database aktivasi. Silahkan mengisi data
        di halaman database pada tabel **Daily Activation**
    """
    st.warning(message, icon='⚠')