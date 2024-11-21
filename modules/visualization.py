from streamlit import session_state as ss
from datetime import datetime, timedelta, date
from .database import fetch_data
import plotly.express as px
import streamlit as st
import pandas as pd

class visualization:
    def revenue_barchart(data: pd.DataFrame):
        df = data.copy()

        df['activation_date'] = pd.to_datetime(df['activation_date'])
    
        revenue = df.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['guaranteed_revenue'].sum().reset_index()
        revenue.rename(columns={
                'activation_date': 'Tanggal',
                'guaranteed_revenue': 'Revenue'
            }, inplace=True)
        
        fig = px.bar(
            revenue, x='Tanggal', y='Revenue'
        )
        fig.update_layout(
            barcornerradius='20%',
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d'
        )
        fig.update_xaxes(
            tick0=revenue['Tanggal'].min(), dtick='M1', tickformat='%b %Y'
        )
        fig.update_yaxes(fixedrange=True)

        st.write(fig)

    def gacpp_barchart(data: pd.DataFrame, order_type: str):
        df = data.copy()
        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA'
        }
        df['order_type'] = df['order_type'].replace(order_type_rename)
        df = df[df['order_type'] == order_type]
        df['activation_date'] = pd.to_datetime(df['activation_date'])

        ga = df.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['order_type'].count().reset_index()
        ga.rename(columns={
                'activation_date': 'Tanggal',
                'order_type': 'Jumlah Aktivasi'
            }, inplace=True)
        
        fig = px.bar(
            ga, x='Tanggal', y='Jumlah Aktivasi'
        )
        fig.update_layout(barcornerradius='20%')
        fig.update_xaxes(
            tick0=ga['Tanggal'].min(), dtick='M1', tickformat='%b %Y'
        )
        fig.update_yaxes(fixedrange=True)

        st.write(fig)

    def ordertype_linechart(data: pd.DataFrame):
        df = data.copy()

        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA'
        }
        df['order_type'] = df['order_type'].replace(order_type_rename)
        df['activation_date'] = pd.to_datetime(df['activation_date'])

        order_type = df.groupby(
                'activation_date'
            )['order_type'].value_counts().reset_index()
        order_type.rename(columns={
                'activation_date': 'Tanggal',
                'order_type': 'Tipe Order'
            }, inplace=True)
        
        minimum = order_type['Tanggal'].min()
        maximum = order_type['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        order_type = order_type.pivot(
            index='Tanggal', columns='Tipe Order', values='count'
        )
        order_type = order_type.asfreq('D').reset_index()
        order_type = order_type.melt(
            id_vars='Tanggal', value_vars=['GA', 'CPP'],
            value_name='Jumlah Aktivasi'
        )

        fig = px.line(
            order_type, x='Tanggal', y='Jumlah Aktivasi', color='Tipe Order',
            color_discrete_sequence=['#FF8225', '#7AB2D3'],
        )
        fig.update_layout(
            hovermode='x unified', legend=dict(
                orientation='h',
                yanchor='bottom',
                xanchor='left',
                y=1
            )
        )
        fig.update_xaxes(showline=True)
        fig.update_yaxes(fixedrange=True)
        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)

    def revenue_linechart(data: pd.DataFrame):
        df = data.copy()

        df['activation_date'] = pd.to_datetime(df['activation_date'])
        revenue = df.groupby(
                'activation_date'
            )['guaranteed_revenue'].sum().reset_index()
        revenue.rename(columns={
                'activation_date': 'Tanggal',
                'guaranteed_revenue': 'Revenue'
            }, inplace=True)
        
        minimum = revenue['Tanggal'].min()
        maximum = revenue['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        revenue = revenue.set_index('Tanggal').asfreq('D').reset_index()

        fig = px.line(
            revenue, x='Tanggal', y='Revenue',
            color_discrete_sequence=['#CC2B52']
        )
        fig.update_layout(
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d',
            hovermode='x unified'
        )

        fig.update_xaxes(showline=True)
        fig.update_yaxes(fixedrange=True)
        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)

    def product_barchart(data: pd.DataFrame):
        df = data.copy()

        df['product_tenure'] = (df['product'] + ' - ' + df['tenure'].astype(str))
        product = df.value_counts(subset=['product_tenure', 'order_type'])
        product = product.reset_index()
        index_range = len(product['product_tenure'].unique())

        product.rename(columns={
            'product_tenure': 'Produk & Tenure',
            'count': 'Jumlah Aktivasi',
            'order_type': 'Tipe Order'
        }, inplace=True)

        fig = px.bar(
            product, x='Jumlah Aktivasi', y='Produk & Tenure',
            color='Tipe Order', text_auto=True,
            color_discrete_sequence=['#DBD3D3', '#FF7F3E', '#0D92F4'],
            category_orders={
                'Tipe Order': [
                    'Change Postpaid Plan', 'Migration', 'New Registration'
                ]
            }
        )
        fig.update_layout(
            barcornerradius='20%',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                xanchor='left',
                y=1
            )
        )
        fig.update_yaxes(
            categoryorder='total ascending',
            range=[index_range - 10.5, index_range],
            minallowed=0, maxallowed=index_range
        )
        fig.update_xaxes(showgrid=True, minallowed=0)
        fig.update_traces(insidetextanchor='middle')

        st.write(fig)