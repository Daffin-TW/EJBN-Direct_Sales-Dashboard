from mysql.connector.abstracts import MySQLCursorAbstract as db_cur
from streamlit import session_state as ss
from datetime import datetime
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
    cursor.close()

    return df.set_index(cursor.description[0][0])

def fetch_data(table: str):
    match table:
        case 'Channel':
            sql = 'SELECT `code` AS `Code`, area AS "Area" FROM Channel;'
            return sql_to_dataframe(sql)
        
        case 'Person':
            sql = 'SELECT nik AS "NIK", `name` AS "NAME";'

        case 'Rce':
            sql = """
                SELECT id AS "ID", nik AS "NIK", `name` AS "Name", channel_code
                    AS "Channel", employment_date AS "Employment Date",
                    end_date AS "End Date" FROM Rce AS R INNER JOIN Person AS P
                    ON R.rce_nik = P.nik;"""
            return sql_to_dataframe(sql)
        
        case 'Agent Editing':
            sql = """
                SELECT A.id AS "ID", CONCAT(R.id, ": ", PR.name) AS "RCE",
                    PA.nik AS "NIK", PA.`name` AS "Name", A.employment_date
                    AS "Employment Date", A.end_date AS "End Date" 
                    FROM Person AS PR INNER JOIN Rce AS R
                    ON PR.nik = R.rce_nik INNER JOIN Agent AS A
                    ON R.id = A.rce_id INNER JOIN Person AS PA
                    ON A.agent_nik = PA.nik;"""
            return sql_to_dataframe(sql)
        
        case 'Agent':
            sql = """
                SELECT A.id AS "ID", R.id AS "RCE ID", PA.nik AS "NIK",
                    PA.`name` AS "Name", PR.`name` AS "RCE", A.employment_date
                    AS "Employment Date", A.end_date AS "End Date" 
                    FROM Person AS PR INNER JOIN Rce AS R
                    ON PR.nik = R.rce_nik INNER JOIN Agent AS A
                    ON R.id = A.rce_id INNER JOIN Person AS PA
                    ON A.agent_nik = PA.nik;"""
            return sql_to_dataframe(sql)
        
        case _:
            raise KeyError(f'{table} tidak ditemukan di database')
        
def fetch_data_primary(table: str):
    match table:
        case 'Channel':
            sql = 'SELECT `code` AS `Code` FROM Channel;'
            return sql_to_dataframe(sql).index
        
        case 'Rce':
            sql = """SELECT DISTINCT `name` AS "Name" FROM Rce AS R
                        INNER JOIN Person AS P ON R.rce_nik = P.nik;"""
            return sql_to_dataframe(sql)
        
        case 'Rce Id Name':
            sql = """SELECT CONCAT(R.id, ": ", P.name) AS "RCE" FROM Rce AS R
                        INNER JOIN Person AS P ON R.rce_nik = P.nik;"""
            return sql_to_dataframe(sql).index
        
        case _:
            raise KeyError(f'{table} tidak ditemukan di database')

def is_editing():
    ss.done_editing = False

def edit_channel():
    df_original = fetch_data('Channel').reset_index()
    
    df_modified: pd.DataFrame = st.data_editor(
        df_original, num_rows='dynamic',
        use_container_width=True, on_change=is_editing,
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
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both']

    changes['Area'] = changes['Area'].fillna('NULL')
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

    sql = []

    if insert_update:
        sql.append(f"""
            INSERT INTO `Channel` VALUES {insert_update} AS new
                ON DUPLICATE KEY UPDATE area = new.area;
        """)

    if delete:
        sql.append(f"""
            DELETE FROM `Channel` WHERE `Code` IN ({delete});
        """)

    return sql

def edit_rce():
    df_original = fetch_data('Rce').reset_index()
    df_original['ID'] = df_original['ID'].astype(str)
    
    df_modified: pd.DataFrame = st.data_editor(
        df_original, num_rows='dynamic',
        use_container_width=True, on_change=is_editing,
        column_config={
            'ID': st.column_config.TextColumn(disabled=True, default='auto'),
            'NIK': st.column_config.TextColumn(
                default=None, max_chars=12,
                required=True, validate='[A-Za-z0-9]+'),
            'Name': st.column_config.TextColumn(
                required=True, default='Nama RCE'
            ),
            'Channel': st.column_config.SelectboxColumn(
                options=fetch_data_primary('Channel'), required=True
            ),
            'Employment Date': st.column_config.DateColumn(
                required=True, default=datetime.now().date(), format='DD/MM/YYYY'
            ),
            'End Date': st.column_config.DateColumn(
                format='DD/MM/YYYY'
            )
        }
    )

    df_modified['ID'] = df_modified['ID'].replace('auto', None)
    duplicates_check = df_modified[df_modified['NIK'].duplicated(keep=False)]

    if not all(duplicates_check.duplicated(['NIK', 'Name'], keep=False)):
        ss.invalid_edit = True
        st.error('NIK dan Nama harus konsisten', icon='❗')
    else:
        ss.invalid_edit = False
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both']

    changes = changes.dropna(subset=['NIK'])
    changes.fillna({
        'ID': 'NULL', 'Employment Date': 'NULL', 'End Date': 'NULL'
    }, inplace=True)
    changes.rename(columns={'_merge': 'Difference'}, inplace=True)
    changes['Update'] = (
        (changes.duplicated(subset=['ID', 'NIK'], keep=False)) &
        (changes['Difference'] == 'right_only')
    )
    changes['Employment Date'] = changes['Employment Date'].astype(str)
    changes['End Date'] = changes['End Date'].astype(str)

    insert_update_person = changes[
        changes['Difference'] == 'left_only'
    ][[
        'NIK', 'Name'
    ]].values
    insert_update_person = tuple(map(tuple, insert_update_person))
    insert_update_person = ', '.join([str(i) for i in insert_update_person])
    insert_update_person = insert_update_person.replace("'NULL'", 'NULL')

    insert_update_rce = changes[
        changes['Difference'] == 'left_only'
    ][[
        'ID', 'NIK', 'Channel',
        'Employment Date', 'End Date'
    ]].values
    insert_update_rce = tuple(map(tuple, insert_update_rce))
    insert_update_rce = ', '.join([str(i) for i in insert_update_rce])
    insert_update_rce = insert_update_rce.replace("'NULL'", 'NULL')

    delete_rce = changes[
        (changes['Difference'] == 'right_only') &
        (changes['Update'] == False).values
    ]['ID'].values
    delete_rce = ', '.join([f"'{i}'" for i in delete_rce])

    sql = []

    if insert_update_person:
        sql.append(f"""
            INSERT INTO Person VALUES {insert_update_person} AS new
                ON DUPLICATE KEY UPDATE
                `name` = new.`name`;
        """)
        
    if insert_update_rce:
        sql.append(f"""
            INSERT INTO Rce VALUES {insert_update_rce} AS new
                ON DUPLICATE KEY UPDATE
                rce_nik = new.rce_nik,
                channel_code = new.channel_code,
                employment_date = new.employment_date,
                end_date = new.end_date;
        """)

    if delete_rce:
        sql.append(f"""
            DELETE FROM Rce WHERE `id` IN ({delete_rce});
        """)

    return sql

def edit_agent():
    df_original = fetch_data('Agent Editing').reset_index()
    df_original['ID'] = df_original['ID'].astype(str)
    
    df_modified: pd.DataFrame = st.data_editor(
        df_original, num_rows='dynamic',
        use_container_width=True, on_change=is_editing,
        column_config={
            'ID': st.column_config.TextColumn(disabled=True, default='auto'),
            'RCE': st.column_config.SelectboxColumn(
                options=fetch_data_primary('Rce Id Name'), required=True
            ),
            'NIK': st.column_config.TextColumn(
                default=None, max_chars=12,
                required=True, validate='[A-Za-z0-9]+'),
            'Name': st.column_config.TextColumn(
                required=True, default='Nama Agent'
            ),
            'Employment Date': st.column_config.DateColumn(
                required=True, default=datetime.now().date(), format='DD/MM/YYYY'
            ),
            'End Date': st.column_config.DateColumn(
                format='DD/MM/YYYY'
            )
        }
    )

    df_modified['ID'] = df_modified['ID'].replace('auto', None)
    duplicates_check = df_modified[df_modified['NIK'].duplicated(keep=False)]

    if not all(duplicates_check.duplicated(['NIK', 'Name'], keep=False)):
        ss.invalid_edit = True
        st.error('NIK dan Nama harus konsisten', icon='❗')
    else:
        ss.invalid_edit = False
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both']

    changes = changes.dropna(subset=['NIK'])
    changes.fillna({
        'ID': 'NULL', 'Employment Date': 'NULL', 'End Date': 'NULL'
    }, inplace=True)
    changes.rename(columns={'_merge': 'Difference'}, inplace=True)
    changes['Update'] = (
        (changes.duplicated(subset=['ID', 'NIK'], keep=False)) &
        (changes['Difference'] == 'right_only')
    )
    changes['Employment Date'] = changes['Employment Date'].astype(str)
    changes['End Date'] = changes['End Date'].astype(str)
    changes['RCE'] = changes['RCE'].str.split(':').str[0]

    insert_update_person = changes[
        changes['Difference'] == 'left_only'
    ][[
        'NIK', 'Name'
    ]].values
    insert_update_person = tuple(map(tuple, insert_update_person))
    insert_update_person = ', '.join([str(i) for i in insert_update_person])
    insert_update_person = insert_update_person.replace("'NULL'", 'NULL')

    insert_update_agent = changes[
        changes['Difference'] == 'left_only'
    ][[
        'ID', 'NIK', 'RCE',
        'Employment Date', 'End Date'
    ]].values
    insert_update_agent = tuple(map(tuple, insert_update_agent))
    insert_update_agent = ', '.join([str(i) for i in insert_update_agent])
    insert_update_agent = insert_update_agent.replace("'NULL'", 'NULL')

    delete_agent = changes[
        (changes['Difference'] == 'right_only') &
        (changes['Update'] == False).values
    ]['ID'].values
    delete_agent = ', '.join([f"'{i}'" for i in delete_agent])

    sql = []

    if insert_update_person:
        sql.append(f"""
            INSERT INTO Person VALUES {insert_update_person} AS new
                ON DUPLICATE KEY UPDATE
                `name` = new.`name`;
        """)
        
    if insert_update_agent:
        sql.append(f"""
            INSERT INTO Agent VALUES {insert_update_agent} AS new
                ON DUPLICATE KEY UPDATE
                agent_nik = new.agent_nik,
                rce_id = new.rce_id,
                employment_date = new.employment_date,
                end_date = new.end_date;
        """)

    if delete_agent:
        sql.append(f"""
            DELETE FROM Agent WHERE `id` IN ({delete_agent});
        """)

    return sql

def execute_sql_query(sql: list):
    check_connection()

    try:
        cursor: db_cur = ss.db_connection.cursor()

        for query in sql:
            cursor.execute(query)
            ss.db_connection.commit()

        cursor.close()
        st.cache_data.clear()

        return (True, 'Success')
    
    except Exception as e:
        cursor.close()
        st.cache_data.clear()
        check_connection()

        return (False, e)