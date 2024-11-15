from streamlit import session_state as ss
from .database import fetch_data
import streamlit as st
import pandas as pd


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
    
    merge = df.merge(agent, left_on='nik_sales', right_on='NIK', how='left')
    merge.sort_values('activation_date', inplace=True)
    merge.reset_index(drop=True, inplace=True)
    merge['NIK'] = (
        merge['ID'] + ': ' + merge['NIK'] + ' - ' + merge['dealer_id'] +
        ' - ' + merge['Name']
    )

    selected_column = {
        'activation_date': 'Date', 'product': 'Product', 'tenure': 'Tenure',
        'NIK': 'Agent', 'order_type': 'Order Type',
        'Tactical/Regular': 'Tactical Regular',
        'Guaranteed Revenue (Mio)': 'Guaranteed Revenue'
    }

    result = merge[selected_column.keys()].copy()
    result.rename(columns=selected_column, inplace=True)

    if not all(result['Agent'].isna()):
        st.error('Terdapat Agent yang belum terdaftar pada database', icon='❗')
        st.write(merge[merge['NIK'].isna()]['nik_sales'].unique().tolist())
        result = result[result['Agent'].isna()]
        ss.invalid_edit = True
    else:
        ss.invalid_edit = False

    return result