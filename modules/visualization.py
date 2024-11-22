from streamlit import session_state as ss
from datetime import datetime, timedelta, date
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np


class visualization:
    @st.cache_data(ttl=300, show_spinner=False)
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
            color_discrete_sequence=['#FF8225', '#7AB2D3'], height=400,
            hover_data={
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

    @st.cache_data(ttl=300, show_spinner=False)
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
            df, x='Tanggal', y='Revenue', height=400,
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

    @st.cache_data(ttl=300, show_spinner=False)
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
            color='Tipe Order', text_auto=True,height=400,
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

    @st.cache_data(ttl=300, show_spinner=False)
    def revenue_barchart(data: tuple[pd.DataFrame]):
        df_act, df_tar = data[0].copy(), data[1].copy()

        columns_rename = {
            'activation_date': 'Tanggal',
            'target_date': 'Tanggal',
            'target_revenue': 'Target',
            'guaranteed_revenue': 'Achieve'
        }

        df_act['activation_date'] = pd.to_datetime(df_act['activation_date'])
        df_act = df_act.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['guaranteed_revenue'].sum().reset_index()
        df_act['activation_date'] = df_act['activation_date'].map(
            lambda dt: dt.replace(day=1)
        )
        df_act.rename(columns=columns_rename, inplace=True)

        df_tar.rename(columns=columns_rename, inplace=True)
        df_tar['Tanggal'] = pd.to_datetime(df_tar['Tanggal'])
        df_tar = df_tar.groupby(['Tanggal']).sum().reset_index()
        df_tar['Target'] = df_tar['Target'].replace(0, np.nan)
        
        df = pd.merge(df_act, df_tar, how='outer', on='Tanggal')

        fig = px.scatter(
            df, x='Tanggal', y='Target',
            color_discrete_sequence=['red'], text='Target'
        )
        fig.update_traces(
            legendgrouptitle_text='Target',
            legendgroup='group',
            name='Target Revenue',
            showlegend=True,
            textposition='bottom right',
            marker_size=10,
            marker_symbol='diamond-wide',
            hovertemplate='Target: Rp%{y:,}',
            texttemplate='Rp%{y:,}',
            textfont=dict(color='black')
        )

        main_fig = px.bar(
            df_act, x='Tanggal', y='Achieve', height=400,
            color_discrete_sequence=['orange']
        )
        main_fig.update_traces(hovertemplate='Avhieve : Rp%{y:,}')
        main_fig.add_trace(fig.data[0])
        main_fig.update_layout(
            yaxis_tickformat=',',
            barcornerradius='20%',
            dragmode='pan',
            hovermode='x'
        )
        main_fig.update_xaxes(dtick='M1', tickformat='%b %Y')
        main_fig.update_yaxes(fixedrange=True)

        st.write(main_fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def gacpp_barchart(data: tuple[pd.DataFrame]):
        df_act, df_tar = data[0].copy(), data[1].copy()

        columns_rename = {
            'activation_date': 'Tanggal',
            'target_date': 'Tanggal',
            'order_type': 'Tipe Order',
            'count': 'Achieve'
        }

        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA',
            'target_ga': 'GA',
            'target_cpp': 'CPP'
        }

        df_act['order_type'] = df_act['order_type'].replace(order_type_rename)
        df_act['activation_date'] = pd.to_datetime(df_act['activation_date'])
        df_act = df_act.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['order_type'].value_counts().reset_index()
        df_act['activation_date'] = df_act['activation_date'].map(
            lambda dt: dt.replace(day=1)
        )
        df_act.rename(columns=columns_rename, inplace=True)

        df_tar.rename(columns=columns_rename, inplace=True)
        df_tar['Tanggal'] = pd.to_datetime(df_tar['Tanggal'])
        df_tar = df_tar.melt(
            'Tanggal', ('target_ga', 'target_cpp'),
            'Tipe Order', 'Target'
        )
        df_tar = df_tar.groupby(['Tanggal', 'Tipe Order']).sum().reset_index()
        df_tar['Tipe Order'] = df_tar['Tipe Order'].replace(order_type_rename)
        df_tar['Target'] = df_tar['Target'].replace(0, np.nan)

        df = pd.merge(df_act, df_tar, how='outer', on=['Tanggal', 'Tipe Order'])

        fig = px.scatter(
            df, x='Tanggal', y='Target', color='Tipe Order',
            color_discrete_sequence=['red'], text='Target'
        )
        fig.update_traces(
            legendgrouptitle_text='Target',
            legendgroup='group',
            showlegend=True,
            textposition='bottom right',
            marker_size=10,
            marker_symbol='diamond-wide',
            hovertemplate='Target: %{y}',
            textfont=dict(color='black')
        )

        main_fig = px.bar(
            df_act, x='Tanggal', y='Achieve',
            facet_col='Tipe Order', height=400,
            color_discrete_sequence=['orange']
        )
        main_fig.update_traces(hovertemplate='Achieve : %{y}')
        main_fig.add_trace(fig.data[0], row=1, col=2)
        main_fig.add_trace(fig.data[1], row=1, col=1)
        main_fig.update_layout(
            barcornerradius='20%',
            dragmode='pan',
            hovermode='x'
        )
        main_fig.update_xaxes(
            showline=True,
            dtick='M1', tickformat='%b %Y'
        )
        main_fig.update_yaxes(fixedrange=True)

        st.write(main_fig)