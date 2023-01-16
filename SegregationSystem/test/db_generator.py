import sqlite3
import os

if __name__ == '__main__':

    db_name = 'segregation.db'
    db_path = os.path.join(os.path.abspath('..'), 'data', db_name)
    conn = None
    if not os.path.exists(db_path):
        print("Sqlite db doesn't exist, the db will be created")
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Sqlite Connection Error [{e}]")
        exit(1)

    cursor = conn.cursor()
    query = " \
            CREATE TABLE IF NOT EXISTS p_session ( \
                user_id integer, \
                session_id integer, \
                json blob, \
                primary key(user_id, session_id) \
            )"

    try:
        cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Sqlite Execution Error [{e}]")

    conn.close()

