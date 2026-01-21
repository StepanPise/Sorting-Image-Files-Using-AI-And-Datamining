import psycopg2
import psycopg2.extras


class Database:

    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=5433,
            dbname="postgres",
            user="myuser",
            password="mysecretpassword"
        )

        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        print("Connected to PostgreSQL")

    def close(self) -> None:
        self.conn.close()
        print("Connection to PostgreSQL closed")
