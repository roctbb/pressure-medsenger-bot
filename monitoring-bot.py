import datetime
import time
from threading import Thread
from flask import Flask, request, render_template, flash, redirect, url_for
import json
import requests
from config import *
from database import *
from const import *
import threading
import psycopg2
from multiprocessing import Process
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        delta = time.time() - self._startTime

        if delta > 1:
            print("Elapsed time: {:.3f} sec".format(delta))


class Debug:
    @staticmethod
    def delimiter():
        return '-------------------------------------------------------------------------------'


class Aux:
    @staticmethod
    def quote():
        return "'"

    @staticmethod
    def doublequote():
        return '"'


class DB:
    @staticmethod
    def connection():
        try:
            return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        except Exception as e:
            print('ERROR_CONNECTION', e)
            return 'ERROR_CONNECTION'

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



app = Flask(__name__)
# app.config.from_object(__name__)

db_uri = "postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config.update(ENV='developer')
# app.config.update(DEBUG=True)
app.config.update(SECRET_KEY='JKJH!Jhjhjhj456545_jgnbh~hfgbgb')

# print('app.config', app.config)

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))

    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

class ActualBots(db.Model):
    __tablename__ = 'actual_bots'

    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer)
    actual = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # def __init__(self, id, contract_id, actual, created_at, updated_at):
    #     self.id = id
    #     self.contract_id = contract_id
    #     self.actual = actual
    #     self.created_at = created_at
    #     self.updated_at = updated_at

    # def __repr__(self):
    #     return "\nActualBots: ('%s','%s')\n---------------------------\n" % (self.contract_id, self.actual)

# for actual_bot in actual_bots:
#     print('actual_bot', actual_bot)

class CategoryParams(db.Model):
    __tablename__ = 'category_params'

    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer)
    category = db.Column(db.String(25))
    mode = db.Column(db.String(10))
    params = db.Column(db.JSON)
    timetable = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # def __init__(self, id, contract_id, category, mode, params, timetable, created_at, updated_at):
    #     self.id = id
    #     self.category = category
    #     self.mode = mode
    #     self.params = params
    #     self.timetable = timetable
    #     self.created_at = created_at
    #     self.updated_at = updated_at

    # def __repr__(self):
    #     return "\nCategoryParams: ('%s','%s', '%s')\n---------------------------\n" % (self.category, self.params, self.timetable)

# category_params = CategoryParams.query.all()
# print(category_params)
# CategoryParamsObj = CategoryParams.query.filter_by(category='systolic_pressure').first()
# print(CategoryParamsObj)
# params = CategoryParamsObj.params
# timetable = CategoryParamsObj.timetable
# print('=================')

# print('CategoryParamsObj', CategoryParamsObj)
# print('')
# print('params', params['max'])
# print('')
# print('timetable', timetable)
# print('')
# print('db', db)
# print(Debug.delimiter())

bootstrap = Bootstrap(app)

# data = {}

def getCategories():
    try:
        data_request = {
            "api_key": APP_KEY
        }

        response = requests.post(MAIN_HOST + '/api/agents/records/categories', json=data_request)

        # print('response', response)

        if (response.status_code == 200):
        #     print(json.loads(response.text))
        #     print(Debug.delimiter())

            return json.loads(response.text)

        print('response.status_code = ', response.status_code)

        return response.status_code


    except Exception as e:
        print('error: ', e)

# categories = getCategories()
#
# print('categories ***************************** ', categories)
# print(Debug.delimiter())

def getRecords(contract_id, category_name):
    try:
        data_request = {
            "contract_id": contract_id,
            "api_key": APP_KEY,
            "category_name": category_name
        }

        response = requests.post(MAIN_HOST + '/api/agents/records/get', json=data_request)

        # print('response', response)

        if (response.status_code == 200):
            # print(json.loads(response.text))

            return json.loads(response.text)

        print('response.status_code = ', response.status_code)

        return response.status_code


    except Exception as e:
        print('error: ', e)


def add_record(contract_id, category_name, value, record_time=None):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "category_name": category_name,
        "value": value,
    }

    if record_time:
        data['time'] = record_time

    try:
        # print('data', data)
        # print('call add_record()', MAIN_HOST + '/api/agents/records/add')
        requests.post(MAIN_HOST + '/api/agents/records/add', json=data)

    except Exception as e:
        print('error requests.post', e)


def dump(data, label):
    print('dump: ' + label + ' ', data)


def delayed(delay, f, args):
    # print('args', args)
    timer = threading.Timer(delay, f, args=args)
    timer.start()


def check_float(number):
    try:
        float(number)
        return True
    except:
        return False


def check_digit(number):
    try:
        int(number)
        return True
    except:
        return False


def digit(val):
    try:
        return int(val)
    except:
        return False


def check_str(val):
    try:
        str(str)
        return True
    except:
        return False


# ***************************************************

def post_request(data, query='/api/agents/message'):
    try:
        # print('post_request()')
        # print('MAIN', MAIN_HOST + query)
        return requests.post(MAIN_HOST + query, json=data)
    except Exception as e:
        print('error post_request()', e)


def warning(contract_id, param, param_value, param_value_2=''):
    text_patient = ''
    text_doctor = ''

    if (param == 'systolic_pressure'):
        param = 'pressure'

    if (param == 'diastolic_pressure'):
        param = 'pressure'

    if (param == 'shin_volume_left'):
        param = 'shin'

    if (param == 'shin_volume_right'):
        param = 'shin'

    if (param in AVAILABLE_MEASUREMENTS):

        if (param == 'pressure'):
            text_patient = MESS_PRESSURE_PATIENT.format(
                param_value, param_value_2)
            text_doctor = MESS_PRESSURE_DOCTOR.format(
                param_value, param_value_2)

        if (param == 'shin'):
            text_patient = MESS_SHIN_PATIENT.format(
                param_value, param_value_2)
            text_doctor = MESS_SHIN_DOCTOR.format(
                param_value, param_value_2)

        if (param == 'weight'):
            text_patient = MESS_WEIGHT_PATIENT
            text_doctor = MESS_WEIGHT_DOCTOR

        if (param == 'temperature'):
            text_patient = MESS_TEMPERATURE_PATIENT
            text_doctor = MESS_TEMPERATURE_DOCTOR

        if (param == 'glukose'):
            text_patient = MESS_GLUKOSE_PATIENT
            text_doctor = MESS_GLUKOSE_DOCTOR

        if (param == 'pain_assessment'):
            text_patient = MESS_PAIN_PATIENT
            text_doctor = MESS_PIAN_DOCTOR

        if (param == 'spo2'):
            text_patient = MESS_SPO2_PATIENT
            text_doctor = MESS_SPO2_DOCTOR

        if (param == 'waist'):
            text_patient = MESS_WAIST_PATIENT
            text_doctor = MESS_WAIST_DOCTOR

        data_patient = {
            "contract_id": contract_id,
            "api_key": APP_KEY,
            "message": {
                "text": text_patient.format(param_value),
                "is_urgent": True,
                "only_patient": True,
            }
        }

        data_doctor = {
            "contract_id": contract_id,
            "api_key": APP_KEY,
            "message": {
                "text": text_doctor.format(param_value),
                "is_urgent": True,
                "only_doctor": True,
                "need_answer": True
            }
        }

        post_request(data_patient)
        post_request(data_doctor)
        print('warning')
        print(Debug.delimiter())


def sender():
    # deadline = 1

    while True:
        # print('START sender')
        # print('')
        query_str = "SELECT * FROM measurements WHERE show = true"
        records = DB.select(query_str)
        measurements = records

        for measurement in measurements:
            id = str(measurement[0])
            contract_id = measurement[1]
            name = measurement[2]
            mode = measurement[4]
            params = measurement[6]
            timetable = measurement[7]
            show = measurement[8]
            date_str = measurement[9].strftime("%Y-%m-%d %H:%M:%S")
            last_push = measurement[9].timestamp()

            # print('id', id)
            # print('contract_id', contract_id)
            # print('name', name)

            if (show == False):
                continue

            data = {}

            if mode == 'daily':
                for item in timetable:
                    if (item == 'hours'):
                        hours = timetable[item]

                        hours_array = []

                        for hour in hours:
                            hour_value = hour['value']
                            hours_array.append(hour_value)

                        for hour in hours:
                            date = datetime.date.fromtimestamp(time.time())
                            hour_value = hour['value']

                            if (hour_value == 24):
                                hour_value = 0

                            measurement_date = datetime.datetime(date.year, date.month, date.day, int(hour_value), 0, 0)
                            control_time = measurement_date.timestamp()
                            current_time = time.time()
                            push_time = last_push
                            diff_current_control = current_time - control_time

                            if diff_current_control > 0:
                                # print('control_time', control_time)
                                # print('push_time', push_time)
                                # print(Debug.delimiter())

                                if control_time > push_time:
                                    print('Запись измерения в messages', name)

                                    if (name == 'systolic_pressure'):
                                        name = 'pressure'

                                    if (name == 'diastolic_pressure'):
                                        name = 'pressure'

                                    if (name == 'shin_volume_left'):
                                        name = 'shin'

                                    if (name == 'shin_volume_right'):
                                        name = 'shin'

                                    len_hours_array = len(hours_array)
                                    action_deadline = 1

                                    pattern = hour_value

                                    for i in range(len_hours_array):
                                        # action_deadline = 0

                                        if (len_hours_array == 1):
                                            if (pattern < hours_array[0]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                # print('11 pattern < hours_array[0]', hours_array[0], pattern,
                                                #       action_deadline)
                                                break

                                            if (pattern == hours_array[0]):
                                                action_deadline = 24
                                                # print('12 pattern == hours_array[0]', hours_array[0], pattern,
                                                #       action_deadline)
                                                break

                                            if (pattern > hours_array[0]):
                                                action_deadline = (24 + int(pattern)) - int(hours_array[0])
                                                # print('13 pattern > hours_array[0]', hours_array[0], pattern,
                                                #       action_deadline)
                                                break

                                        if (len_hours_array == 2):
                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(pattern)

                                                # print('21 pattern < hours_array[0]', hours_array[0], pattern,
                                                #       action_deadline)
                                                break

                                            if (pattern == hours_array[1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                # print('22 pattern > hours_array[0]', hours_array[0], pattern,
                                                #       action_deadline)
                                                break

                                        if (len_hours_array > 2):

                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(hours_array[0])
                                                # print('31 pattern <= hours_array[0]', hours_array[0], pattern,
                                                #       action_deadline)
                                                break

                                            if (pattern == hours_array[len_hours_array - 1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                # print('32 pattern >= hours_array[len_hours_array-1]', hours_array[0],
                                                #       pattern, action_deadline)
                                                break

                                            if (i > 0):
                                                if (hours_array[i] == pattern):
                                                    action_deadline = int(hours_array[i + 1]) - int(hours_array[i])
                                                    # print('33 hours_array[i] >= pattern', hours_array[0], pattern,
                                                    #       action_deadline)
                                                    # break

                                    # print('action_deadline', action_deadline)

                                    action_deadline = action_deadline * 60 * 60
                                    data_deadline = int(time.time()) + action_deadline

                                    # print('name', name)
                                    # print('int(time.time())', int(time.time()))
                                    # print('data_deadline', data_deadline - 600)

                                    data = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "message": {
                                            "text": MESS_MEASUREMENT[name]['text'],
                                            "action_link": "frame/" + name,
                                            "action_deadline": data_deadline - 600,
                                            "action_name": MESS_MEASUREMENT[name]['action_name'],
                                            "action_onetime": True,
                                            "only_doctor": False,
                                            "only_patient": True,
                                        },
                                        "hour_value": hour_value
                                    }

                                    data_update_deadline = int(time.time()) - (4 * 60 * 60)

                                    data_update = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "action_link": "frame/" + name,
                                        "action_deadline": data_update_deadline
                                    }

                                    try:
                                        query = '/api/agents/correct_action_deadline'
                                        # print('post request')
                                        # print('MAIN_HOST + query', MAIN_HOST + query)
                                        # print('data', data)
                                        # response = requests.post(MAIN_HOST + query, json=data_update)
                                        # print('response ' + MAIN_HOST + query, response.status_code)

                                    except Exception as e:
                                        print('error requests.post', e)

                                    # print('data_update', data_update)
                                    # print(Debug.delimiter())

                                    query_str = "UPDATE measurements set last_push = '" + \
                                                str(datetime.datetime.fromtimestamp(
                                                    current_time).isoformat()) + Aux.quote() + \
                                                " WHERE id = '" + str(id) + Aux.quote()

                                    # print('query_str', query_str)

                                    DB.query(query_str)
                                    print('data measurements', data)
                                    post_request(data)

        query_str = "SELECT * FROM medicines WHERE show = true"

        records = DB.select(query_str)
        medicines = records

        for medicine in medicines:
            id = str(medicine[0])
            contract_id = medicine[1]
            name = medicine[2]
            mode = medicine[3]
            dosage = medicine[4]
            amount = medicine[5]
            timetable = medicine[6]
            show = measurement[7]
            date_str = medicine[8].strftime("%Y-%m-%d %H:%M:%S")
            last_push = medicine[8].timestamp()

            if (show == False):
                continue

            # hours_array = []
            # data = {}

            if mode == 'daily':
                for item in timetable:
                    if (item == 'hours'):
                        hours = timetable[item]

                        hours_array = []

                        for hour in hours:
                            hours_array.append(hour['value'])

                        for hour in hours:
                            date = datetime.date.fromtimestamp(time.time())
                            hour_value = hour['value']

                            if (hour_value == 24):
                                hour_value = 0

                            # hours_array.append(hour_value)
                            medicine_date = datetime.datetime(date.year, date.month, date.day, int(hour_value), 0, 0)

                            control_time = medicine_date.timestamp()
                            current_time = time.time()
                            push_time = last_push
                            diff_current_control = current_time - control_time

                            if diff_current_control > 0:
                                if control_time > push_time:
                                    print('Запись лекарства в messages', name)

                                    len_hours_array = len(hours_array)
                                    action_deadline = 1

                                    pattern = hour_value

                                    for i in range(len_hours_array):
                                        # action_deadline = 0

                                        if (len_hours_array == 1):
                                            if (pattern < hours_array[0]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('111 pattern < hours_array[0]', hours_array[0], pattern,
                                                      action_deadline)
                                                break

                                            if (pattern == hours_array[0]):
                                                action_deadline = 24
                                                print('112 pattern == hours_array[0]', hours_array[0], pattern,
                                                      action_deadline)
                                                break

                                            if (pattern > hours_array[0]):
                                                action_deadline = (24 + int(pattern)) - int(hours_array[0])
                                                print('113 pattern > hours_array[0]', hours_array[0], pattern,
                                                      action_deadline)
                                                break

                                        if (len_hours_array == 2):
                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(pattern)
                                                print('221 pattern < hours_array[0]', hours_array[0], pattern,
                                                      action_deadline)
                                                break

                                            if (pattern == hours_array[1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('222 pattern > hours_array[0]', hours_array[0], pattern,
                                                      action_deadline)
                                                break

                                            # if (pattern > hours_array[0] and pattern < hours_array[1]):
                                            #     action_deadline = hours_array[0] - pattern
                                            #     print('23 pattern < hours_array[0]', action_deadline)
                                            #     break

                                        if (len_hours_array > 2):

                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(hours_array[0])
                                                print('331 pattern <= hours_array[0]', hours_array[0], pattern,
                                                      action_deadline)
                                                break

                                            # if (pattern == hours_array[0]):
                                            #     action_deadline = hours_array[0] - pattern
                                            #     print('31 pattern <= hours_array[0]', hours_array[0], pattern,
                                            #           action_deadline)
                                            #     break

                                            if (pattern == hours_array[len_hours_array - 1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('332 pattern >= hours_array[len_hours_array-1]', hours_array[0],
                                                      pattern, action_deadline)
                                                break

                                            if (i > 0):
                                                # true_hour = hours_array[i]

                                                if (hours_array[i] == pattern):
                                                    action_deadline = int(hours_array[i + 1]) - int(hours_array[i])
                                                    print('333 hours_array[i] >= pattern', hours_array[0], pattern,
                                                          action_deadline)
                                                    # break

                                    # if (action_deadline > 0):
                                    #     deadline = action_deadline

                                    # print('action_deadline', action_deadline)

                                    data_deadline = int(time.time()) + (action_deadline * 60 * 60)

                                    data = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "message": {
                                            "text": MESS_MEDICINE['text'].format(name),
                                            "action_link": MESS_MEDICINE['action_link'].format(id),
                                            "action_name": MESS_MEDICINE['action_name'].format(name, dosage),
                                            "action_onetime": True,
                                            "action_deadline": data_deadline - 600,
                                            "only_doctor": False,
                                            "only_patient": True,
                                        }
                                    }

                                    # print('name medicine', name)
                                    # print('data_deadline medicine', data_deadline - 600)
                                    # print('int(time.time()) medicine', int(time.time()))
                                    # print(Debug.delimiter())

                                    data_update_deadline = int(time.time()) - (4 * 60 * 60)

                                    # print('data_update_deadline | medicine', data_update_deadline)

                                    data_update = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "action_link": "medicine/" + id,
                                        "action_deadline": data_update_deadline
                                    }

                                    # print('data_update', data_update)

                                    try:
                                        query = '/api/agents/correct_action_deadline'
                                        # print('post request')
                                        # print('MAIN_HOST + query', MAIN_HOST + query)
                                        # print('data', data)

                                        # print('data_update', type(data_update), data_update)
                                        # print(Debug.delimiter())

                                        # data_update = json.dumps(data_update)

                                        # print('data_update dumps', type(data_update), data_update)
                                        # print(Debug.delimiter())

                                        response = requests.post(MAIN_HOST + query, json=data_update)
                                        # print('response | medicine: ', MAIN_HOST + query, response.status_code)
                                        # print(Debug.delimiter())

                                        # if (response.status_code == 200):
                                        #     print('requests.post', response.text)
                                    except Exception as e:
                                        print('error requests.post', e)

                                    # print('data_update medicine', data_update)
                                    # print(Debug.delimiter())

                                    query_str = "UPDATE medicines set last_push = '" + \
                                                str(datetime.datetime.fromtimestamp(
                                                    current_time).isoformat()) + Aux.quote() + \
                                                " WHERE id = '" + str(id) + Aux.quote()

                                    # print('query_str medicines', query_str)
                                    # print(Debug.delimiter())

                                    DB.query(query_str)

                                    print('data medicines', data)
                                    # print(Debug.delimiter())

                                    post_request(data)

        # print('')
        # print('END Sender')
        # print(Debug.delimiter())

        time.sleep(20)


def quard():
    key = request.args.get('api_key', '')

    if key != APP_KEY:
        print('WRONG_APP_KEY')
        return 'WRONG_APP_KEY'

    try:
        contract_id = int(request.args.get('contract_id', ''))
        print('quard() | contract_id', contract_id)
    except Exception as e:
        print('ERROR_CONTRACT', e)
        return 'ERROR_CONTRACT'

    try:
        sql_str = "SELECT * FROM actual_bots WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()

        conn = DB.connection()
        cursor = conn.cursor()
        cursor.execute(sql_str)
        actual_bots = {}

        for row in cursor:
            actual_bots = {
                "name": row[2],
                "alias": row[3],
                "mode": row[4]
            }

        cursor.close()
        conn.close()

        if len(actual_bots) == 0:
            print('ERROR_CONTRACT_NOT_EXISTS')
            return 'ERROR_CONTRACT_NOT_EXISTS'

    except Exception as e:
        print('ERROR_CONNECTION', e)
        return 'ERROR_CONNECTION'

    return contract_id


# GET ROUTES

@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/csv-reader', methods=['GET'])
def csv_reader__():
    csv_path = "./backup/amCharts.csv"

    with open(csv_path, "r") as f_obj:
        csv_reader(f_obj)

    # csv_reader('./backup/amCharts.csv')
    print('csv_reader()')
    return 'csv_reader()'


@app.errorhandler(404)
def page_not_found(error):
    title = "Page not found: 404"
    error_text = title
    return render_template('404.html', title=title, error_text=error_text), 404


@app.errorhandler(500)
def server_error(error):
    title = "Server error: 500"
    error_text = title
    return render_template('500.html', title=title, error_text=error_text), 500


@app.route('/graph-test', methods=['GET'])
def graph_test():
    contract_id = quard()

    proc = Process(target=zzz, args=(contract_id,))
    proc.start()
    print('proc', proc)
    proc. join()
    proc.close()
    print('proc close', proc)

    # zzz(2)

    print('graph_test()')

    return 'graph_test()'


@app.route('/graph', methods=['GET'])
def graph():
    contract_id = quard()

    print('graph()')

    constants = {}
    systolic = []
    diastolic = []
    pulse = []
    glukose = []
    weight = []
    temperature = []
    times = []
    pressure_timestamp = []
    glukose_trace_times = []
    weight_trace_times = []
    temperature_trace_times = []
    medicines_names = []
    medicines_trace_times = []
    medicines_trace_data = {}
    medicines_times_ = []
    time_placeholder = "%Y-%m-%d %H:%M:%S"
    dosage = []
    amount = []

    array_x = []
    array_y = []
    comments = []
    systolic_dic = {}

    if (True):
        constants = {}

        query_str = "SELECT * FROM measurements WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()
        records = DB.select(query_str)

        medical_record_categories = getCategories()

        for item in medical_record_categories:
            category = item['name']

            try:
                CategoryParamsObj = CategoryParams.query.filter_by(category=category).first()
                # print('CategoryParamsObj = ', CategoryParamsObj.category)

                params = CategoryParamsObj.params
                # timetable = CategoryParamsObj.timetable
            except Exception as e:
                print('ERROR CONNECTION CategoryParamsObj', e)

            if (category == 'spo2'):
                try:
                    constants['max_spo2'] = params['max']
                    constants['min_spo2'] = params['min']
                except Exception as e:
                    constants['max_spo2'] = MAX_SPO2_DEFAULT
                    constants['min_spo2'] = MIN_SPO2_DEFAULT

            if (category == 'glukose'):
                try:
                    constants['max_glukose'] = params['max']
                    constants['min_glukose'] = params['min']
                except Exception as e:
                    constants['max_glukose'] = MAX_GLUKOSE_DEFAULT
                    constants['min_glukose'] = MIN_GLUKOSE_DEFAULT

            if (category == 'pain_assessment'):
                try:
                    constants['max_pain'] = params['max']
                    constants['min_pain'] = params['min']
                except Exception as e:
                    constants['max_pain'] = MAX_PAIN_DEFAULT
                    constants['min_pain'] = MIN_PAIN_DEFAULT

            if (category == 'systolic_pressure' or category == 'diastolic_pressure' or category == 'pulse'):
                try:
                    constants['max_systolic'] = params['max_systolic']
                    constants['min_systolic'] = params['min_systolic']
                    constants['max_diastolic'] = params['max_diastolic']
                    constants['min_diastolic'] = params['min_diastolic']
                    constants['max_pulse'] = params['max_pulse']
                    constants['min_pulse'] = params['min_pulse']
                except:
                    constants['max_systolic'] = MAX_SYSTOLIC_DEFAULT
                    constants['min_systolic'] = MIN_SYSTOLIC_DEFAULT
                    constants['max_diastolic'] = MAX_DIASTOLIC_DEFAULT
                    constants['min_diastolic'] = MIN_DIASTOLIC_DEFAULT
                    constants['max_pulse'] = MAX_PULSE_DEFAULT
                    constants['min_pulse'] = MIN_PULSE_DEFAULT

            if (category == 'weight'):
                try:
                    constants['max_weight'] = params['max']
                    constants['min_weight'] = params['min']
                except Exception as e:
                    constants['max_weight'] = MAX_WEIGHT_DEFAULT
                    constants['min_weight'] = MIN_WEIGHT_DEFAULT

            if (category == 'waist_circumference'):
                try:
                    constants['max_waist'] = params['max']
                    constants['min_waist'] = params['min']
                except Exception as e:
                    constants['max_waist'] = MAX_WAIST_DEFAULT
                    constants['min_waist'] = MIN_WAIST_DEFAULT

            if (category == 'leg_circumference_left' or category == 'leg_circumference_right'):
                try:
                    constants['max_shin_left'] = params['max']
                    constants['min_shin_left'] = params['min']
                    constants['max_shin_right'] = params['max']
                    constants['min_shin_right'] = params['min']
                except Exception as e:
                    constants['max_shin_left'] = MAX_SHIN_DEFAULT
                    constants['min_shin_left'] = MIN_SHIN_DEFAULT
                    constants['max_shin_right'] = MAX_SHIN_DEFAULT
                    constants['min_shin_right'] = MIN_SHIN_DEFAULT

            if (category == 'temperature'):
                try:
                    constants['max_temperature'] = params['max']
                    constants['min_temperature'] = params['min']
                except Exception as e:
                    constants['max_temperature'] = MAX_TEMPERATURE_DEFAULT
                    constants['min_temperature'] = MIN_TEMPERATURE_DEFAULT

            # print(category , type(category), type('temperature'))
            # print('---')

        print('constants', constants)

        # for row in records:
        #     name = row[2]
        #     params = row[6]
        #
        #     if (name == 'systolic_pressure'):
        #         try:
        #             constants['max_systolic'] = params['max_systolic']
        #             constants['min_systolic'] = params['min_systolic']
        #             constants['max_diastolic'] = params['max_diastolic']
        #             constants['min_diastolic'] = params['min_diastolic']
        #             constants['max_pulse'] = params['max_pulse']
        #             constants['min_pulse'] = params['min_pulse']
        #         except:
        #             constants['max_systolic'] = MAX_SYSTOLIC_DEFAULT
        #             constants['min_systolic'] = MIN_SYSTOLIC_DEFAULT
        #             constants['max_diastolic'] = MAX_DIASTOLIC_DEFAULT
        #             constants['min_diastolic'] = MIN_DIASTOLIC_DEFAULT
        #             constants['max_pulse'] = MAX_PULSE_DEFAULT
        #             constants['min_pulse'] = MIN_PULSE_DEFAULT
        #
        #     if (name == 'weight'):
        #         try:
        #             constants['max_weight'] = params['max']
        #             constants['min_weight'] = params['min']
        #         except Exception as e:
        #             constants['max_weight'] = MAX_WEIGHT_DEFAULT
        #             constants['min_weight'] = MIN_WEIGHT_DEFAULT
        #
        #     if (name == 'shin_volume_left'):
        #         try:
        #             constants['max_shin_left'] = params['max']
        #             constants['min_shin_left'] = params['min']
        #             constants['max_shin_right'] = params['max']
        #             constants['min_shin_right'] = params['min']
        #         except Exception as e:
        #             constants['max_shin_left'] = MAX_SHIN_DEFAULT
        #             constants['min_shin_left'] = MIN_SHIN_DEFAULT
        #             constants['max_shin_right'] = MAX_SHIN_DEFAULT
        #             constants['min_shin_right'] = MIN_SHIN_DEFAULT
        #
        #     if (name == 'temperature'):
        #         try:
        #             constants['max_temperature'] = params['max']
        #             constants['min_temperature'] = params['min']
        #         except Exception as e:
        #             constants['max_temperature'] = MAX_TEMPERATURE_DEFAULT
        #             constants['min_temperature'] = MIN_TEMPERATURE_DEFAULT
        #
        #     if (name == 'glukose'):
        #         try:
        #             constants['max_glukose'] = params['max']
        #             constants['min_glukose'] = params['min']
        #         except Exception as e:
        #             constants['max_glukose'] = MAX_GLUKOSE_DEFAULT
        #             constants['min_glukose'] = MIN_GLUKOSE_DEFAULT
        #
        #     if (name == 'pain_assessment'):
        #         try:
        #             constants['max_pain'] = params['max']
        #             constants['min_pain'] = params['min']
        #         except Exception as e:
        #             constants['max_pain'] = MAX_PAIN_DEFAULT
        #             constants['min_pain'] = MIN_PAIN_DEFAULT
        #
        #     if (name == 'spo2'):
        #         try:
        #             constants['max_spo2'] = params['max']
        #             constants['min_spo2'] = params['min']
        #         except Exception as e:
        #             constants['max_spo2'] = MAX_SPO2_DEFAULT
        #             constants['min_spo2'] = MIN_SPO2_DEFAULT
        #
        #     if (name == 'waist'):
        #         try:
        #             constants['max_waist'] = params['max']
        #             constants['min_waist'] = params['min']
        #         except Exception as e:
        #             constants['max_waist'] = MAX_WAIST_DEFAULT
        #             constants['min_waist'] = MIN_WAIST_DEFAULT

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = (SELECT id FROM measurements WHERE contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and name = 'systolic_pressure') ORDER BY time ASC"

        records = DB.select(query_str)

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        # START SYS STAT

        # stat max

        query_str = "SELECT m.id, max(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = 'systolic_pressure' GROUP BY m.id"

        records = DB.select(query_str)

        sys_max_value = 0

        for row in records:
            sys_max_value = row[1]

        # stat min

        query_str = "SELECT m.id, min(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = 'systolic_pressure' GROUP BY m.id"

        records = DB.select(query_str)

        sys_min_value = 0

        for row in records:
            sys_min_value = row[1]

        # stat avg

        query_str = "SELECT m.id, avg(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = 'systolic_pressure' GROUP BY m.id"

        records = DB.select(query_str)

        sys_avg_value = 0

        for row in records:
            sys_avg_value = row[1]

        # sys_common_count

        query_str = "SELECT m.id, count(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = 'systolic_pressure' GROUP BY m.id"

        # print('query_str', query_str)

        records = DB.select(query_str)

        sys_common_count = 0

        for row in records:
            sys_common_count = row[1]

        query_str = "SELECT m.id, count(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and mr.value < " + Aux.quote() + str(
            constants['max_systolic']) + Aux.quote() + " and m.name = 'systolic_pressure' GROUP BY m.id"

        records = DB.select(query_str)

        sys_norm_count = 0
        sys_slice_normal = 0
        sys_slice_critical = 0

        for row in records:
            sys_norm_count = row[1]

        try:
            sys_slice_normal = (sys_norm_count * 100) // sys_common_count
            sys_slice_critical = 100 - sys_slice_normal
        except Exception as e:
            print('error try except', e)

        # QUERIES SYS WEEK
        fromTable = "FROM measurements m "
        name = "systolic_pressure"
        paramName = Aux.quote() + name + Aux.quote()
        innerJoin = " INNER JOIN measurements_results mr ON m.id = mr.measurements_id "
        where = " where m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and mr.time > (now() - interval '7 days') and m.name = " + paramName
        query_str = "SELECT m.id, max(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_max_week = 0
        for row in records:
            sys_max_week = row[1]
        query_str = "SELECT m.id, min(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_min_week = 0
        for row in records:
            sys_min_week = row[1]
        query_str = "SELECT m.id, avg(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_avg_week = 0
        for row in records:
            sys_avg_week = row[1]
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_common_count_week = 0
        for row in records:
            sys_common_count_week = row[1]
            # print('sys_common_count_week', sys_common_count_week)
        andWhere = " and mr.value < " + Aux.quote() + str(constants['max_systolic']) + Aux.quote()
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + andWhere + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_normal_count_week = 0
        sys_slice_normal_week = 0
        sys_slice_critical_week = 0
        for row in records:
            sys_normal_count_week = row[1]
        try:
            sys_slice_normal_week = (sys_normal_count_week * 100) // sys_common_count_week
            sys_slice_critical_week = 100 - sys_slice_normal_week
        except Exception as e:
            print('error try except sys_slice_normal_week', e)
        # END QUERIES SYS WEEK

        # QUERIES SYS MONTH
        fromTable = "FROM measurements m "
        name = "systolic_pressure"
        paramName = Aux.quote() + name + Aux.quote()
        innerJoin = " INNER JOIN measurements_results mr ON m.id = mr.measurements_id "
        where = " where m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and mr.time > (now() - interval '30 days') and m.name = " + paramName
        query_str = "SELECT m.id, max(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_max_month = 0
        for row in records:
            sys_max_month = row[1]
        query_str = "SELECT m.id, min(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_min_month = 0
        for row in records:
            sys_min_month = row[1]
        query_str = "SELECT m.id, avg(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_avg_month = 0
        for row in records:
            sys_avg_month = row[1]
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_common_count_month = 0
        for row in records:
            sys_common_count_month = row[1]
        andWhere = " and mr.value < " + Aux.quote() + str(constants['max_systolic']) + Aux.quote()
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + andWhere + " GROUP BY m.id"
        records = DB.select(query_str)
        sys_normal_count_month = 0
        sys_slice_normal_month = 0
        sys_slice_critical_month = 0
        for row in records:
            sys_normal_count_month = row[1]
        try:
            sys_slice_normal_month = (sys_normal_count_month * 100) // sys_common_count_month
            sys_slice_critical_month = 100 - sys_slice_normal_month
        except Exception as e:
            print('error try except sys month', e)
        # END QUERIES SYS WEEK

        response = getRecords(contract_id, 'systolic_pressure')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        systolic_dic = {
            "x": x,
            "y": y,
            # "sys_max_value": int(sys_max_value),
            # "sys_max_value": max(y),
            # "sys_min_value": int(sys_min_value),
            # "sys_min_value": min(y),
            # "sys_avg_value": sum(sys_avg_value),
            # "sys_slice_normal": int(sys_slice_normal),
            # "sys_slice_critical": int(sys_slice_critical),
            # "sys_max_week": int(sys_max_week),
            # "sys_min_week": int(sys_min_week),
            # "sys_avg_week": int(sys_avg_week),
            # "sys_slice_normal_week": int(sys_slice_normal_week),
            # "sys_slice_critical_week": int(sys_slice_critical_week),
            # "sys_max_month": int(sys_max_month),
            # "sys_min_month": int(sys_min_month),
            # "sys_avg_month": int(sys_avg_month),
            # "sys_slice_normal_month": int(sys_slice_normal_month),
            # "sys_slice_critical_month": int(sys_slice_critical_month),
            "comments": '',
            "name": category['description']
        }

        systolic = systolic_dic

        # START DIA DATA

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'diastolic_pressure')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

        # START DIA STAT

        # stat max

        name = "diastolic_pressure"

        query_str = "SELECT m.id, max(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = " + Aux.quote() + str(name) + Aux.quote() + " GROUP BY m.id"

        records = DB.select(query_str)

        dia_max_value = 0

        for row in records:
            dia_max_value = row[1]

        # stat min

        query_str = "SELECT m.id, min(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = " + Aux.quote() + str(name) + Aux.quote() + " GROUP BY m.id"

        records = DB.select(query_str)

        dia_min_value = 0

        for row in records:
            dia_min_value = row[1]

        # stat avg

        query_str = "SELECT m.id, avg(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = " + Aux.quote() + str(name) + Aux.quote() + " GROUP BY m.id"

        records = DB.select(query_str)

        dia_avg_value = 0

        for row in records:
            dia_avg_value = row[1]

        # dia_common_count

        query_str = "SELECT m.id, count(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and m.name = " + Aux.quote() + str(name) + Aux.quote() + " GROUP BY m.id"

        records = DB.select(query_str)

        dia_common_count = 0

        for row in records:
            dia_common_count = row[1]

        query_str = "SELECT m.id, count(mr.value) FROM measurements m INNER JOIN measurements_results mr ON m.id = mr.measurements_id WHERE m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and mr.value < " + Aux.quote() + str(
            constants['max_diastolic']) + Aux.quote() + " and m.name = " + Aux.quote() + str(
            name) + Aux.quote() + " GROUP BY m.id"

        records = DB.select(query_str)

        dia_norm_count = 0
        dia_slice_normal = 0
        dia_slice_critical = 0

        for row in records:
            dia_norm_count = row[1]

        try:
            dia_slice_normal = (dia_norm_count * 100) // dia_common_count
            dia_slice_critical = 100 - dia_slice_normal
        except Exception as e:
            print('error try except dia', e)

        # END DIA STAT

        # QUERIES DIA MONTH
        fromTable = "FROM measurements m "
        name = "diastolic_pressure"
        paramName = Aux.quote() + name + Aux.quote()
        innerJoin = " INNER JOIN measurements_results mr ON m.id = mr.measurements_id "
        where = " where m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and mr.time > (now() - interval '30 days') and m.name = " + paramName
        query_str = "SELECT m.id, max(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_max_month = 0
        for row in records:
            dia_max_month = row[1]
        query_str = "SELECT m.id, min(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_min_month = 0
        for row in records:
            dia_min_month = row[1]
        query_str = "SELECT m.id, avg(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_avg_month = 0
        for row in records:
            dia_avg_month = row[1]
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_common_count_month = 0
        for row in records:
            dia_common_count_month = row[1]
        andWhere = " and mr.value < " + Aux.quote() + str(constants['max_diastolic']) + Aux.quote()
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + andWhere + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_normal_count_month = 0
        dia_slice_normal_month = 0
        dia_slice_critical_month = 0
        for row in records:
            dia_normal_count_month = row[1]
        try:
            dia_slice_normal_month = (dia_normal_count_month * 100) // dia_common_count_month
            dia_slice_critical_month = 100 - dia_slice_normal_month
        except Exception as e:
            print('error try except sys month', e)
        # END QUERIES DIA MONTH

        # QUERIES DIA WEEK
        fromTable = "FROM measurements m "
        name = "diastolic_pressure"
        paramName = Aux.quote() + name + Aux.quote()
        innerJoin = " INNER JOIN measurements_results mr ON m.id = mr.measurements_id "
        where = " where m.contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and mr.time > (now() - interval '7 days') and m.name = " + paramName
        query_str = "SELECT m.id, max(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_max_week = 0
        for row in records:
            dia_max_week = row[1]
        query_str = "SELECT m.id, min(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_min_week = 0
        for row in records:
            dia_min_week = row[1]
        query_str = "SELECT m.id, avg(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_avg_week = 0
        for row in records:
            dia_avg_week = row[1]
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_common_count_week = 0
        for row in records:
            dia_common_count_week = row[1]
        andWhere = " and mr.value < " + Aux.quote() + str(constants['max_diastolic']) + Aux.quote()
        query_str = "SELECT m.id, count(mr.value) " + fromTable + innerJoin + where + andWhere + " GROUP BY m.id"
        records = DB.select(query_str)
        dia_normal_count_week = 0
        dia_slice_normal_week = 0
        dia_slice_critical_week = 0
        for row in records:
            dia_normal_count_week = row[1]
        try:
            dia_slice_normal_week = (dia_normal_count_week * 100) // dia_common_count_week
            dia_slice_critical_week = 100 - dia_slice_normal_week
        except Exception as e:
            print('error try except sys month', e)
        # END QUERIES DIA WEEK

        response = getRecords(contract_id, 'diastolic_pressure')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        diastolic_dic = {
            "x": x,
            "y": y,
            # "dia_max_value": int(dia_max_value),
            # "dia_min_value": int(dia_min_value),
            # "dia_avg_value": int(dia_avg_value),
            # "dia_slice_normal": int(dia_slice_normal),
            # "dia_slice_critical": int(dia_slice_critical),
            # "dia_max_month": int(dia_max_month),
            # "dia_min_month": int(dia_min_month),
            # "dia_avg_month": int(dia_avg_month),
            # "dia_slice_normal_month": int(dia_slice_normal_month),
            # "dia_slice_critical_month": int(dia_slice_critical_month),
            # "dia_max_week": int(dia_max_week),
            # "dia_min_week": int(dia_min_week),
            # "dia_avg_week": int(dia_avg_week),
            # "dia_slice_normal_week": int(dia_slice_normal_week),
            # "dia_slice_critical_week": int(dia_slice_critical_week),
            "name": category['description']
        }

        diastolic = diastolic_dic

        # START PULSE DATA

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'pulse')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

        response = getRecords(contract_id, 'pulse')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        pulse_dic = {
            "x": x,
            "y": y,
            "name": category['description']
        }

        pulse = pulse_dic

        query_str = "select * from medicines m inner join medicines_results mr on m.id = mr.medicines_id " + \
                    " WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        text = []
        dosage = []
        amount = []
        medicines_data = {}

        for row in records:
            date_ = row[13]
            text.append(row[2])
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))

        query_str = "SELECT m.name, m.dosage, m.amount, m.id, count(m.id) c FROM medicines m INNER JOIN medicines_results mr ON m.id = mr.medicines_id " + \
                    " WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " GROUP BY m.id"

        records = DB.select(query_str)

        for row in records:
            name = row[0]
            dosage = row[1]
            amount = row[2]
            medicines_id = row[3]
            query_str = "SELECT * FROM medicines_results WHERE medicines_id = '" + medicines_id + "'"
            results = DB.select(query_str)

            medicines_times_ = []

            for item in results:
                date_ = item[2]
                medicines_times_.append(date_.strftime("%Y-%m-%d %H:%M:%S"))

            medicines_data[name] = {
                'medicines_times_': medicines_times_,
                'dosage': dosage,
                'amount': amount
            }

        medicine_dic = {
            "x": array_x,
            "y": array_y,
            "text": text,
            "dosage": [],
            "amount": [],
            "name": "Лекарства",
            "medicines_data": medicines_data
        }

        medicine = medicine_dic

        medicines_trace_data = medicines_data

        # ********************************************* pain_assessment

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'pain_assessment')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'pain_assessment')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        pain_assessment_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        # print('pain_assessment_dic', pain_assessment_dic)

        # ********************************************* weight

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'weight')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'weight')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        weight_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        weight_series = weight_dic

        # ********************************************* temperature

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'temperature')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'temperature')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        temperature_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        temperature_series = temperature_dic

        # ********************************************* glukose

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'glukose')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'glukose')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        glukose_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        glukose_series = glukose_dic

        # ********************************************* SPO2

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'spo2')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'spo2')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        spo2_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        spo2_series = spo2_dic

        # ********************************************* WAIST

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = " \
                    "(SELECT id FROM measurements WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " and name = 'waist')" + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'waist_circumference')
        x = []
        y = []
        category = response['category']
        values = response['values']

        print('values', values)
        print('-----------------------')

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        waist_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        print(' waist_dic *************************************',  waist_dic)

        waist_series = waist_dic

        # shin_left_dic

        param_name = 'shin_volume_left'

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = (SELECT id FROM measurements WHERE contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and name = 'shin_volume_left') ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'leg_circumference_left')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        shin_left_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        shin_left = shin_left_dic

        param_name = 'shin_volume_right'

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = (SELECT id FROM measurements WHERE contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and name = 'shin_volume_right') ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        comments = []

        for row in records:
            date_ = row[2]
            value_ = row[3]
            array_x.append(date_.strftime("%Y-%m-%d %H:%M:%S"))
            array_y.append(value_)

            if (row[6] == None):
                comments.append('')
            else:
                comments.append(row[6])

        response = getRecords(contract_id, 'leg_circumference_right')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime("%Y-%m-%d %H:%M:%S"))
            y.append(value['value'])

        shin_right_dic = {
            "x": x,
            "y": y,
            "comments": comments,
            "name": category['description']
        }

        shin_right = shin_right_dic

        return render_template('graph.html',
                               constants=constants,
                               medicine=medicine,
                               systolic=systolic,
                               comments=comments,
                               diastolic=diastolic,
                               pulse_=pulse,
                               glukose=glukose_series,
                               weight=weight_series,
                               temperature=temperature_series,
                               pain_assessment=pain_assessment_dic,
                               spo2=spo2_series,
                               waist=waist_series,
                               shin_left=shin_left,
                               shin_right=shin_right,
                               medicine_trace_data=medicines_trace_data
                               )
    else:
        print('NONE_MEASUREMENTS')
        return NONE_MEASUREMENTS

    return "ok"


@app.route('/settings', methods=['GET'])
def settings():
    print('settings')

    try:
        contract_id = quard()
        # print('contract_id', contract_id)
    except Exception as e:
        print('UNKNOWN ERROR')
        return 'UNKNOWN ERROR'

    if (contract_id == ERROR_KEY):
        return ERROR_KEY

    if (contract_id == ERROR_CONTRACT):
        return ERROR_CONTRACT

    query_str = "SELECT * FROM measurements WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()

    records = DB.select(query_str)

    measurements_main = []
    pressure = {}
    shin = {}

    for row in records:
        timetable = []
        measurement_new = {}
        id = row[0]
        name = row[2]
        alias = row[3]
        mode = row[4]
        unit = row[5]
        params = row[6]
        timetable.append(row[7])
        show = row[8]
        last_push = row[9]

        if (name == 'shin_volume_left'):
            shin['id'] = id
            shin['name'] = 'shin'
            shin['alias'] = 'измерение голени'
            shin['mode'] = mode
            shin['last_push'] = last_push.strftime("%Y-%m-%d %H:%M:%S")
            shin['unit'] = unit
            shin['timetable'] = timetable
            shin['show'] = show

            try:
                shin['max'] = params['max']
                shin['min'] = params['min']
            except Exception as e:
                shin['max'] = MAX_SHIN
                shin['min'] = MIN_SHIN

            measurements_main.append(shin)

            continue

        if (name == 'systolic_pressure'):
            pressure['id'] = id
            pressure['name'] = 'pressure'
            pressure['alias'] = 'давление'
            pressure['mode'] = mode
            pressure['last_push'] = last_push.strftime("%Y-%m-%d %H:%M:%S")
            pressure['unit'] = unit
            pressure['timetable'] = timetable
            pressure['show'] = show

            pressure['max_systolic'] = params['max_systolic']
            pressure['min_systolic'] = params['min_systolic']
            pressure['max_diastolic'] = params['max_diastolic']
            pressure['min_diastolic'] = params['min_diastolic']
            pressure['max_pulse'] = params['max_pulse']
            pressure['min_pulse'] = params['min_pulse']
            continue

        out_list = ['systolic_pressure', 'diastolic_pressure', 'pulse', 'shin_volume_left', 'shin_volume_right']

        if (name not in out_list):
            measurement_new['id'] = id
            measurement_new['name'] = name
            measurement_new['alias'] = alias
            measurement_new['mode'] = mode
            measurement_new['last_push'] = last_push.strftime("%Y-%m-%d %H:%M:%S")
            measurement_new['unit'] = unit
            measurement_new['show'] = show
            measurement_new['timetable'] = timetable

            try:
                measurement_new['max'] = params['max']
                measurement_new['min'] = params['min']
            except Exception as e:
                measurement_new['max'] = 0
                measurement_new['min'] = 0
                # print('ERROR_KEY')

            measurements_main.append(measurement_new)

    measurements_main.append(pressure)

    query_str = "SELECT m.name, m.dosage, m.amount, m.id, m.timetable, m.show, m.last_push, m.created_at, m.mode FROM medicines m  WHERE contract_id = " + Aux.quote() + str(
        contract_id) + Aux.quote()
    records = DB.select(query_str)

    medicines_new = []

    for row in records:
        times = []
        timetable = []
        medicines_data = {}

        name = row[0]
        dosage = row[1]
        amount = row[2]
        uid = row[3]
        timetable.append(row[4])
        show = row[5]
        last_sent = row[6].strftime("%Y-%m-%d %H:%M:%S")
        created_at = row[7].strftime("%Y-%m-%d %H:%M:%S")
        mode = row[8]
        medicines_id = uid
        query_str = "SELECT * FROM medicines_results WHERE medicines_id = '" + medicines_id + "'"
        results = DB.select(query_str)

        for item in results:
            # print('item', name, item[2])
            date_ = item[2]
            times.append(date_.strftime("%Y-%m-%d %H:%M:%S"))

        medicines_data = {
            # 'times': times,
            'uid': uid,
            'name': name,
            'dosage': dosage,
            'amount': amount,
            'mode': mode,
            'timetable': timetable,
            'last_sent': last_sent,
            'created_at': created_at,
            'show': show
        }

        medicines_new.append(medicines_data)

    # Конец Формирование данных

    medicines = medicines_new
    measurements = measurements_main

    # print('measurements', measurements)

    return render_template('settings.html',
                           medicines_data=json.dumps(medicines),
                           measurements_data=json.dumps(measurements),
                           medicines_data_new=json.dumps(medicines_new))


@app.route('/medicine/<uid>', methods=['GET'])
def medicine_done(uid):
    result = quard()

    if result in ERRORS:
        return result

    query_str = "INSERT INTO medicines_results VALUES(nextval('medicines_results$id$seq')," + \
                Aux.quote() + str(uid) + Aux.quote() + \
                ",(select * from now()), (select * from now()), (select * from now()))"

    result = DB.query(query_str)

    if (result != 'SUCCESS_QUERY'):
        return result

    return MESS_THANKS


@app.route('/frame/<string:pull>', methods=['GET'])
def action_pull(pull):
    print('pull', pull)

    auth = quard()

    constants = {}

    if (auth == 'ERROR_KEY'):
        print('/frame ERROR_KEY')
        return ERROR_KEY

    if (auth == 'ERROR_CONTRACT'):
        print('/frame ERROR_CONTRACT')
        return ERROR_CONTRACT

    if (pull == 'shin'):
        constants['shin_max'] = MAX_SHIN
        constants['shint_min'] = MIN_SHIN

        return render_template('shin.html', tmpl=pull, constants=constants)

    if (pull == 'pressure'):
        constants['sys_max'] = MAX_SYSTOLIC
        constants['sys_min'] = MIN_SYSTOLIC
        constants['dia_max'] = MAX_DIASTOLIC
        constants['dia_min'] = MIN_DIASTOLIC
        constants['pulse_max'] = MAX_PULSE
        constants['pulse_min'] = MIN_PULSE

        return render_template('pressure.html', tmpl=pull, constants=constants)

    if (pull == 'weight'):
        constants['weight_max'] = MAX_WEIGHT
        constants['weight_min'] = MIN_WEIGHT

        return render_template('measurement.html', tmpl=pull, constants=constants)

        # return render_template('pressure.html', tmpl=pull, constants=constants)

    if (pull == 'temperature'):
        constants['temperature_max'] = MAX_TEMPERATURE
        constants['temperature_min'] = MIN_TEMPERATURE

        return render_template('measurement.html', tmpl=pull, constants=constants)

        # return render_template('temperature.html', tmpl=pull, constants=constants)

    if (pull == 'glukose'):
        constants['glukose_max'] = MAX_GLUKOSE
        constants['glukose_min'] = MIN_GLUKOSE

        return render_template('measurement.html', tmpl=pull, constants=constants)

        # return render_template('glukose.html', tmpl=pull, constants=constants)

    if (pull == 'pain_assessment'):
        constants['pain_assessment_max'] = MAX_ASSESSMENT
        constants['ain_assessment_min'] = MIN_ASSESSMENT

        return render_template('pain_assessment.html', tmpl=pull, constants=constants)

    if (pull == 'spo2'):
        constants['spo2_max'] = MAX_SPO2
        constants['spo2_min'] = MIN_SPO2
        return render_template('spo2.html', tmpl=pull, constants=constants)

    if (pull == 'waist'):
        constants['waist_max'] = MAX_WAIST
        constants['waist_min'] = MIN_WAIST

        return render_template('waist.html', tmpl=pull, constants=constants)

    return render_template('measurement.html', tmpl=pull, constants=constants)


# POST ROUTES

@app.route('/status', methods=['POST'])
def status():
    print('status')

    try:
        data = request.json
        # print('status() | data', data)
    except Exception as e:
        print('error status()', e)
        return 'error status'

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    query_str = "SELECT contract_id FROM actual_bots"

    records = DB.select(query_str)

    tracked_contracts = []

    for row in records:
        tracked_contracts.append(row[0])

    answer = {
        "is_tracking_data": True,
        "supported_scenarios": SUPPORTED_SCENARIOS,
        "tracked_contracts": tracked_contracts
    }

    # print('answer', answer)

    return json.dumps(answer)


@app.route('/settings', methods=['POST'])
def setting_save():
    contract_id = quard()

    if contract_id in ERRORS:
        return contract_id

    try:
        data = json.loads(request.form.get('json'))
    except Exception as e:
        print('ERROR_JSON_LOADS', e)
        return 'ERROR_JSON_LOADS'

    for measurement in data['measurements_data']:
        params = {}
        id = measurement['id']
        name = measurement['name']

        if (name == 'pressure'):
            params['max_systolic'] = measurement['max_systolic']
            params['min_systolic'] = measurement['min_systolic']
            params['max_diastolic'] = measurement['max_diastolic']
            params['min_diastolic'] = measurement['min_diastolic']
            params['max_pulse'] = measurement['max_pulse']
            params['min_pulse'] = measurement['min_pulse']
        else:
            # print('measurement', measurement)
            # print(Debug.delimiter())

            params['max'] = measurement['max']
            params['min'] = measurement['min']

        params = json.dumps(params)
        mode = measurement['mode']
        timetable = measurement['timetable'][0]

        timetable_new = {}

        for item in timetable:
            if (item == 'hours'):
                hours__ = []

                for el in timetable[item]:
                    element = el['value']

                    hour_value_ = int(element)

                    if (hour_value_ == 24):
                        hour_value_ = 0

                    hours__.append(hour_value_)

                unique_array = {each: each for each in hours__}.values()
                hours__.sort()

                hours_new__ = []

                new = []

                for hour in unique_array:
                    new.append(hour)
                    hours_new__.append({
                        "value": hour
                    })

                new.sort()

                new_array = []

                for hour in new:
                    new_array.append({
                        "value": hour
                    })

                timetable_new[item] = new_array
            else:
                timetable_new[item] = timetable[item]

        timetable = timetable_new

        timetable = json.dumps(timetable)
        show = str(measurement['show'])

        query_str = "UPDATE measurements set " + \
                    " mode = " + Aux.quote() + mode + Aux.quote() + "," + \
                    " params = " + Aux.quote() + params + Aux.quote() + "," + \
                    " timetable = " + Aux.quote() + timetable + Aux.quote() + "," + \
                    " show = " + Aux.quote() + show + Aux.quote() + \
                    " WHERE id = " + Aux.quote() + str(id) + Aux.quote()

        DB.query(query_str)

    for medicine in data['medicines_data']:
        name = medicine['name']
        mode = medicine['mode']
        dosage = medicine['dosage']
        amount = medicine['amount']
        json__ = medicine['timetable'][0]
        timetable = json__
        # timetable = json.dumps(json__)
        show = medicine['show']

        timetable_new = {}

        timetable_new = {}

        for item in timetable:
            if (item == 'hours'):
                hours__ = []

                for el in timetable[item]:
                    element = el['value']

                    hour_value_ = int(element)

                    if (hour_value_ == 24):
                        hour_value_ = 0

                    hours__.append(hour_value_)

                unique_array = {each: each for each in hours__}.values()
                hours__.sort()

                hours_new__ = []

                new = []

                for hour in unique_array:
                    new.append(hour)
                    hours_new__.append({
                        "value": hour
                    })

                new.sort()

                new_array = []

                for hour in new:
                    new_array.append({
                        "value": hour
                    })

                timetable_new[item] = new_array
            else:
                timetable_new[item] = timetable[item]

        timetable = timetable_new

        timetable = json.dumps(timetable)

        if "uid" not in medicine:
            query_str = "INSERT INTO medicines VALUES((select uuid_generate_v4())," + \
                        str(contract_id) + "," + \
                        Aux.quote() + str(name) + Aux.quote() + "," + \
                        Aux.quote() + str(mode) + Aux.quote() + "," + \
                        Aux.quote() + str(dosage) + Aux.quote() + "," + \
                        Aux.quote() + str(amount) + Aux.quote() + "," + \
                        Aux.quote() + str(timetable) + Aux.quote() + "," + \
                        Aux.quote() + str(show) + Aux.quote() + \
                        ", (select * from now()), (select * from now()), (select * from now()))"

            DB.query(query_str)
        else:
            query_str = "UPDATE medicines set name = " + Aux.quote() + str(name) + Aux.quote() + "," + \
                        " mode = " + Aux.quote() + str(mode) + Aux.quote() + "," + \
                        " dosage = " + Aux.quote() + str(dosage) + Aux.quote() + "," + \
                        " amount = " + Aux.quote() + str(amount) + Aux.quote() + "," + \
                        " timetable = " + Aux.quote() + str(timetable) + Aux.quote() + "," + \
                        " show = " + Aux.quote() + str(show) + Aux.quote() + \
                        " WHERE id = " + Aux.quote() + str(medicine['uid']) + Aux.quote()

            DB.query(query_str)

    return "ok"

@app.route('/init', methods=['POST'])
def init():
    new_contract = True

    try:
        data = request.json

        if (data == None):
            print('None data /init')
            return 'None'

        if ('api_key' not in data):
            print('key api_key not exists')
            return 'key api_key not exists'

        if (APP_KEY != data['api_key']):
            print('invalid key')
            return 'invalid key'

        if ('contract_id' not in data):
            print('key contract_id not exists')
            return 'key contract_id not exists'

        contract_id = data['contract_id']

        actual_bots = ActualBots.query.filter_by(contract_id=contract_id)
        id = 0

        for actual_bot in actual_bots:
            id = actual_bot.id

        if id > 0:
            new_contract = False
            print('if id > 0')

            try:
                db.session.query(ActualBots).update({"actual": True})
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('db.session.rollback()', e)
                raise

        print('new_contract = ', new_contract)

        if (new_contract == True):
            try:
                actual_bots = ActualBots(contract_id=contract_id, actual=True, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
                print('actual_bots', actual_bots)
                db.session.add(actual_bots)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('db.session.add(actual_bots)', e)
                raise

            preset = None

            if 'preset' in data:
                preset = data['preset']
            else:
                preset = None

            print('preset = ', preset)

            preset_params = []

            if 'params' in data:
                preset_params = data['params']
            else:
                preset_params = None

            print('preset_params = ', preset_params)

            #  *************************************************************** systolic

            try:
                max_systolic = (preset_params['max_systolic'])
            except Exception as e:
                max_systolic = MAX_SYSTOLIC_DEFAULT

            try:
                min_systolic = preset_params['min_systolic']
            except Exception as e:
                min_systolic = MIN_SYSTOLIC_DEFAULT

            try:
                max_diastolic = preset_params['max_diastolic']
            except Exception as e:
                max_diastolic = MAX_DIASTOLIC_DEFAULT

            try:
                min_diastolic = preset_params['min_diastolic']
            except Exception as e:
                min_diastolic = MIN_DIASTOLIC_DEFAULT

            try:
                max_pulse = preset_params['max_pulse']
            except Exception as e:
                max_pulse = MAX_PULSE_DEFAULT

            try:
                min_pulse = preset_params['min_pulse']
            except Exception as e:
                min_pulse = MIN_PULSE_DEFAULT

            params = {}
            timetable = {
                "days_month": [
                    {
                        "day": 1,
                        "hour": 10
                    }
                ],
                "days_week": [
                    {
                        "day": 1,
                        "hour": 10
                    }
                ],
                "hours": [
                    {
                        "value": 10
                    }
                ]
            }
            mode = 'daily'

            if (preset == 'heartfailure' or preset == 'stenocardia' or preset == 'fibrillation' or preset == 'hypertensia'):
                params = {
                    "max_systolic": max_systolic,
                    "min_systolic": min_systolic,
                    "max_diastolic": max_diastolic,
                    "min_diastolic": min_diastolic,
                    "max_pulse": max_pulse,
                    "min_pulse": min_pulse
                }

                name = 'pressure'

                data = {
                    "contract_id": contract_id,
                    "api_key": APP_KEY,
                    "message": {
                        "text": MESS_MEASUREMENT[name]['text'],
                        "action_link": "frame/" + name,
                        "action_deadline": time.time() + (60 * 60 * 24),
                        "action_name": MESS_MEASUREMENT[name]['action_name'],
                        "action_onetime": True,
                        "only_doctor": False,
                        "only_patient": True,
                    }
                }

                delayed(1, post_request, [data])
            else:
                params = {}

            try:
                category_params = CategoryParams(contract_id=contract_id,
                                                 category='sistolic_pressure',
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)

                category_params = CategoryParams(contract_id=contract_id,
                                                 category='diastolic_pressure',
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)

                category_params = CategoryParams(contract_id=contract_id,
                                                 category='pulse',
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add pressure in category_params >> )', e)
                raise

            # *************************************************************** temperature

            params = {
                "max": MAX_TEMPERATURE_DEFAULT,
                "min": MIN_TEMPERATURE_DEFAULT
            }

            try:
                category_params = CategoryParams(contract_id=contract_id,
                                                 category='temperature',
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add temperature in category_params >> )', e)
                raise

            # *************************************************************** glukose

            try:
                name = 'glukose'

                params = {
                    "max": MAX_GLUKOSE_DEFAULT,
                    "min": MIN_GLUKOSE_DEFAULT
                }

                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add temperature in category_params >> )', e)
                raise

            name = 'weight'

            if (preset == 'heartfailure' or preset == 'stenocardia' or preset == 'fibrillation'):
                try:
                    max_weight = preset_params['max_weight']
                except Exception as e:
                    max_weight = MAX_WEIGHT_DEFAULT

                try:
                    min_weight = preset_params['min_weight']
                except Exception as e:
                    min_weight = MIN_WEIGHT_DEFAULT

                params = {
                    "max": max_weight,
                    "min": min_weight
                }

                data = {
                    "contract_id": contract_id,
                    "api_key": APP_KEY,
                    "message": {
                        "text": MESS_MEASUREMENT[name]['text'],
                        "action_link": "frame/" + name,
                        "action_deadline": time.time() + (60 * 60 * 24),
                        "action_name": MESS_MEASUREMENT[name]['action_name'],
                        "action_onetime": True,
                        "only_doctor": False,
                        "only_patient": True,
                    }
                }

                delayed(1, post_request, [data])
            else:
                params = {}

            try:
                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add weight in category_params >> )', e)
                raise

            # *************************************************************** waist_circumference

            name = 'waist_circumference'

            if (preset == 'heartfailure'):
                try:
                    max_waist = preset_params['max_waist']
                except Exception as e:
                    max_waist = MAX_WAIST_DEFAULT

                try:
                    min_waist = preset_params['min_waist']
                except Exception as e:
                    min_waist = MIN_WAIST_DEFAULT

                params = {
                    "max": max_waist,
                    "min": min_waist
                }

                data = {
                    "contract_id": contract_id,
                    "api_key": APP_KEY,
                    "message": {
                        "text": MESS_MEASUREMENT['waist']['text'],
                        "action_link": "frame/" + "waist",
                        "action_deadline": time.time() + (60 * 60 * 24),
                        "action_name": MESS_MEASUREMENT['waist']['action_name'],
                        "action_onetime": True,
                        "only_doctor": False,
                        "only_patient": True,
                    }
                }

                delayed(1, post_request, [data])
            else:
                params = {}

            try:
                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add waist in category_params >> )', e)
                raise

            # *************************************************************** spo2

            try:
                name = 'spo2'

                params = {
                    "max": MAX_SPO2_DEFAULT,
                    "min": MIN_SPO2_DEFAULT
                }

                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add temperature in category_params >> )', e)
                raise

            # *************************************************************** pain_assessment

            try:
                name = 'pain_assessment'

                params = {
                    "max": MAX_PAIN_DEFAULT,
                    "min": MIN_PAIN_DEFAULT
                }

                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add temperature in category_params >> )', e)
                raise

            params = {
                "max": MAX_SHIN_DEFAULT,
                "min": MIN_SHIN_DEFAULT
            }

            if (preset == 'heartfailure'):
                name = 'shin'

                data = {
                    "contract_id": contract_id,
                    "api_key": APP_KEY,
                    "message": {
                        "text": MESS_MEASUREMENT[name]['text'],
                        "action_link": "frame/" + name,
                        "action_deadline": time.time() + (60 * 60 * 24),
                        "action_name": MESS_MEASUREMENT[name]['action_name'],
                        "action_onetime": True,
                        "only_doctor": False,
                        "only_patient": True,
                    }
                }

                delayed(1, post_request, [data])
            else:
                params = {}

            # *************************************************************** leg_circumference_left

            try:
                name = 'leg_circumference_left'

                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add temperature in category_params >> )', e)
                raise

            # *************************************************************** leg_circumference_right

            try:
                params = {}

                name = 'leg_circumference_right'

                category_params = CategoryParams(contract_id=contract_id,
                                                 category=name,
                                                 mode=mode,
                                                 params=params,
                                                 timetable=timetable,
                                                 created_at=datetime.datetime.now(),
                                                 updated_at=datetime.datetime.now())

                db.session.add(category_params)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('ERROR add temperature in category_params >> )', e)
                raise

            # *************************************************************** next parameter

    except Exception as e:
        print('ERROR INIT', e)
        return 'ERROR INIT'

    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    try:
        data = request.json

        if (data == None):
            return 'None'

        if data['api_key'] != APP_KEY:
            return 'invalid key'

        contract_id = data['contract_id']

        query_str = "SELECT * FROM actual_bots WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()

        records = DB.select(query_str)
        id = 0

        for row in records:
            # print('id', id)
            id = row[1]

        if id > 0:
            query_str = "UPDATE actual_bots SET actual = false WHERE contract_id = " + Aux.quote() + str(
                contract_id) + Aux.quote()

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

    except Exception as e:
        print('error', e)
        return 'ERROR INIT'

    return 'ok'


@app.route('/frame/<string:pull>', methods=['POST'])
def action_pull_save(pull):
    param = ''
    param_value = ''

    contract_id = quard()

    if (contract_id in ERRORS):
        # print('contract_id', contract_id)
        return contract_id

    if (pull in AVAILABLE_MEASUREMENTS):
        # print('pull in AVAILABLE_MEASUREMENTS', pull)
        param = pull
        param_value = request.form.get(param, '')
        comments = request.form.get('comments', '')

    if (pull == 'shin'):
        shin_left = request.form.get('shin_left', '')
        shin_right = request.form.get('shin_right', '')

        if False in map(check_digit, [shin_left, shin_right]):
            return ERROR_FORM

        try:
            shin_left = int(shin_left)
        except Exception as e:
            shin_left = MAX_SHIN_DEFAULT
            print('Exception int(shin_left)', e)

        try:
            shin_right = int(shin_right)
        except Exception as e:
            shin_right = MAX_SHIN_DEFAULT
            print('Exception int(shin_right)', e)

        if (shin_left < MIN_SHIN or shin_left > MAX_SHIN):
            return ERROR_OUTSIDE_SHIN

        if (shin_right < MIN_SHIN or shin_right > MAX_SHIN):
            return ERROR_OUTSIDE_SHIN

        query_str = "select params from measurements where contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and name = 'shin_volume_left'"

        records = DB.select(query_str)

        for row in records:
            params = row[0]

        max_shin = params['max']
        min_shin = params['min']

        try:
            max_shin = int(max_shin)
            min_shin = int(min_shin)
        except Exception as e:
            max_shin = MAX_SHIN
            min_shin = MIN_SHIN
            print("WARNING_NOT_INT", e)

        if (shin_left < min_shin or shin_left > max_shin) or (shin_right < min_shin or shin_right > max_shin):
            delayed(1, warning, [contract_id, 'shin', shin_left, shin_right])

        # # insert shin_left
        # query_str = "select id from measurements where contract_id = " + str(
        #     contract_id) + " and name = 'shin_volume_left'"
        #
        # records = DB.select(query_str)
        #
        # for row in records:
        #     id = row[0]
        #
        # query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(
        #     id) + ",(select * from now())," + str(
        #     shin_left) + ",(select * from now()),(select * from now())," + Aux.quote() + str(
        #     comments) + Aux.quote() + ")"
        #
        # DB.query(query_str)

        delayed(1, add_record, [contract_id, 'leg_circumference_left', shin_left, int(time.time())])

        # insert shin_right
        # query_str = "select id from measurements where contract_id = " + str(
        #     contract_id) + " and name = 'shin_volume_right'"
        #
        # records = DB.select(query_str)
        #
        # for row in records:
        #     id = row[0]
        #
        # query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(
        #     id) + ",(select * from now())," + str(
        #     shin_right) + ",(select * from now()),(select * from now())," + Aux.quote() + str(
        #     comments) + Aux.quote() + ")"
        #
        # DB.query(query_str)

        delayed(1, add_record, [contract_id, 'leg_circumference_right', shin_right, int(time.time())])

    elif (pull == 'pressure'):
        systolic = request.form.get('systolic', '')
        diastolic = request.form.get('diastolic', '')
        pulse_ = request.form.get('pulse_', '')

        if False in map(check_digit, [systolic, diastolic, pulse_]):
            return ERROR_FORM

        try:
            systolic = int(systolic)
        except Exception as e:
            systolic = 120
            print('int(systolic)', e)

        try:
            diastolic = int(diastolic)
        except Exception as e:
            diastolic = 80
            print('int(diastolic)', e)

        try:
            pulse_ = int(pulse_)
        except Exception as e:
            pulse_ = 60
            print('int(pulse)', e)

        if (systolic < MIN_SYSTOLIC or systolic > MAX_SYSTOLIC):
            flash(ERROR_OUTSIDE_SYSTOLIC_TEXT)
            return action_pull(pull)

            # return ERROR_OUTSIDE_SYSTOLIC

        if (diastolic < MIN_DIASTOLIC or diastolic > MAX_DIASTOLIC):
            return ERROR_OUTSIDE_DIASTOLIC

        if (pulse_ < MIN_PULSE or pulse_ > MAX_PULSE):
            return ERROR_OUTSIDE_PULSE

        query_str = "select params from measurements where contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and name = 'systolic_pressure'"

        records = DB.select(query_str)

        for row in records:
            params = row[0]

        try:
            max_systolic = int(params['max_systolic'])
            min_systolic = int(params['min_systolic'])
            max_diastolic = int(params['max_diastolic'])
            min_diastolic = int(params['min_diastolic'])
            max_pulse = int(params['max_pulse'])
            min_pulse = int(params['min_pulse'])
        except Exception as e:
            max_systolic = MAX_SYSTOLIC_DEFAULT
            min_systolic = MIN_SYSTOLIC_DEFAULT
            max_diastolic = MAX_DIASTOLIC_DEFAULT
            min_diastolic = MIN_DIASTOLIC_DEFAULT
            max_pulse = MAX_PULSE_DEFAULT
            min_pulse = MIN_PULSE_DEFAULT
            print("WARNING_NOT_INT", e)

        if not (min_systolic <= systolic <= max_systolic and min_diastolic <= diastolic <= max_diastolic):
            delayed(1, warning, [contract_id, 'pressure', systolic, diastolic])

        query_str = "select id from measurements where contract_id = " + str(
            contract_id) + " and name = 'systolic_pressure'"

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        # query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(
        #     id) + ",(select * from now())," + str(
        #     systolic) + ",(select * from now()),(select * from now())," + Aux.quote() + str(
        #     comments) + Aux.quote() + ")"
        #
        # DB.query(query_str)

        # add_record(contract_id, 'systolic_pressure', systolic, int(time.time()))

        delayed(1, add_record, [contract_id, 'systolic_pressure', systolic, int(time.time())])

        # query_str = "select id from measurements where contract_id = " + str(
        #     contract_id) + " and name = 'diastolic_pressure'"
        #
        # records = DB.select(query_str)
        #
        # for row in records:
        #     id = row[0]
        #
        # query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(
        #     id) + ",(select * from now())," + str(
        #     diastolic) + ",(select * from now()),(select * from now())," + Aux.quote() + str(
        #     comments) + Aux.quote() + ")"
        #
        # DB.query(query_str)

        # add_record(contract_id, 'diastolic_pressure', diastolic, int(time.time()))

        delayed(1, add_record, [contract_id, 'diastolic_pressure', diastolic, int(time.time())])

        # query_str = "select id from measurements where contract_id = " + str(contract_id) + " and name = 'pulse'"
        #
        # records = DB.select(query_str)
        #
        # for row in records:
        #     id = row[0]
        #
        # query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(
        #     id) + ",(select * from now())," + str(
        #     pulse_) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"
        #
        # DB.query(query_str)

        # add_record(contract_id, 'pulse', pulse_, int(time.time()))

        delayed(1, add_record, [contract_id, 'pulse', pulse_, int(time.time())])

    else:
        if check_float(param_value) == False:
            return ERROR_FORM

        query_str = "select params from measurements where contract_id = " + Aux.quote() + str(
            contract_id) + Aux.quote() + " and name = " + Aux.quote() + str(pull) + Aux.quote()

        records = DB.select(query_str)

        for row in records:
            params = row[0]

        try:
            max = params['max']
            min = params['min']
        except Exception as e:
            max = 0
            min = 0
            print("WARNING_FLOAT", e)

        max = float(max)
        min = float(min)
        param_value = float(param_value)

        if (pull == 'spo2' and (param_value < MIN_SPO2 or param_value > MAX_SPO2)):
            param_value_int = int(param_value)
            flash(ERROR_OUTSIDE_SPO2_TEXT, category=param_value_int)
            return action_pull(pull)

        if (param == 'waist' and (param_value < MIN_WAIST or param_value > MAX_WAIST)):
            param_value_int = int(param_value)
            flash(ERROR_OUTSIDE_WAIST_TEXT, category=param_value_int)
            return action_pull(pull)

        if (param == 'weight' and (param_value < MIN_WEIGHT or param_value > MAX_WEIGHT)):
            return ERROR_OUTSIDE_WEIGHT

        if (param == 'glukose' and (param_value < MIN_GLUKOSE or param_value > MAX_GLUKOSE)):
            return ERROR_OUTSIDE_GLUKOSE

        if (param == 'temperature' and (param_value < MIN_TEMPERATURE or param_value > MAX_TEMPERATURE)):
            return ERROR_OUTSIDE_TEMPERATURE

        param_for_record = param

        if (param == 'waist'):
            param_for_record = 'waist_circumference'

        if (param == 'shin_volume_left'):
            param_for_record = 'leg_circumference_left'

        if (param == 'shin_volume_right'):
            param_for_record = 'leg_circumference_right'

        if (param_value < min or param_value > max):
            # Сигналим врачу
            delayed(1, warning, [contract_id, param, param_value])

        # query_str = "select id from measurements where contract_id = " + Aux.quote() + str(
        #     contract_id) + Aux.quote() + " and name = " + Aux.quote() + str(pull) + Aux.quote()
        #
        # records = DB.select(query_str)
        #
        # for row in records:
        #     id = row[0]
        #
        # query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(
        #     id) + ",(select * from now())," + str(
        #     param_value) + ",(select * from now()),(select * from now())," + Aux.quote() + str(
        #     comments) + Aux.quote() + ")"
        #
        # DB.query(query_str)

        delayed(1, add_record, [contract_id, param_for_record, param_value, int(time.time())])

    # print('action_pull_save(pull)', pull)

    return MESS_THANKS


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']

    if key != APP_KEY:
        return ERROR_KEY

    return "ok"


t = Thread(target=sender)
t.start()

app.run(port='9099', host='0.0.0.0')
