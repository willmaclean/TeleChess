import sqlite3
from sqlite3 import Error

DB = 'bot.db'


def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(DB)
    except Error as e:
        print(e)
    return conn


def get_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS chats
                    (chat_id INT,
                    is_group INT,
                    title TEXT)""")
    connection.commit()
    connection.close()


def insert(table, values_dict):
    connection = create_connection()
    cursor = connection.cursor()
    values_to_insert = '?, ' * len(values_dict.keys())
    stmt = f""" INSERT INTO {table}({','.join(values_dict.keys())})
                 VALUES({values_to_insert[:-2]}) """
    cursor.execute(stmt, tuple(values_dict.values()))
    connection.commit()
    return cursor.lastrowid



def exists(table, col, val):
    connection = create_connection()
    cursor = connection.cursor()
    stmt = f"""select * from {table} where {col} = {val}"""
    cursor.execute(stmt)
    data = cursor.fetchall()
    if len(data) == 0:
        return False
    else:
        return True


get_db()
