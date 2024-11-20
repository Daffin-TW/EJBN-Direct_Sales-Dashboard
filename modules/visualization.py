from streamlit import session_state as ss
from datetime import datetime, timedelta, date
from .database import fetch_data
import plotly.express as px
import streamlit as st
import pandas as pd

class visualization:
    def revenue_linechart():
        df = fetch_data('Activation').copy()
        date_revenue = df.groupby(
                'activation_date'
            )['guaranteed_revenue'].sum().reset_index()
        date_revenue.rename(columns={
                'activation_date': 'Tanggal',
                'guaranteed_revenue': 'Revenue'
            }, inplace=True)
        
        maximum = date_revenue['Tanggal'].max().month
        minimum = date_revenue['Tanggal'].min().month
        line = [f'2024-{i+1}-1' for i in range(minimum, maximum)]

        fig = px.line(
            date_revenue, x='Tanggal', y='Revenue',
            color_discrete_sequence=['#CC2B52']
        )
        fig.update_layout(
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d',
        )
        for i in line:
            fig.add_vline(i, line_dash='dash', line_color='#FA812F')

        # fig.update_xaxes(minallowed=minimum, maxallowed=maximum)

        st.write(fig)

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
        fig.update_traces(insidetextanchor='middle')

        st.write(fig)