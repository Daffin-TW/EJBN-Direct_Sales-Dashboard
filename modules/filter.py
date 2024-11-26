from .database import fetch_data_primary
from datetime import datetime, timedelta
import streamlit as st


def filter_name():
    st.markdown('**Nama**')
    return st.text_input(
        'filter_name',
        placeholder='Filter berdasarkan nama',
        label_visibility='collapsed'
    )

def filter_channel():
    st.markdown('**Channel**')
    options = fetch_data_primary('Channel').index
    selection = st.multiselect(
        'filter_channel', options=options,
        placeholder='Filter berdasarkan Channel',
        label_visibility='collapsed'
    )
    return str(tuple(selection)).replace(',)', ')').replace('()', '')

def filter_rce():
    st.markdown('**RCE**')
    options = fetch_data_primary('Rce Id Name').index
    selection = st.multiselect(
        'filter_rce', options=options,
        placeholder='Filter berdasarkan RCE',
        label_visibility='collapsed'
    )
    return str(tuple(selection)).replace(',)', ')').replace('()', '')

def filter_date():
    st.markdown('**Tanggal**')
    return st.date_input(
        'filter_date_input', label_visibility='collapsed',
        value=(datetime.now() - timedelta(days=184), datetime.now()),
        format='DD/MM/YYYY'
    )

def filter_month():
    month = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May',
        6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October',
        11: 'November', 12: 'December'
    }

    st.markdown('**Bulan**')
    return st.select_slider(
        'filter_month_slider', options=month, value=(1, 12),
        format_func=lambda x: month.get(x), label_visibility='collapsed'
    )

def filter_active():
    st.markdown('**Status**')
    status_opt = ('All', 'Active', 'Inactive')
    return st.radio(
        'filter_status', options=status_opt, label_visibility='collapsed'
    )

def filter_peragent():
    # st.markdown('**Filter Per Agent**')
    return st.checkbox(
        '**Filter Rata-rata Per Agent**', key='filter_peragent',
    )

def filter_edit(table: str):
    sql = []

    match table:
        case 'Channel':
            st.warning('Tidak ada filter khusus untuk tabel Channel...')

        case 'RCE':
            name = filter_name()
            channel = filter_channel()
            active = filter_active()
            
            if name:
                sql.append(f"P.`name` LIKE '%{name}%'")
            if channel:
                sql.append(f'R.channel_code IN {channel}')
            if active == 'Active':
                sql.append(f"""(
                    (R.employment_date <= CURDATE() OR
                        R.employment_date IS NULL
                    ) AND
                    (R.end_date >= CURDATE() OR R.end_date IS NULL)
                )""")
            elif active == 'Inactive':
                sql.append(f"""(
                    R.employment_date >= CURDATE() OR
                    R.end_date <= CURDATE()
                )""")

        case 'Agent':
            name = filter_name()
            rce = filter_rce()
            channel = filter_channel()
            active = filter_active()
            
            if name:
                sql.append(f"PA.`name` LIKE '%{name}%'")
            if rce:
                sql.append(f'A.rce_id IN {rce}')
            if channel:
                sql.append(f'R.channel_code IN {channel}')
            if active == 'Active':
                sql.append(f"""(
                    (A.employment_date <= CURDATE() OR A.end_date IS NULL) AND
                    (A.end_date >= CURDATE() OR A.end_date IS NULL)
                )""")
            elif active == 'Inactive':
                sql.append(f"""(
                    A.employment_date >= CURDATE() OR
                    A.end_date <= CURDATE()
                )""")

        case 'RCE Target':
            name = filter_name()
            rce = filter_rce()
            channel = filter_channel()
            month = filter_month()
            active = filter_active()
            
            if name:
                sql.append(f"P.`name` LIKE '%{name}%'")
            if rce:
                sql.append(f'RT.rce_id IN {rce}')
            if channel:
                sql.append(f'R.channel_code IN {channel}')
            if month:
                sql.append(
                    f'(MONTH(RT.target_date) BETWEEN {month[0]} AND {month[1]})'
                )
            if active == 'Active':
                sql.append(f"""(
                    (R.employment_date <= CURDATE() OR
                        R.employment_date IS NULL
                    ) AND (R.end_date >= CURDATE() OR R.end_date IS NULL)
                )""")
            elif active == 'Inactive':
                sql.append(f"""(
                    R.employment_date >= CURDATE() OR
                    R.end_date <= CURDATE()
                )""")

        case 'Agent Target':
            name = filter_name()
            rce = filter_rce()
            channel = filter_channel()
            month = filter_month()
            active = filter_active()
            
            if name:
                sql.append(f"PA.`name` LIKE '%{name}%'")
            if rce:
                sql.append(f'RT.rce_id IN {rce}')
            if channel:
                sql.append(f'R.channel_code IN {channel}')
            if month:
                sql.append(
                    f'(MONTH(RT.target_date) BETWEEN {month[0]} AND {month[1]})'
                )
            if active == 'Active':
                sql.append(f"""(
                    (A.employment_date <= CURDATE() OR A.end_date IS NULL) AND
                    (A.end_date >= CURDATE() OR A.end_date IS NULL)
                )""")
            elif active == 'Inactive':
                sql.append(f"""(
                    A.employment_date >= CURDATE() OR
                    A.end_date <= CURDATE()
                )""")

        case 'Daily Activation':
            name = filter_name()
            rce = filter_rce()
            channel = filter_channel()
            date = filter_date()
            
            if name:
                sql.append(f"P.`name` LIKE '%{name}%'")
            if rce:
                sql.append(f'R.id IN {rce}')
            if channel:
                sql.append(f'R.channel_code IN {channel}')
            if len(date) == 1:
                sql.append(f"DA.activation_date >= '{date[0]}'")
            elif len(date) == 2:
                sql.append(f"""(
                DA.activation_date BETWEEN '{date[0]}' AND '{date[1]}'
            )""")
            
        case _:
            st.error(f'Tidak ada tabel dengan nama {table}')
    
    if sql:
        query = 'WHERE ' + ' AND '.join(sql)
    else:
        query = ''

    return query

def filter_dashboard(table: str):
    query = dict()
    
    match table:
        case 'General':
            sql = dict()
            sql['act'], sql['tar'] = list(), list()

            rce = filter_rce()
            channel = filter_channel()
            date = filter_date()

            if rce:
                sql['act'].append(f'R.id IN {rce}')
                sql['tar'].append(f'R.id IN {rce}')
            if channel:
                sql['act'].append(f'R.channel_code IN {channel}')
                sql['tar'].append(f'R.channel_code IN {channel}')
            if len(date) == 1:
                sql['act'].append(f"DA.activation_date >= '{date[0]}'")
                sql['tar'].append(f"""
                    MONTH(RT.target_date) >= MONTH('{date[0]}')
                """)
            elif len(date) == 2:
                sql['act'].append(f"""(
                    DA.activation_date BETWEEN '{date[0]}' AND '{date[1]}'
                )""")
                sql['tar'].append(f"""
                    MONTH(RT.target_date) BETWEEN MONTH('{date[0]}') AND
                    MONTH('{date[1]}')
                """)

        case 'RCE Comparison':
            sql = dict()
            sql['act'] = list()

            rce = filter_rce()
            channel = filter_channel()
            date = filter_date()

            if rce:
                sql['act'].append(f'R.id IN {rce}')
            if channel:
                sql['act'].append(f'R.channel_code IN {channel}')
            if len(date) == 1:
                sql['act'].append(f"DA.activation_date >= '{date[0]}'")
            elif len(date) == 2:
                sql['act'].append(f"""(
                    DA.activation_date BETWEEN '{date[0]}' AND '{date[1]}'
                )""")
            
        case _:
            st.error(f'Tidak ada tabel dengan nama {table}')

    for key, value in sql.items():
        if value:
            query[key] = 'WHERE ' + ' AND '.join(value)
        else:
            query[key] = ''

    return query