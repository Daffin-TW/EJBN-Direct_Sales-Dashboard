from streamlit import session_state as ss
import streamlit as st


def init_content():
    st.logo('images/horizontal_long_logo.png', icon_image='images/logo.png',
            size='large')

    placeholder = st.container()
    col1, col2 = placeholder.columns((2, 4))

    col1.markdown(f'### {ss.navigation.title()}')
    col2_1, col2_2, col2_3 = col2.columns(3)
    
    if col2_1.button(
        '📊 Dashboard', 'dashboard_button',
        use_container_width=True) and ss.navigation != '📊 dashboard':
        st.switch_page('pages/dashboard.py')

    elif col2_2.button(
        '💾 Database', 'database_button',
        use_container_width=True) and ss.navigation != '💾 database':
        st.switch_page('pages/database.py')

    elif col2_3.button(
        '🖊 About', 'about_button',
        use_container_width=True) and ss.navigation != '🖊 about':
        st.switch_page('pages/about.py')
    
    st.divider()

def init_sidebar():
    with st.sidebar:
        st.divider()
        st.markdown('## Navigasi')

        options = ('📊 Dashboard', '💾 Database', '🖊 About')
        index = options.index(ss.navigation.title())
        nav_input = st.selectbox(
            'navigation_input', options, index=index,
            label_visibility='collapsed', placeholder='Pilih Halaman')
        
        if nav_input.lower() != ss.navigation:
            st.switch_page(f'pages/{nav_input.split()[-1].lower()}.py')