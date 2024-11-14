from .database import fetch_data, fetch_data_primary
import streamlit as st
import pandas as pd
import numpy as np


def tenure_extraction(data: str):
    token = data.split('-')
    if len(token) == 1:
        return 1
    else:
        return int(token[-1])

def product_extraction(data: str):
    token = data.rstrip('-2412369')
    return token

@st.cache_data(ttl=60, show_spinner=False)
def preprocessing_daily_activation(data: pd.DataFrame) -> pd.DataFrame:
    columns = [
        'activation_date', 'Package_Rev', 'order_type',
        'tenure', 'dealer_id', 'nik_sales', 'salesperson_nm', 'RCM',
        'Tactical/Regular', 'Guaranteed Revenue (Mio)'
    ]

    df = data[columns].copy()
    df = df[df['RCM'] != 'Indra Irawati'].reset_index(drop=True)

    df['activation_date'] = pd.to_datetime(
        df['activation_date'], format='%Y%m%d'
    ).dt.date
    df['tenure'] = df['Package_Rev'].apply(tenure_extraction)
    df['Guaranteed Revenue (Mio)'] = (
        df['Guaranteed Revenue (Mio)'] * 1000000
    ).astype(int)
    df['product'] = df['Package_Rev'].apply(product_extraction)
    
    agent = fetch_data('Agent').reset_index()
    agent.sort_values('Employment Date', inplace=True)
    agent.drop_duplicates(['ID', 'NIK'], keep='last', inplace=True)
    agent['ID'] = agent['ID'].astype(str)
    
    result = df.merge(agent, left_on='nik_sales', right_on='NIK', how='left')
    result.sort_values('activation_date', inplace=True)
    result.reset_index(drop=True, inplace=True)
    result['NIK'] = (
        result['ID'] + ': ' + result['NIK'] + ' - ' + result['dealer_id'] +
        ' - ' + result['Name']
    )

    selected_column = {
        'activation_date': 'Date', 'product': 'Product', 'tenure': 'Tenure',
        'NIK': 'Agent', 'order_type': 'Order Type',
        'Tactical/Regular': 'Tactical Regular',
        'Guaranteed Revenue (Mio)': 'Guaranteed Revenue'
    }

    result = result[selected_column.keys()]
    result.rename(columns=selected_column, inplace=True)

    return result