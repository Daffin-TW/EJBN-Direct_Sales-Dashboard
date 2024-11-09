from streamlit import session_state as ss
from modules import check_login_state
import streamlit as st


def init_configuration():
    st.set_page_config(
        page_title='EJBN RCE Dashboard',
        page_icon='images/logo.png',
        initial_sidebar_state='collapsed',
        layout='wide'
    )
    check_login_state()

def init_content():

    # Add a logo in sidebar
    st.logo('images/horizontal_long_logo.png', icon_image='images/logo.png',
            size='large')

    # Add a title and a button on page to navigate
    placeholder = st.container()
    col1, col2 = placeholder.columns((2, 4), vertical_alignment='bottom')
    col1.markdown(f'# {ss.navigation.title()}')

    button_columns = col2.columns(3)
    pages = {'dashboard': '📊 Dashboard',
             'database': '💾 Database',
             'about': '🖊 About'}
    
    # Create the button and the switch pages function
    for column, page in zip(button_columns, pages.keys()):
        if column.button(
            pages[page], f'{page}_button',
            use_container_width=True) and ss.navigation != pages[page].lower():
            ss.is_firsttime = True
            st.switch_page(f'pages/{page}.py')

    st.divider()

def init_sidebar():

    # Add a selectbox on sidebar to navigate
    with st.sidebar:
        st.divider()
        st.markdown('## Navigasi')

        options = ('📊 Dashboard', '💾 Database', '🖊 About')
        index = options.index(ss.navigation.title())
        nav_input = st.selectbox(
            'navigation_input', options, index=index,
            label_visibility='collapsed', placeholder='Pilih Halaman')
        
        # Switch pages if the navigation is not referring to current page
        if nav_input.lower() != ss.navigation:
            ss.is_firsttime = True
            st.switch_page(f'pages/{nav_input.split()[-1].lower()}.py')