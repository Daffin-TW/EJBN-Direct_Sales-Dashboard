from streamlit import session_state as ss
import streamlit as st


def init_content():
    st.logo('images/logo.png')

    placeholder = st.container()
    col1, col2 = placeholder.columns((1, 2))

    col1.markdown('### The Title')
    col2_1, col2_2, col2_3 = col2.columns(3)
    if col2_1.button('Dashboard', 'dashboard_button', use_container_width=True):
        st.switch_page('pages/dashboard.py')
    elif col2_2.button('Database', 'database_button', use_container_width=True):
        st.switch_page('pages/database.py')
    elif col2_3.button('About', 'about_button', use_container_width=True):
        st.switch_page('pages/about.py')
    
    st.divider()

# def nav_callback():
#     st.write(f'{ss.navigation}')
#     st.switch_page(f'pages/{ss.navigation}.py')

def init_sidebar():
    with st.sidebar:
        st.html('<h1 style="text-align: center">EJBN Direct Sales dashboard</h1>')
        st.divider()
        st.markdown('## Navigasi')

        options = ('Dashboard', 'Database', 'About')
        nav_input = st.selectbox(
            'navigation_input', options,
            label_visibility='collapsed', placeholder='Pilih Halaman')
        
        if nav_input.lower() != ss.navigation.lower():
            st.write(f'{nav_input}')
            st.switch_page(f'pages/{nav_input.lower()}.py')