import psycopg2
import psycopg2.extras

def connect():
        conn = psycopg2.connect(
            password='knife612',
            host='localhost',
            port = '5432',
            dbname='postgres', 
            user='postgres',
            cursor_factory=psycopg2.extras.NamedTupleCursor
        )
        conn.autocommit = True
        return conn
