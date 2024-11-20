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

vis.product_barchart()