from mysql.connector.abstracts import MySQLCursorAbstract as db_cur
from streamlit import session_state as ss
from warnings import filterwarnings
from datetime import datetime
import mysql.connector
import streamlit as st
import pandas as pd


filterwarnings(
    "ignore",
    category=UserWarning,
    message='.*pandas only supports SQLAlchemy connectable.*'
)
pd.set_option('future.no_silent_downcasting', True)

st.cache_resource(show_spinner=False, ttl=300)
def connect_db():
    try:
        with st.spinner('Menghubungi database, mohon ditunggu...'):
            db_connection = mysql.connector.connect(
                host=st.secrets.db_credentials.host,
                user=st.secrets.db_credentials.username,
                password=st.secrets.db_credentials.password,
                database=st.secrets.db_credentials.database,
                port=st.secrets.db_credentials.port,
                charset=st.secrets.db_credentials.charset
            )

            return db_connection
    
    except:
        st.toast("""
            Mengalami kendala? Hubungi [Daffin_TW](https://wa.me/6282332232896)
            untuk bertanya atau perbaikan.
        """, icon='🚨')
        st.error('⛔ Database tidak bisa dihubungi.')
        st.stop()

def check_connection():
    if not ss.db_connection.is_connected():
        st.toast(
            'Database tidak terhubung. Mencoba untuk menghubung kembali.',
            icon='⛔'
        )
        st.cache_resource.clear()
        ss.db_connection = connect_db()

@st.cache_data(show_spinner=False, ttl=300)
def sql_to_dataframe(sql: str):
    with st.spinner('Sedang memuat data, mohon ditunggu...'):
        ss.db_is_loading = True

        check_connection()
        df = pd.read_sql(sql, ss.db_connection)

    ss.db_is_loading = False
    return df.set_index(df.columns[0])

def fetch_data(table: str, filter_query: str = ''):
    match table:
        case 'Channel':
            sql = 'SELECT `code` AS `Code`, area AS "Area" FROM Channel'

        case 'Person':
            sql = 'SELECT nik AS "NIK", `name` AS "NAME"'

        case 'Rce':
            sql = f"""
                SELECT id AS "ID", nik AS "NIK", `name` AS "Name", channel_code
                    AS "Channel", employment_date AS "Employment Date",
                    end_date AS "End Date"
                FROM Rce AS R INNER JOIN Person AS P
                    ON R.rce_nik = P.nik
                {filter_query}
            """
        
        case 'Agent Editing':
            sql = f"""
                SELECT A.id AS "ID", CONCAT(R.id, ': ', PR.name) AS "RCE",
                    PA.nik AS "NIK", PA.`name` AS "Name", A.employment_date
                    AS "Employment Date", A.end_date AS "End Date" 
                FROM Person AS PR INNER JOIN Rce AS R
                    ON PR.nik = R.rce_nik INNER JOIN Agent AS A
                    ON R.id = A.rce_id INNER JOIN Person AS PA
                    ON A.agent_nik = PA.nik
                {filter_query}
                """
        
        case 'Agent':
            sql = """
                SELECT A.id AS "ID", PA.nik AS "NIK",
                    PA.`name` AS "Name", PR.`name` AS "RCE", A.employment_date
                    AS "Employment Date", A.end_date AS "End Date" 
                FROM Person AS PR INNER JOIN Rce AS R
                    ON PR.nik = R.rce_nik INNER JOIN Agent AS A
                    ON R.id = A.rce_id INNER JOIN Person AS PA
                    ON A.agent_nik = PA.nik"""
        
        case 'RCE Target':
            sql = """
                SELECT
                    RT.id AS "ID", YEAR(RT.target_date) AS "Tahun",
                    MONTHNAME(RT.target_date) AS "Bulan", P.`name` AS "RCE",
                    RT.target_ga AS "Target GA", RT.target_cpp AS
                    "Target CPP", RT.target_revenue AS "Target Revenue"
                FROM RceTarget AS RT
                    INNER JOIN Rce AS R ON RT.rce_id = R.id
                    INNER JOIN Person AS P ON R.rce_nik = P.nik
                ORDER BY
                    RT.id
            """

        case 'RCE Target Editing':
            sql = f"""
                SELECT
                    RT.id AS "ID", YEAR(RT.target_date) AS "Tahun",
                    MONTHNAME(RT.target_date) AS "Bulan",
                    CONCAT(R.id, ': ', P.name) AS "RCE", RT.target_ga AS
                    "Target GA", RT.target_cpp AS "Target CPP",
                    RT.target_revenue AS "Target Revenue"
                FROM RceTarget AS RT
                    INNER JOIN Rce AS R ON RT.rce_id = R.id
                    INNER JOIN Person AS P ON R.rce_nik = P.nik
                {filter_query}
                ORDER BY
                    RT.id
            """

        case 'Agent Target':
            sql = f"""
                SELECT
                    `AT`.id AS "ID",
                    YEAR(RT.target_date) AS "Tahun",
                    MONTHNAME(RT.target_date) AS "Bulan",
                    PA.`name` AS "Agent",
                    `AT`.target_ga AS "Target GA",
                    `AT`.target_cpp AS "Target CPP"
                FROM AgentTarget AS `AT`
                    INNER JOIN RceTarget AS RT ON `AT`.rce_target_id = RT.id
                    INNER JOIN Agent AS A ON `AT`.agent_id = A.id
                    INNER JOIN Person AS PA ON A.agent_nik = PA.nik
                {filter_query}
                ORDER BY
                    `AT`.id
            """

        case 'Agent Target Editing':
            sql = f"""
                SELECT
                    `AT`.id AS "ID",
                    CONCAT(RT.id, ': ', PR.`name`, ' - ',
                        MONTHNAME(RT.target_date), ', ', YEAR(RT.target_date)
                    ) AS "RCE Target ID",
                    CONCAT(
                        `AT`.agent_id, ': ', PA.nik, ' - ', R.channel_code,
                        ' - ', PA.`name`
                    ) AS "Agent",
                    `AT`.target_ga AS "Target GA",
                    `AT`.target_cpp AS "Target CPP"
                FROM AgentTarget AS `AT`
                    INNER JOIN RceTarget AS RT ON `AT`.rce_target_id = RT.id
                    INNER JOIN Rce as R ON RT.rce_id = R.id
                    INNER JOIN Person PR ON R.rce_nik = PR.nik
                    INNER JOIN Agent AS A ON `AT`.agent_id = A.id
                    INNER JOIN Person AS PA ON A.agent_nik = PA.nik
                {filter_query}
                ORDER BY
                    `AT`.id
            """

        case 'Activation':
            sql = f"""
                SELECT
                    DA.id AS "ID", DA.activation_date AS "Date", DA.product AS
                    "Product", DA.tenure AS "Tenure", P.`name` AS "Agent",
                    DA.order_type AS "Order Type",
                    DA.tactical_regular AS "Tactical Regular",
                    DA.guaranteed_revenue AS "Guaranteed Revenue"
                FROM DailyActivation AS DA
                    INNER JOIN Agent AS A ON DA.agent_id = A.id
                    INNER JOIN Person AS P ON A.agent_nik = P.nik
                {filter_query}
                ORDER BY
                    DA.activation_date, DA.id
            """

        case 'Activation Editing':
            sql = f"""
                SELECT
                    DA.id AS "ID", DA.activation_date AS "Date", DA.product AS
                    "Product", DA.tenure AS "Tenure", CONCAT(
                        A.id, ': ', P.nik, ' - ', R.channel_code, ' - ', P.`name`
                    ) AS "Agent", DA.order_type AS "Order Type",
                    DA.tactical_regular AS "Tactical Regular",
                    DA.guaranteed_revenue AS "Guaranteed Revenue"
                FROM DailyActivation AS DA
                    INNER JOIN Agent AS A ON DA.agent_id = A.id
                    INNER JOIN Person AS P ON A.agent_nik = P.nik
                    INNER JOIN Rce AS R ON A.rce_id = R.id
                {filter_query}
                ORDER BY
                    DA.activation_date, DA.id
            """

        case _:
            raise KeyError(f'{table} tidak ditemukan di database')
    
    if not ss.get('db_is_loading', False):
        return sql_to_dataframe(sql + ';')
        
def fetch_data_primary(table: str):
    match table:
        case 'Channel':
            sql = 'SELECT `code` AS `Code` FROM Channel;'
            if not ss.get('db_is_loading', False):
                return sql_to_dataframe(sql).index
        
        case 'Rce':
            sql = """SELECT DISTINCT `name` AS "Name" FROM Rce AS R
                        INNER JOIN Person AS P ON R.rce_nik = P.nik;"""
            if not ss.get('db_is_loading', False):
                return sql_to_dataframe(sql)
        
        case 'Rce Id Name':
            sql = """SELECT CONCAT(R.id, ': ', P.`name`) AS "RCE" FROM Rce AS R
                        INNER JOIN Person AS P ON R.rce_nik = P.nik;"""
            if not ss.get('db_is_loading', False):
                return sql_to_dataframe(sql).index
        
        case 'Agent Id Name':
            sql = """SELECT CONCAT(
                            A.id, ': ', P.nik, ' - ', R.channel_code, ' - ', P.`name`
                        ) AS "Agent" FROM Agent AS A
                        INNER JOIN Rce AS R ON A.rce_id = R.id
                        INNER JOIN Person AS P ON A.agent_nik = P.nik
                        ORDER BY A.id;"""
            if not ss.get('db_is_loading', False):
                return sql_to_dataframe(sql).index
        
        case 'Rce Target Id Name':
            sql = """
                SELECT
                    CONCAT(
                        RT.id, ': ', P.`name`, ' - ', MONTHNAME(RT.target_date),
                        ', ', YEAR(RT.target_date)
                    ) AS "RCE Target ID"
                FROM RceTarget AS RT
                    INNER JOIN Rce as R ON RT.rce_id = R.id
                    INNER JOIN Person P ON R.rce_nik = P.nik
                ORDER BY
                    RT.id;"""
            if not ss.get('db_is_loading', False):
                return sql_to_dataframe(sql).index
        
        case _:
            raise KeyError(f'{table} tidak ditemukan di database')

def is_editing():
    ss.done_editing = False

def edit_channel(filter_query: str = ''):
    df_original = fetch_data('Channel', filter_query).reset_index()
    
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
    ).loc[lambda x : x['_merge'] != 'both'].copy()

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
        (changes['Update'] == False)
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

def edit_rce(filter_query: str = ''):
    df_original = fetch_data('Rce', filter_query).reset_index()
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
                default=datetime.now().date(), format='DD/MM/YYYY'
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
    ).loc[lambda x : x['_merge'] != 'both'].copy()

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
        (changes['Update'] == False)
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

def edit_agent(filter_query: str = ''):
    df_original = fetch_data('Agent Editing', filter_query).reset_index()
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
                default=datetime.now().date(), format='DD/MM/YYYY'
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
    ).loc[lambda x : x['_merge'] != 'both'].copy()

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
        (changes['Update'] == False)
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

def edit_rce_target(filter_query: str = ''):
    df_original = fetch_data('RCE Target Editing', filter_query).reset_index()
    df_original['ID'] = df_original['ID'].astype(str)
    
    month = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May',
        6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October',
        11: 'November', 12: 'December'
    }
    month_number = {j: i for i, j in month.items()}

    df_modified: pd.DataFrame = st.data_editor(
        df_original, num_rows='dynamic',
        use_container_width=True, on_change=is_editing,
        column_config={
            'ID': st.column_config.TextColumn(disabled=True, default='auto'),
            'RCE': st.column_config.SelectboxColumn(
                options=fetch_data_primary('Rce Id Name'), required=True,
            ),
            'Tahun': st.column_config.NumberColumn(
                required=True, default=datetime.now().year,
                min_value=2000, max_value=9999, step=1, format='%i'
            ),
            'Bulan': st.column_config.SelectboxColumn(
                required=True, options=month.values(),
                default=month[datetime.now().month]
            ),
            'Target GA': st.column_config.NumberColumn(),
            'Target CPP': st.column_config.NumberColumn(),
            'Target Revenue': st.column_config.NumberColumn()
        }
    )

    df_modified['ID'] = df_modified['ID'].replace('auto', None)

    if any(df_modified.duplicated(['Tahun', 'Bulan', 'RCE'], keep=False)):
        ss.invalid_edit = True
        st.error('Terdapat tanggal target yang sama untuk satu RCE', icon='❗')
    else:
        ss.invalid_edit = False
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both'].copy()

    changes.fillna({
        'ID': 'NULL', 'Target GA': 'NULL',
        'Target CPP': 'NULL', 'Target Revenue': 'NULL'
    }, inplace=True)
    changes.rename(columns={'_merge': 'Difference'}, inplace=True)
    changes['Update'] = (
        (changes.duplicated(subset=['ID'], keep=False)) &
        (changes['Difference'] == 'right_only')
    )
    changes['Target Date'] = (
        changes['Tahun'].astype(int).astype(str) + '-' +
        changes['Bulan'].map(month_number).astype(str) + '-1'
    )
    changes['RCE'] = changes['RCE'].str.split(':').str[0]

    insert_update_target = changes[
        changes['Difference'] == 'left_only'
    ][[
        'ID', 'Target Date', 'RCE', 'Target GA',
        'Target CPP', 'Target Revenue'
    ]].values
    insert_update_target = tuple(map(tuple, insert_update_target))
    insert_update_target = ', '.join([str(i) for i in insert_update_target])
    insert_update_target = insert_update_target.replace("'NULL'", 'NULL')

    delete_target = changes[
        (changes['Difference'] == 'right_only') &
        (changes['Update'] == False)
    ]['ID'].values
    delete_target = ', '.join([f"'{i}'" for i in delete_target])

    sql = []

    if insert_update_target:
        sql.append(f"""
            INSERT INTO RceTarget VALUES {insert_update_target} AS new
                ON DUPLICATE KEY UPDATE
                target_date = new.target_date,
                rce_id = new.rce_id,
                target_ga = new.target_ga,
                target_cpp = new.target_cpp,
                target_revenue = new.target_revenue;
        """)

    if delete_target:
        sql.append(f"""
            DELETE FROM RceTarget WHERE `id` IN ({delete_target});
        """)
    
    return sql

def edit_agent_target(filter_query: str = ''):
    df_original = fetch_data('Agent Target Editing', filter_query).reset_index()
    df_original['ID'] = df_original['ID'].astype(str)

    df_modified: pd.DataFrame = st.data_editor(
        df_original, num_rows='dynamic',
        use_container_width=True, on_change=is_editing,
        column_config={
            'ID': st.column_config.TextColumn(disabled=True, default='auto'),
            'RCE Target ID': st.column_config.SelectboxColumn(
                options=fetch_data_primary('Rce Target Id Name'), required=True,
            ),
            'Agent': st.column_config.SelectboxColumn(
                options=fetch_data_primary('Agent Id Name'), required=True,
            ),
            'Target GA': st.column_config.NumberColumn(),
            'Target CPP': st.column_config.NumberColumn()
        }
    )

    df_modified['ID'] = df_modified['ID'].replace('auto', None)

    if any(df_modified.duplicated(['RCE Target ID', 'Agent'], keep=False)):
        ss.invalid_edit = True
        st.error('Terdapat tanggal target yang sama untuk satu Agent', icon='❗')
    else:
        ss.invalid_edit = False
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both'].copy()

    changes.fillna({
        'ID': 'NULL', 'Target GA': 'NULL', 'Target CPP': 'NULL'
    }, inplace=True)
    changes.rename(columns={'_merge': 'Difference'}, inplace=True)
    changes['Update'] = (
        (changes.duplicated(subset=['ID'], keep=False)) &
        (changes['Difference'] == 'right_only')
    )
    changes['RCE Target ID'] = changes['RCE Target ID'].str.split(':').str[0]
    changes['Agent'] = changes['Agent'].str.split(':').str[0]

    insert_update_target = changes[
        changes['Difference'] == 'left_only'
    ][[
        'ID', 'RCE Target ID', 'Agent', 'Target GA', 'Target CPP'
    ]].values
    insert_update_target = tuple(map(tuple, insert_update_target))
    insert_update_target = ', '.join([str(i) for i in insert_update_target])
    insert_update_target = insert_update_target.replace("'NULL'", 'NULL')

    delete_target = changes[
        (changes['Difference'] == 'right_only') &
        (changes['Update'] == False)
    ]['ID'].values
    delete_target = ', '.join([f"'{i}'" for i in delete_target])

    sql = []

    if insert_update_target:
        sql.append(f"""
            INSERT INTO AgentTarget VALUES {insert_update_target} AS new
                ON DUPLICATE KEY UPDATE
                rce_target_id = new.rce_target_id,
                agent_id = new.agent_id,
                target_ga = new.target_ga,
                target_cpp = new.target_cpp;
        """)

    if delete_target:
        sql.append(f"""
            DELETE FROM AgentTarget WHERE `id` IN ({delete_target});
        """)
    
    return sql

def activation_upload(data: pd.DataFrame):
    changes = data.copy()
    changes.fillna({
        'Date': 'NULL', 'Product': 'NULL', 'Tenure': 'NULL',
        'Order Type': 'NULL', 'Tactical Regular': 'NULL',
        'Guaranteed Revenue': 'NULL'
    }, inplace=True)

    delete_activation = [changes['Date'].min(), changes['Date'].max()]

    changes['Agent'] = changes['Agent'].str.split(':').str[0]
    changes['Date'] = changes['Date'].astype(str)

    insert_activation = changes[[
        'Date', 'Product', 'Tenure', 'Agent', 'Order Type',
        'Tactical Regular', 'Guaranteed Revenue'
    ]].values
    insert_activation = tuple(map(tuple, insert_activation))
    insert_activation = ', '.join([str(i) for i in insert_activation])
    insert_activation = insert_activation.replace("'NULL'", 'NULL')

    sql = []

    if delete_activation:
        sql.append(f"""
            DELETE FROM DailyActivation
            WHERE activation_date BETWEEN '{delete_activation[0]}' AND 
            '{delete_activation[1]}';
        """)

    if insert_activation:
        sql.append(f"""
            INSERT INTO DailyActivation (
                activation_date,
                product,
                tenure,
                agent_id,
                order_type,
                tactical_regular,
                guaranteed_revenue
            )
            VALUES
                {insert_activation};
        """)
    
    return sql

def edit_activation(data: pd.DataFrame = None, filter_query: str = ''):
    if data is not None:
        return activation_upload(data)

    else:
        df_original = fetch_data('Activation Editing', filter_query).reset_index()
        df_original['ID'] = df_original['ID'].astype(str)
    
    order_type = ['New Registration', 'Migration', 'Change Postpaid Plan']
    tactical_regular = ['Tactical', 'Regular']

    df_modified: pd.DataFrame = st.data_editor(
        df_original, num_rows='dynamic',
        use_container_width=True, on_change=is_editing,
        column_config={
            'ID': st.column_config.TextColumn(disabled=True, default='auto'),
            'Date': st.column_config.DateColumn(
                required=True, default=datetime.now().date(), format='DD/MM/YYYY'
            ),
            'Tenure': st.column_config.NumberColumn(min_value=1, step=1),
            'Agent': st.column_config.SelectboxColumn(
                options=fetch_data_primary('Agent Id Name'), required=True,
            ),
            'Order Type': st.column_config.SelectboxColumn(
                options=order_type, default=order_type[0]
            ),
            'Tactical Regular': st.column_config.SelectboxColumn(
                options=tactical_regular, default=tactical_regular[0]
            ),
            'Guaranteed Revenue': st.column_config.NumberColumn(min_value=0)
        }
    )

    df_modified['ID'] = df_modified['ID'].replace('auto', None)
    
    changes = df_modified.merge(
        df_original, indicator = True, how='outer',
    ).loc[lambda x : x['_merge'] != 'both'].copy()

    changes.fillna({
        'ID': 'NULL', 'Date': 'NULL', 'Product': 'NULL', 'Tenure': 'NULL',
        'Order Type': 'NULL', 'Tactical Regular': 'NULL',
        'Guaranteed Revenue': 'NULL'
    }, inplace=True)
    changes.rename(columns={'_merge': 'Difference'}, inplace=True)
    changes['Update'] = (
        (changes.duplicated(subset=['ID'], keep=False)) &
        (changes['Difference'] == 'right_only')
    )
    changes['Agent'] = changes['Agent'].str.split(':').str[0]
    changes['Date'] = changes['Date'].astype(str)

    insert_update_activation = changes[
        changes['Difference'] == 'left_only'
    ][[
        'ID', 'Date', 'Product', 'Tenure', 'Agent', 'Order Type',
        'Tactical Regular', 'Guaranteed Revenue'
    ]].values
    insert_update_activation = tuple(map(tuple, insert_update_activation))
    insert_update_activation = ', '.join([str(i) for i in insert_update_activation])
    insert_update_activation = insert_update_activation.replace("'NULL'", 'NULL')

    delete_activation = changes[
        (changes['Difference'] == 'right_only') &
        (changes['Update'] == False)
    ]['ID'].values
    delete_activation = ', '.join([f"'{i}'" for i in delete_activation])

    sql = []

    if insert_update_activation:
        sql.append(f"""
            INSERT INTO DailyActivation VALUES {insert_update_activation} AS new
                ON DUPLICATE KEY UPDATE
                activation_date = new.activation_date,
                tenure = new.tenure,
                agent_id = new.agent_id,
                order_type = new.order_type,
                tactical_regular = new.tactical_regular,
                guaranteed_revenue = new.guaranteed_revenue;
        """)

    if delete_activation:
        sql.append(f"""
            DELETE FROM DailyActivation WHERE `id` IN ({delete_activation});
        """)
    
    return sql

def execute_sql_query(sql: list):
    ss.db_is_loading = True
    check_connection()

    try:
        cursor: db_cur = ss.db_connection.cursor()

        for query in sql:
            cursor.execute(query)
            ss.db_connection.commit()

        cursor.close()
        st.cache_data.clear()
        ss.db_is_loading = False

        return (True, 'Success')
    
    except Exception as e:
        cursor.close()
        st.cache_data.clear()
        check_connection()
        ss.db_is_loading = False

        return (False, e)