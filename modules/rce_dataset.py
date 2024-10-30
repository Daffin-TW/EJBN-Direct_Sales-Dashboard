import streamlit as st
import pandas as pd

@st.cache_data
def get_dataset(csv_url: str = None) -> pd.DataFrame:
    if csv_url is not None:
        url = 'https://drive.google.com/uc?id=' + csv_url.split('/')[-2]
    else:
        # Newest clean dataset
        sheets_id = st.secrets.dataset.id
        url = 'https://drive.google.com/uc?id=' + sheets_id
    return pd.read_csv(url)

def load_dataset(csv_url: str = None) -> pd.DataFrame:
    with st.spinner('Importing the data...'):
        df = get_dataset(csv_url)

    return df