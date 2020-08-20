import psycopg2
from config_db import *

class DB:
    @staticmethod
    def connection():
        try:
            return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        except Exception as e:
            print('ERROR_CONNECTION DB', e)
            return 'ERROR_CONNECTION DB'

    @staticmethod
    def fetchall(table):
        try:
            conn = DB.connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ' + table, ('ALA',))
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            # print('SUCCESS_FETCHALL', table)
            return records
        except Exception as e:
            print('ERROR_FETCHALL', e)
            return 'ERROR_FETCHALL'

    @staticmethod
    def insert(table, values):
        try:
            conn = None
            conn = DB.connection()
            cursor = conn.cursor()
            query_str = "INSERT INTO " + table + " VALUES(" + values + ")"
            cursor.execute(query_str)
            conn.commit()
            cursor.close()
            # print('SUCCESS_INSERT', table)
            return 'SUCCESS_INSERT'
        except (Exception, psycopg2.DatabaseError) as e:
            print('ERROR_INSERT', e)
            return 'ERROR_INSERT'
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def query(query_str):
        try:
            # print(query_str)
            # print(Debug.delimiter())
            conn = None
            conn = DB.connection()
            cursor = conn.cursor()
            cursor.execute(query_str)
            conn.commit()
            cursor.close()

            return 'SUCCESS_QUERY'
        except (Exception, psycopg2.DatabaseError) as e:
            print('ERROR_QUERY', e)
            return 'ERROR_QUERY'
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def select(query_str):
        try:
            conn = None
            conn = DB.connection()
            cursor = conn.cursor()
            cursor.execute(query_str)
            records = cursor.fetchall()
            conn.commit()
            cursor.close()

            return records
        except (Exception, psycopg2.DatabaseError) as e:
            print('ERROR_SELECT', e)
            return 'ERROR_SELECT'
        finally:
            if conn is not None:
                conn.close()