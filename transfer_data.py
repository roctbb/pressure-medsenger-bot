import datetime
from flask import Flask
# from config import *
from database import *
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import argparse
from colorama import Fore, Back, Style

app = Flask(__name__)
# app.config.from_object(__name__)

db_uri = "postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
# app.config.update(ENV='developer')
# app.config.update(DEBUG=True)
app.config.update(SECRET_KEY='JKJH!Jhjhjhj456545_jgnbh~hfgbgb')

db = SQLAlchemy(app)

print('db', db)

def out_red(text):
    print(Fore.RED + text)
    print(Style.RESET_ALL)

def out_red_light(text):
    print(Fore.LIGHTRED_EX + text)
    print(Style.RESET_ALL)
def out_yellow(text):
    print(Fore.YELLOW + text)
    print(Style.RESET_ALL)
def out_blue(text):
    print(Fore.BLUE + text)
    print(Style.RESET_ALL)
def out_green(text):
    print(Fore.GREEN + text)
    print(Style.RESET_ALL)
def out_green_light(text):
    print(Fore.LIGHTGREEN_EX + text)
    print(Style.RESET_ALL)
def out_cyan_light(text):
    print(Fore.LIGHTCYAN_EX + text)
    print(Style.RESET_ALL)
def out_magenta_light(text):
    print(Fore.LIGHTMAGENTA_EX + text)
    print(Style.RESET_ALL)

out_green_light('Script started')

class CategoryParams(db.Model):
    __tablename__ = 'category_params'

    #id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(25), primary_key=True)
    mode = db.Column(db.String(10))
    params = db.Column(db.JSON)
    timetable = db.Column(db.JSON)
    show = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_push = db.Column(db.DateTime)

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

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='?')

    return parser

parser = createParser()
namespace = parser.parse_args()
contract_id = namespace.name

# print('namespace', contract_id, type(contract_id))

query_str = "SELECT * FROM measurements WHERE contract_id = " + "'" + contract_id + "'"

records = DB.select(query_str)

# print('records', records)

for record in records:
    category = record[2]
    mode = record[4]
    params = record[6]
    timetable = record[7]
    show = record[8]
    created_at = record[9]
    updated_at = record[10]

    if (category == 'shin_volume_left'):
        category = 'leg_circumference_left'

    if (category == 'shin_volume_right'):
        category = 'leg_circumference_right'

    if (category == 'waist'):
        category = 'waist_circumference'

    out_cyan_light(category)
    print(mode)
    print(params)
    print(timetable)
    print(show)
    print(created_at)
    print(updated_at)

    try:
        category_params = CategoryParams(contract_id=contract_id,
                                         category=category,
                                         mode=mode,
                                         params=params,
                                         timetable=timetable,
                                         show=show,
                                         created_at=created_at,
                                         updated_at=updated_at,
                                         last_push=datetime.datetime.now())

        db.session.add(category_params)
        # db.session.commit()

        # query = CategoryParams.query.filter_by(contract_id=contract_id, category=category)

        # if query.count() != 0:
        #     contract = query.first()
        #
        #     print('params before ', contract.params)

            # contract.mode = mode
            # contract.params = params
            # contract.timetable = timetable
            # contract.show = show

            # print('params after', contract.params)
    except Exception as e:
        out_red_light('ERROR >>')
        print(e)

    print('------------')