from streamlit import session_state as ss
from datetime import datetime, timedelta, date
from plotly.subplots import make_subplots
from modules import filter_peragent
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np


# CONSTANT
TITLE_FONT_COLOR = {'font_color': 'black'}


class general:
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
        
        df = df.pivot(
            index='Tanggal', columns='Tipe Order', values='count'
        )
        df = df.asfreq('D').reset_index()
        df = df.melt(
            id_vars='Tanggal', value_vars=['GA', 'CPP'],
            value_name='Jumlah Aktivasi'
        )

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        fig = px.line(
            df, x='Tanggal', y='Jumlah Aktivasi', color='Tipe Order',
            color_discrete_sequence=['#FF8225', '#7AB2D3'], height=400,
            hover_data={
                'Tanggal': False
            }
        )
        fig.update_layout(hovermode='x unified', dragmode='pan')
        fig.update_legends(orientation='h', yanchor='bottom', xanchor='left', y=1)
        fig.update_xaxes(showline=True, title=TITLE_FONT_COLOR)
        fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)
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
        df = df.set_index('Tanggal').asfreq('D').reset_index()

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

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

        fig.update_xaxes(showline=True, title=TITLE_FONT_COLOR)
        fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)

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
        fig.update_layout(barcornerradius='20%', dragmode='pan')
        fig.update_legends(orientation='h', yanchor='bottom', xanchor='left', y=1)
        fig.update_yaxes(
            categoryorder='total ascending', title=TITLE_FONT_COLOR,
            range=[index_range - 10.5, index_range],
            minallowed=0, maxallowed=index_range
        )
        fig.update_xaxes(minallowed=0, title=TITLE_FONT_COLOR)
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
        
        df = pd.merge(df_act, df_tar, how='left', on='Tanggal')

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
            textfont_color='black'
        )

        main_fig = px.bar(
            df_act, x='Tanggal', y='Achieve', height=400,
            color_discrete_sequence=['orange']
        )
        main_fig.update_traces(hovertemplate='Achieve : Rp%{y:,}')
        main_fig.add_trace(fig.data[0])
        main_fig.update_layout(
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d',
            barcornerradius='20%',
            dragmode='pan',
            hovermode='x'
        )
        main_fig.update_xaxes(
            dtick='M1', tickformat='%b %Y', title=TITLE_FONT_COLOR
        )
        main_fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)

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

        df = pd.merge(df_act, df_tar, how='left', on=['Tanggal', 'Tipe Order'])

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
            textfont_color='black'
        )

        main_fig = px.bar(
            df_act, x='Tanggal', y='Achieve',
            facet_col='Tipe Order', height=400,
            color_discrete_sequence=['orange']
        )
        main_fig.update_traces(hovertemplate='Achieve : %{y}')
        main_fig.add_trace(fig.data[0], row=1, col=2)
        main_fig.add_trace(fig.data[1], row=1, col=1)
        main_fig.for_each_annotation(
            lambda a: a.update(text=a.text.split('=')[1])
        )
        main_fig.update_layout(
            barcornerradius='20%',
            dragmode='pan',
            hovermode='x'
        )
        main_fig.update_xaxes(
            showline=True, dtick='M1', tickformat='%b %Y', title=TITLE_FONT_COLOR
        )
        main_fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)

        st.write(main_fig)

class rce_comparison:
    @st.cache_data(ttl=300, show_spinner=False)
    def ordertype_linechart(data: pd.DataFrame, agent_filter=False):
        df = data.copy()

        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA'
        }
        df['order_type'] = df['order_type'].replace(order_type_rename)
        df['activation_date'] = pd.to_datetime(df['activation_date'])
        df['Bulan'] = df['activation_date'].dt.month
        agent = df.groupby(['Bulan', 'rce'])['agent_id'].nunique().reset_index()

        df = df.groupby(
                ['activation_date', 'rce']
            )['order_type'].value_counts().reset_index()
        df.rename(columns={
                'activation_date': 'Tanggal',
                'order_type': 'Tipe Order',
                'rce': 'RCE'
            }, inplace=True)
        df = df.pivot(
            index=['Tanggal', 'RCE'], columns='Tipe Order', values='count'
        )
        df = df.unstack().asfreq('D').stack(future_stack=True).reset_index()
        df = df.melt(
            id_vars=['Tanggal', 'RCE'], value_vars=['GA', 'CPP'],
            value_name='count'
        )
        df['count'] = df['count'].fillna(0)
        df['Jumlah Kumulatif Aktivasi'] = df.groupby(
                ['RCE', 'Tipe Order']
            )['count'].cumsum()
        df['Bulan'] = df['Tanggal'].dt.month
        
        if agent_filter:
            df = df.merge(
                agent, left_on=['Bulan', 'RCE'], right_on=['Bulan', 'rce']
            )
            df['Jumlah Kumulatif Aktivasi'] = (
                df['Jumlah Kumulatif Aktivasi'] / df['agent_id']
            )

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        fig = px.line(
            df, x='Tanggal', y='Jumlah Kumulatif Aktivasi',
            color='RCE', height=500, line_dash='Tipe Order',
            color_discrete_sequence=px.colors.qualitative.Dark2,
            hover_data={
                'Tanggal': False
            }
        )
        fig.for_each_trace(
            lambda t: t.update(
                legendgroup=t.name.split(', ')[-1],
                legendgrouptitle={'text': t.name.split(', ')[-1]},
                name=t.name.split(', ')[0].split(': ')[-1],
                hovertemplate='%{y:.0f}'
            )
        )
        fig.update_layout(hovermode='x unified', dragmode='pan')
        fig.update_legends(orientation='h', yanchor='bottom', xanchor='left', y=1)
        fig.update_xaxes(showline=True, title=TITLE_FONT_COLOR)
        fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)
        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def revenue_linechart(data: pd.DataFrame, agent_filter=False):
        df = data.copy()

        df['activation_date'] = pd.to_datetime(df['activation_date'])
        df['Bulan'] = df['activation_date'].dt.month
        agent = df.groupby(['Bulan', 'rce'])['agent_id'].nunique().reset_index()

        df = df.groupby(
                ['activation_date', 'rce']
            )['guaranteed_revenue'].sum().reset_index()
        df.rename(columns={
                'activation_date': 'Tanggal',
                'guaranteed_revenue': 'Kumulatif Revenue',
                'rce': 'RCE'
            }, inplace=True)
        df = df.set_index(['Tanggal', 'RCE'])
        df = df.unstack().asfreq('D').stack(future_stack=True).reset_index()
        df['Kumulatif Revenue'] = df['Kumulatif Revenue'].fillna(0)
        df['Kumulatif Revenue'] = df.groupby(
                ['RCE']
            )['Kumulatif Revenue'].cumsum()
        df['Bulan'] = df['Tanggal'].dt.month

        if agent_filter:
            df = df.merge(
                agent, left_on=['Bulan', 'RCE'], right_on=['Bulan', 'rce']
            )
            df['Kumulatif Revenue'] = df['Kumulatif Revenue'] / df['agent_id']

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        fig = px.line(
            df, x='Tanggal', y='Kumulatif Revenue',
            color='RCE', height=500,
            color_discrete_sequence=px.colors.qualitative.Dark2,
            hover_data={
                'Tanggal': False
            }
        )
        fig.for_each_trace(
            lambda t: t.update(
                name=t.name.split(': ')[-1], hovertemplate='%{y}',
            )
        )
        fig.update_layout(
            hovermode='x unified',
            dragmode='pan',
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d'
        )
        fig.update_legends(orientation='h', yanchor='bottom', xanchor='left', y=1)
        fig.update_xaxes(showline=True, title=TITLE_FONT_COLOR)
        fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)
        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def product_barchart(data: pd.DataFrame):
        df = data.copy()

        df['product_tenure'] = (df['product'] + ' - ' + df['tenure'].astype(str))
        df = df.value_counts(subset=['rce', 'product_tenure', 'order_type'])
        df = df.reset_index()

        df.rename(columns={
            'product_tenure': 'Produk & Tenure',
            'count': 'Jumlah Aktivasi',
            'order_type': 'Tipe Order',
            'rce': 'RCE'
        }, inplace=True)

        fig = px.bar(
            df, x='Jumlah Aktivasi', y='Produk & Tenure', facet_row='RCE',
            color='Tipe Order', text_auto=True, height=700,
            color_discrete_sequence=['#DBD3D3', '#FF7F3E', '#0D92F4'],
            category_orders={
                'Tipe Order': [
                    'Change Postpaid Plan', 'Migration', 'New Registration'
                ]
            }, hover_data={'Produk & Tenure': False}, hover_name='Produk & Tenure'
        )
        fig.update_layout(barcornerradius='20%', dragmode='pan')
        fig.update_legends(orientation='h', yanchor='bottom', xanchor='left', y=1)
        fig.update_yaxes(
            range=[-0.5, 2.5], categoryorder='total descending',
            minallowed=-0.5, matches=None, title=TITLE_FONT_COLOR
        )
        fig.update_xaxes(minallowed=0, showline=True, title=TITLE_FONT_COLOR)
        fig.update_traces(insidetextanchor='middle')
        fig.for_each_annotation(
            lambda a: a.update(text=a.text.split(': ')[-1], xshift=-5)
        )

        st.write(fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def achieve_barchart(data: tuple[pd.DataFrame]):
        df_act, df_tar = data[0].copy(), data[1].copy()

        columns_rename = {
            'activation_date': 'Tanggal',
            'target_date': 'Tanggal',
            'order_type': 'Tipe Order',
            'rce': 'RCE',
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
                [pd.Grouper(key='activation_date', freq='ME'), 'rce']
            )['order_type'].value_counts().reset_index()
        df_act['activation_date'] = df_act['activation_date'].map(
            lambda dt: dt.replace(day=1)
        )
        df_act.rename(columns=columns_rename, inplace=True)

        df_tar.rename(columns=columns_rename, inplace=True)
        df_tar['Tanggal'] = pd.to_datetime(df_tar['Tanggal'])
        df_tar = df_tar.melt(
            ['Tanggal', 'RCE'], ('target_ga', 'target_cpp'),
            'Tipe Order', 'Target'
        )
        df_tar = df_tar.groupby(
                ['Tanggal', 'Tipe Order', 'RCE']
            ).sum().reset_index()
        df_tar['Tipe Order'] = df_tar['Tipe Order'].replace(order_type_rename)
        df_tar['Target'] = df_tar['Target'].replace(0, np.nan)

        df = pd.merge(
            df_act, df_tar, how='outer', on=['Tanggal', 'Tipe Order', 'RCE']
        )
        df['Persentase Achieve (%)'] = (df['Achieve'] / df['Target']) * 100
        df.dropna(inplace=True)

        fig = px.bar(
            df, x='Tanggal', y='Persentase Achieve (%)', barmode='group',
            color='RCE', facet_row='Tipe Order', height=700, text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Dark2
        )

        fig.for_each_annotation(
            lambda a: a.update(text=a.text.split('=')[1], xshift=-5)
        )
        fig.for_each_yaxis(lambda a: a.update(ticksuffix='%'))
        fig.for_each_trace(lambda t: t.update(name=t.name.split(': ')[-1]))
        fig.update_layout(barcornerradius='20%', dragmode='pan')
        fig.update_legends(orientation='h', yanchor='bottom', xanchor='left', y=1)
        fig.update_traces(
            textposition='outside', 
            texttemplate='%{y:.1f}%',
            hovertemplate='%{y:.1f}% | %{x}',
            textfont_color='black'
        )
        fig.update_xaxes(
            showline=True, dtick='M1', tickformat='%b %Y', title=TITLE_FONT_COLOR
        )
        fig.update_yaxes(minallowed=0, matches=None, title=TITLE_FONT_COLOR)
        fig.add_hline(
            100, line_dash='dash', line_color='red',
            annotation_text='Target', annotation_position='bottom right',
            annotation_font_color='red'
        )

        st.write(fig)

class rce_statistics:
    @st.cache_data(ttl=300, show_spinner=False)
    def ordertype_linechart(data: tuple[pd.DataFrame]):
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
                'activation_date'
            )['order_type'].value_counts().reset_index()
        df_act.rename(columns=columns_rename, inplace=True)
        df_act = df_act.pivot(
            index=['Tanggal'], columns='Tipe Order', values='Achieve'
        )
        df_act = df_act.asfreq('D').reset_index()
        df_act = df_act.melt(
            id_vars=['Tanggal'], value_vars=['GA', 'CPP'],
            value_name='Achieve'
        )
        df_act['Achieve'] = df_act['Achieve'].fillna(0)
        df_act['Bulan'] = df_act['Tanggal'].dt.month
        df_act['Jumlah Aktivasi'] = df_act.groupby(
                ['Tipe Order', 'Bulan']
            )['Achieve'].cumsum()
        
        df_tar.rename(columns=columns_rename, inplace=True)
        df_tar['Tanggal'] = pd.to_datetime(df_tar['Tanggal'])
        df_tar['Bulan'] = df_tar['Tanggal'].dt.month
        df_tar = df_tar.melt(
            'Bulan', ('target_ga', 'target_cpp'),
            'Tipe Order', 'Target'
        )
        df_tar = df_tar.groupby(
                ['Bulan', 'Tipe Order']
            )['Target'].sum().reset_index()
        df_tar['Tipe Order'] = df_tar['Tipe Order'].replace(order_type_rename)
        df_tar['Target'] = df_tar['Target'].replace(0, np.nan)

        df = pd.merge(df_act, df_tar, how='left', on=['Bulan', 'Tipe Order'])
        df['Target Harian'] = df['Target'] / df['Tanggal'].dt.daysinmonth
        df['Target Harian'] = df['Target Harian'].astype(float)
        df['Target Harian'] = df.groupby(
                ['Bulan', 'Tipe Order']
            )['Target Harian'].cumsum()

        month_year = df['Tanggal'].map(lambda dt: dt.replace(day=1)).unique()
        for tanggal in month_year:
            df.loc[len(df)] = [
                tanggal, 'GA', np.nan, np.nan, np.nan, np.nan, np.nan
            ]
            df.loc[len(df)] = [
                tanggal, 'CPP', np.nan, np.nan, np.nan, np.nan, np.nan
            ]
        df.sort_values(
            by=['Tipe Order', 'Tanggal', 'Achieve'],
            ascending=False, inplace=True
        )

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        fig = px.line(
            df, x='Tanggal', y='Target Harian', color_discrete_sequence=['red'],
            line_dash='Tipe Order',
            hover_data={
                'Tanggal': False
            }
        )
        fig.update_traces(
            legendgrouptitle_text='Target',
            legendgroup='target',
            hovertemplate='%{y:.0f}'
        )
        main_fig = px.line(
            df, x='Tanggal', y='Jumlah Aktivasi',
            height=500, line_dash='Tipe Order',
            color_discrete_sequence=['#7AB2D3'],
            hover_data={
                'Tanggal': False
            }
        )
        main_fig.update_traces(
            legendgrouptitle_text='Achieve',
            legendgroup='achieve',
            hovertemplate='%{y}'
        )
        main_fig.add_traces(fig.data)
        main_fig.update_layout(hovermode='x unified', dragmode='pan')
        main_fig.update_legends(
            orientation='h', yanchor='bottom', xanchor='left', y=1
        )
        main_fig.update_xaxes(showline=True, title=TITLE_FONT_COLOR)
        main_fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)
        for i in line:
            main_fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(main_fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def revenue_areachart(data: tuple[pd.DataFrame]):
        df_act, df_tar = data[0].copy(), data[1].copy()

        columns_rename = {
            'activation_date': 'Tanggal',
            'target_date': 'Tanggal',
            'guaranteed_revenue': 'Revenue',
            'target_revenue': 'Target'
        }

        df_act['activation_date'] = pd.to_datetime(df_act['activation_date'])
        df_act = df_act.groupby(
                ['activation_date']
            )['guaranteed_revenue'].sum().reset_index()
        df_act.rename(columns=columns_rename, inplace=True)
        df_act['Bulan'] = df_act['Tanggal'].dt.month
        df_act.set_index('Tanggal', inplace=True)
        df_act = df_act.asfreq('D').reset_index()
        df_act['Revenue'] = df_act.groupby(['Bulan'])['Revenue'].cumsum()

        df_tar.rename(columns=columns_rename, inplace=True)
        df_tar['Tanggal'] = pd.to_datetime(df_tar['Tanggal'])
        df_tar['Bulan'] = df_tar['Tanggal'].dt.month
        df_tar = df_tar.groupby(
                ['Bulan']
            )['Target'].sum().reset_index()
        df_tar['Target'] = df_tar['Target'].replace(0, np.nan)

        df = pd.merge(df_act, df_tar, how='left', on='Bulan')
        df['Target Harian'] = df['Target'] / df['Tanggal'].dt.daysinmonth
        df['Target Harian'] = df['Target Harian'].astype(float)
        df['Target Harian'] = df.groupby(
                'Bulan'
            )['Target Harian'].cumsum()

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        fig = px.line(
            df, x='Tanggal', y='Target Harian', color_discrete_sequence=['red'],
            hover_data={
                'Tanggal': False
            }
        )
        fig.update_traces(
            legendgrouptitle_text='Target',
            legendgroup='target',
            hovertemplate='Rp%{y:,.0f}'
        )
        main_fig = px.area(
            df, x='Tanggal', y='Revenue', 
            height=500, color_discrete_sequence=['#7AB2D3'],
            hover_data={
                'Tanggal': False
            }
        )
        main_fig.update_traces(
            legendgrouptitle_text='Achieve',
            legendgroup='achieve',
            hovertemplate='Rp%{y:,.0f}'
        )
        main_fig.add_traces(fig.data)
        main_fig.update_layout(
            yaxis_tickprefix='Rp',
            yaxis_tickformat=',.1d',
            hovermode='x unified', dragmode='pan'
        )
        main_fig.update_legends(
            orientation='h', yanchor='bottom', xanchor='left', y=1
        )
        main_fig.update_xaxes(showline=True, title=TITLE_FONT_COLOR)
        main_fig.update_yaxes(minallowed=0, title=TITLE_FONT_COLOR)
        for i in line:
            main_fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(main_fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def growth_barchart(data: pd.DataFrame):
        df = data.copy()

        columns_rename = {
            'activation_date': 'Tanggal',
            'target_date': 'Tanggal',
            'order_type': 'Tipe Achieve',
            'count': 'Achieve'
        }
        order_type_rename = {
            'Change Postpaid Plan': 'CPP',
            'Migration': 'GA',
            'New Registration': 'GA',
        }

        df['order_type'] = df['order_type'].replace(order_type_rename)
        df['activation_date'] = pd.to_datetime(df['activation_date'])
        df_order = df.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['order_type'].value_counts().reset_index()
        df_rev = df.groupby(
                pd.Grouper(key='activation_date', freq='ME')
            )['guaranteed_revenue'].sum().reset_index()
        df_rev['order_type'] = 'Revenue'
        
        df = df_order.copy()
        for value in df_rev.values:
            df.loc[len(df)] = value[[0, 2, 1]]

        df['activation_date'] = df['activation_date'].map(
            lambda dt: dt.replace(day=1)
        )
        df.rename(columns=columns_rename, inplace=True)
        df.sort_values(['Tanggal', 'Tipe Achieve'], inplace=True)
        df['Growth Rate (%)'] = df['Achieve'].pct_change(periods=3)
        df['Growth Rate (%)'] = df['Growth Rate (%)'] * 100
        df.dropna(inplace=True)
        df.reset_index(inplace=True)

        fig = px.bar(
            df, x='Tanggal', y='Growth Rate (%)', barmode='group',
            color='Tipe Achieve', height=500,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(hovertemplate='%{y:.1f}% | %{x}')
        fig.update_layout(
            barcornerradius='20%',
            dragmode='pan'
        )
        fig.update_xaxes(
            dtick='M1', tickformat='%b %Y', title=TITLE_FONT_COLOR
        )
        fig.for_each_yaxis(lambda a: a.update(ticksuffix='%'))
        fig.update_yaxes(title=TITLE_FONT_COLOR)
        fig.add_hline(0, line_color='#3C3D37')

        st.write(fig)

    @st.cache_data(ttl=300, show_spinner=False)
    def ordertype_heatmap(data: pd.DataFrame):
        df = data.copy()

        columns_rename = {
            'activation_date': 'Tanggal',
            'target_date': 'Tanggal',
            'order_type': 'Tipe Order',
            'count': 'Jumlah Aktivasi'
        }

        df['activation_date'] = pd.to_datetime(df['activation_date'])
        df = df.groupby(
                pd.Grouper(key='activation_date', freq='D')
            )['order_type'].value_counts().reset_index()
        df.rename(columns=columns_rename, inplace=True)

        minimum = df['Tanggal'].min()
        maximum = df['Tanggal'].max()
        line = [f'2024-{i+1}-1' for i in range(minimum.month, maximum.month)]

        df = df.pivot(
                index='Tipe Order', columns='Tanggal'
            )['Jumlah Aktivasi'].fillna(0)
        
        fig = px.imshow(df, x=df.columns, y=df.index, height=500)
        fig.update_traces(hovertemplate='Aktivasi : %{z} | %{x}')
        fig.update_layout(
            barcornerradius='20%',
            dragmode='pan'
        )
        fig.update_xaxes(title=TITLE_FONT_COLOR)
        fig.update_yaxes(
            fixedrange=True, title=TITLE_FONT_COLOR,
            tickangle=-90, showgrid=False
        )
        for i in line:
            fig.add_vline(i, line_dash='dot', line_color='#3C3D37')

        st.write(fig)