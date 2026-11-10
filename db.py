import os

import psycopg2
import psycopg2.extras

def connect():
        # Connection settings come from the standard PostgreSQL environment
        # variables, so no password is stored in the source code.
        conn = psycopg2.connect(
            password=os.environ.get('PGPASSWORD'),
            host=os.environ.get('PGHOST', 'localhost'),
            port=os.environ.get('PGPORT', '5432'),
            dbname=os.environ.get('PGDATABASE', 'postgres'),
            user=os.environ.get('PGUSER', 'postgres'),
            cursor_factory=psycopg2.extras.NamedTupleCursor
        )
        conn.autocommit = True
        return conn
