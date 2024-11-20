from streamlit import session_state as ss
from .database import fetch_data
import plotly.express as px
import streamlit as st
import pandas as pd

class visualization:
    def product_barchart():
        df = fetch_data('Activation').copy()
        df['product_tenure'] = (df['product'] + ' - ' + df['tenure'].astype(str))
        product_values = df.value_counts(subset=['product_tenure', 'order_type'])
        product_values = product_values.reset_index()
        index_range = len(product_values['product_tenure'].unique())

        product_values.rename(columns={
            'product_tenure': 'Produk & Tenure',
            'count': 'Jumlah',
            'order_type': 'Tipe Order'
        }, inplace=True)

        fig = px.bar(
            product_values, x='Jumlah', y='Produk & Tenure',
            color='Tipe Order', text_auto=True,
            color_discrete_sequence=['#DBD3D3', '#FF7F3E', '#0D92F4'],
            category_orders={
                'Tipe Order': [
                    'Change Postpaid Plan', 'Migration', 'New Registration'
                ]
            }
        )
        fig.update_yaxes(
            categoryorder='total ascending',
            range=[index_range - 10.5, index_range]
        )
        fig.update_xaxes(showgrid=True)
        fig.update_layout(legend=dict(
            orientation='h',
            yanchor='bottom',
            xanchor='left',
            y=1
        ))
        fig.update_traces(insidetextanchor="middle")

        st.write(fig)