from modules import (
    init_configuration, init_sidebar, init_content, visualization as vis
)
from streamlit import session_state as ss
import streamlit as st


def initialization():
    init_configuration()

    ss.navigation = '📊 dashboard'
    init_content()
    init_sidebar()


initialization()

def first_row():
    col1, col2, col3 = st.columns(3)
    
    with st.container():
        with col2.container(border=True):
            vis.revenue_linechart()

        with col3.container(border=True):
            vis.product_barchart()

first_row()