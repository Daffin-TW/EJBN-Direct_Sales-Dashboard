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
    columns = {
        'activation_date', 'Package_Rev', 'order_type',
        'tenure', 'dealer_id', 'nik_sales', 'salesperson_nm', 'RCM',
        'Tactical/Regular', 'Guaranteed Revenue (Mio)'
    }

    check_columns = columns - set(data.columns)

    if check_columns:
        st.error(f'Tidak ada kolom {list(check_columns)}')
        st.stop()

    df = data[list(columns)].copy()

    df = df[df['dealer_id'].isin(['DS03', 'DS04', 'DS05'])]
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
        'NIK': 'Agent', 'nik_sales': 'NIK Sales', 'order_type': 'Order Type',
        'Tactical/Regular': 'Tactical Regular',
        'Guaranteed Revenue (Mio)': 'Guaranteed Revenue'
    }

    result = merge[selected_column.keys()].copy()
    result.rename(columns=selected_column, inplace=True)

    if any(result['Agent'].isna()):
        st.error('Terdapat Agent yang belum terdaftar pada database', icon='❗')
        st.write(
            merge[merge['NIK'].isna()][
                    ['dealer_id', 'nik_sales']
                ].drop_duplicates()
        )
        st.markdown('**Berikut data dengan Agent yang belum masuk database**')
        result = result[result['Agent'].isna()]
        result.drop(columns=['Agent'], inplace=True)
        ss.invalid_edit = True

    else:
        result.drop(columns=['NIK Sales'], inplace=True)
        ss.invalid_edit = False

    return result