from streamlit import session_state as ss
from datetime import datetime, timedelta, date
from .database import fetch_data
import plotly.express as px
import streamlit as st
import pandas as pd


class visualization:
    @st.cache_data(ttl=300)
    def ordertype_linechart(data: pd.DataFrame):
        df = data.copy()

        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA'
        }
        df['order_type'] = df['order_type'].replace(order_type_rename)
        df['activation_date'] = pd.to_datetime(df['activation_date'])

        df = df.groupby(
                'activation_date'
            )['order_type'].value_counts().reset_index()
        df.rename(columns={
                'activation_date': 'Tanggal',
                'order_type': 'Tipe Order'
            }, inplace=True)
        
        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        df = df.pivot(
            index='Tanggal', columns='Tipe Order', values='count'
        )
        df = df.asfreq('D').reset_index()
        df = df.melt(
            id_vars='Tanggal', value_vars=['GA', 'CPP'],
            value_name='Jumlah Aktivasi'
        )

        fig = px.line(
            df, x='Tanggal', y='Jumlah Aktivasi', color='Tipe Order',
            color_discrete_sequence=['#FF8225', '#7AB2D3'], hover_data={
                'Tanggal': False
            }
        )
        fig.update_layout(
            hovermode='x unified',
            dragmode='pan',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                xanchor='left',
                y=1
            )
        )
        fig.update_xaxes(showline=True, showgrid=True)
        fig.update_yaxes(fixedrange=True)
        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)

    @st.cache_data(ttl=300)
    def revenue_areachart(data: pd.DataFrame):
        df = data.copy()

        df['activation_date'] = pd.to_datetime(df['activation_date'])
        df = df.groupby(
                'activation_date'
            )['guaranteed_revenue'].sum().reset_index()
        df.rename(columns={
                'activation_date': 'Tanggal',
                'guaranteed_revenue': 'Revenue'
            }, inplace=True)
        
        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        df = df.set_index('Tanggal').asfreq('D').reset_index()

        fig = px.area(
            df, x='Tanggal', y='Revenue',
            color_discrete_sequence=['#CC2B52'],
            hover_data={'Tanggal': False}
        )
        fig.update_layout(
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d',
            hovermode='x unified',
            dragmode='pan'
        )

        fig.update_xaxes(showline=True)
        fig.update_yaxes(fixedrange=True)

        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)

    @st.cache_data(ttl=300)
    def product_barchart(data: pd.DataFrame):
        df = data.copy()

        df['product_tenure'] = (df['product'] + ' - ' + df['tenure'].astype(str))
        df = df.value_counts(subset=['product_tenure', 'order_type'])
        df = df.reset_index()
        index_range = len(df['product_tenure'].unique())

        df.rename(columns={
            'product_tenure': 'Produk & Tenure',
            'count': 'Jumlah Aktivasi',
            'order_type': 'Tipe Order'
        }, inplace=True)

        fig = px.bar(
            df, x='Jumlah Aktivasi', y='Produk & Tenure',
            color='Tipe Order', text_auto=True,
            color_discrete_sequence=['#DBD3D3', '#FF7F3E', '#0D92F4'],
            category_orders={
                'Tipe Order': [
                    'Change Postpaid Plan', 'Migration', 'New Registration'
                ]
            }, hover_data={'Produk & Tenure': False}, hover_name='Produk & Tenure'
        )
        fig.update_layout(
            barcornerradius='20%',
            dragmode='pan',
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

    @st.cache_data(ttl=300)
    def revenue_barchart(data: pd.DataFrame):
        df = data.copy()

        df['activation_date'] = pd.to_datetime(df['activation_date'])
    
        df = df.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['guaranteed_revenue'].sum().reset_index()
        df.rename(columns={
                'activation_date': 'Tanggal',
                'guaranteed_revenue': 'Revenue'
            }, inplace=True)
        
        fig = px.bar(
            df, x='Tanggal', y='Revenue'
        )
        fig.update_layout(
            barcornerradius='20%',
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d',
            dragmode='pan'
        )
        fig.update_xaxes(
            tick0=df['Tanggal'].min(), dtick='M1', tickformat='%b %Y'
        )
        fig.update_yaxes(fixedrange=True)

        st.write(fig)

    @st.cache_data(ttl=300)
    def gacpp_barchart(data: pd.DataFrame):
        df = data.copy()
        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA'
        }
        df['order_type'] = df['order_type'].replace(order_type_rename)
        df['activation_date'] = pd.to_datetime(df['activation_date'])

        df = df.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['order_type'].value_counts().reset_index()
        df.rename(columns={
                'activation_date': 'Tanggal',
                'order_type': 'Tipe Order',
                'count': 'Jumlah Aktivasi'
            }, inplace=True)

        fig = px.bar(
            df, x='Tanggal', y='Jumlah Aktivasi',
            facet_row='Tipe Order'
        )
        fig.update_layout(barcornerradius='20%', dragmode='pan')
        fig.update_xaxes(
            showline=True,
            tick0=df['Tanggal'].min(),
            dtick='M1', tickformat='%b %Y'
        )
        fig.update_yaxes(fixedrange=True)

        st.write(fig)