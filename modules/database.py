from mysql.connector.abstracts import MySQLCursorAbstract as db_cur
from streamlit import session_state as ss
import mysql.connector
import streamlit as st
import pandas as pd


st.cache_resource(show_spinner=False, ttl=300)
def connect_db():
    db_connection = mysql.connector.connect(
        host=st.secrets.db_credentials.host,
        user=st.secrets.db_credentials.username,
        password=st.secrets.db_credentials.password,
        database=st.secrets.db_credentials.database
    )

    return db_connection

def check_connection():
    if not ss.db_connection.is_connected():
        st.toast('Database tidak terhubung. Mencoba untuk menghubung kembali',
                 icon='⛔')
        st.cache_resource.clear()
        ss.db_connection = connect_db()

@st.cache_data(show_spinner=False, ttl=300)
def sql_to_dataframe(sql: str):
    check_connection()
    cursor: db_cur = ss.db_connection.cursor()
    cursor.execute(sql)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = [i[0] for i in cursor.description]
    return df.set_index(cursor.description[0][0])

def fetch_channel():
    sql = 'SELECT `code` AS `Code`, area AS "Area" FROM Channel;'
    return sql_to_dataframe(sql)

def is_editing():
    ss.done_editing = False

def update_channel():
    df_original = fetch_channel().reset_index()
    
    df_modified = st.data_editor(
        df_original.copy(), num_rows='dynamic', use_container_width=True,
        on_change=is_editing,
        column_config={
            'Code': st.column_config.TextColumn(
                default='DS00', max_chars=5,
                required=True, validate='[A-Za-z]+[0-9]+'
            )
        }
    )

    if any(df_modified['Code'].duplicated()):
        ss.invalid_edit = True
        st.error('Kode tidak boleh duplikat', icon='❗')
    else:
        ss.invalid_edit = False
    df_modified['Code'] = df_modified['Code'].drop_duplicates()
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both']

    changes = changes.dropna(subset=['Code'])
    changes['Area'] = changes['Area'].fillna('Null')
    changes.rename(columns={'_merge': 'Difference'}, inplace=True)
    changes.drop_duplicates(subset=['Code', 'Difference'], inplace=True)
    changes['Update'] = changes.duplicated(subset=['Code'], keep=False)
    
    insert_update = changes[
        changes['Difference'] == 'left_only'
    ][['Code', 'Area']].values
    insert_update = tuple(map(tuple, insert_update))
    insert_update = ', '.join([str(i) for i in insert_update])

    delete = changes[
        (changes['Difference'] == 'right_only') &
        (changes['Update'] == False).values
    ]['Code'].values
    delete = ', '.join([f"'{i}'" for i in delete])

    sql = ''
    if insert_update:
        sql += f"""
            INSERT INTO Channel VALUES {insert_update} AS new
                ON DUPLICATE KEY UPDATE area = new.area;
        """

    if delete:
        sql += f"""
            DELETE FROM Channel WHERE `Code` IN ({delete});
        """

    return sql

def execute_sql_query(sql: str):
    check_connection()

    try:
        cursor: db_cur = ss.db_connection.cursor()
        cursor.execute(sql)
        ss.db_connection.commit()
        st.cache_data.clear()
        return (True, 'Success')
    except Exception as e:
        st.cache_data.clear()
        return (False, e)