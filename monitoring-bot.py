import datetime
import time
from threading import Thread
from flask import Flask, request, render_template
import json
import requests
from config import *
from database import *
from const import *
import threading
import psycopg2

# from flask_sqlalchemy import SQLAlchemy
# from psycopg2 import sql

class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        delta = time.time() - self._startTime

        if delta > 1:
            print("Elapsed time: {:.3f} sec".format(delta))

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
            print(query_str)
            print(Debug.delimiter())
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


class Debug:
    @staticmethod
    def delimiter():
        return '-------------------------------------------------------------------------------'

app = Flask(__name__)

data = {}

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
        print('data', data)
        print('call add_record()', MAIN_HOST + '/api/agents/records/add')
        requests.post(MAIN_HOST + '/api/agents/records/add', json=data)

    except Exception as e:
        print('connection error', e)

def dump(data, label):
    print('dump: ' + label + ' ', data)

def delayed(delay, f, args):
    print('args', args)
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

# ************

def post_request(data, query='/api/agents/message'):
    try:
        print('post_request()')
        print('MAIN', MAIN_HOST + query)
        return requests.post(MAIN_HOST + query, json=data)
    except Exception as e:
        print('error post_request', e)

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
    deadline = 1

    while True:
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
                                                print('11 pattern < hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (pattern == hours_array[0]):
                                                action_deadline = 24
                                                print('12 pattern == hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (pattern > hours_array[0]):
                                                action_deadline = (24 + int(pattern)) - int(hours_array[0])
                                                print('13 pattern > hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                        if (len_hours_array == 2):
                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(pattern)

                                                print('21 pattern < hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (pattern == hours_array[1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('22 pattern > hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            # if (pattern > hours_array[0] and pattern < hours_array[1]):
                                            #     action_deadline = hours_array[0] - pattern
                                            #     print('23 pattern < hours_array[0]', action_deadline)
                                            #     break

                                        if (len_hours_array > 2):

                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(hours_array[0])
                                                print('31 pattern <= hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (pattern == hours_array[len_hours_array - 1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('32 pattern >= hours_array[len_hours_array-1]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (i > 0):
                                                # true_hour = hours_array[i]

                                                if (hours_array[i] == pattern):
                                                    action_deadline = int(hours_array[i + 1]) - int(hours_array[i])
                                                    print('33 hours_array[i] >= pattern', hours_array[0], pattern, action_deadline)
                                                    # break

                                    # if (action_deadline > 0):
                                    #     deadline = action_deadline

                                    print('action_deadline', action_deadline)

                                    action_deadline = action_deadline * 60 * 60
                                    data_deadline = int(time.time()) + action_deadline

                                    print('name', name)
                                    print('int(time.time())', int(time.time()))
                                    print('data_deadline', data_deadline - 600)

                                    data = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "message": {
                                            "text": MESS_MEASUREMENT[name]['text'],
                                            "action_link": "frame/" + name,
                                            "action_deadline":  data_deadline - 600,
                                            "action_name": MESS_MEASUREMENT[name]['action_name'],
                                            "action_onetime": True,
                                            "only_doctor": False,
                                            "only_patient": True,
                                        },
                                        "hour_value": hour_value
                                    }



                                    data_update_deadline = int(time.time()) - (4 * 60 * 60)

                                    # print('data_update_deadline', data_update_deadline)

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
                                        response = requests.post(MAIN_HOST + query, json=data_update)
                                        print('response', response.status_code)

                                        if (response.status_code == 200):
                                            print('requests.post', response.text)
                                    except Exception as e:
                                        print('error requests.post', e)

                                    print('data_update', data_update)
                                    print(Debug.delimiter())

                                    query_str = "UPDATE measurements set last_push = '" + \
                                                str(datetime.datetime.fromtimestamp(current_time).isoformat()) + Aux.quote() + \
                                                " WHERE id = '" + str(id) + Aux.quote()

                                    DB.query(query_str)
                                    print('data test', data)
                                    post_request(data)

            # if mode == 'weekly':
            #     for item in timetable:
            #         days_week = item['days_week']
            #
            #         for day_hour in days_week:
            #             date = datetime.date.fromtimestamp(time.time())
            #             day_week = date.today().isoweekday()
            #             day_week__ = int(day_hour['day'])
            #
            #             if day_week__ == day_week:
            #                 a = day_hour['hour']
            #                 b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)
            #
            #                 control_time = b.timestamp()
            #                 current_time = time.time()
            #                 push_time = last_push
            #                 diff_current_control = current_time - control_time
            #
            #                 if diff_current_control > 0:
            #                     if control_time > push_time:
            #                         data = {
            #                             "contract_id": contract_id,
            #                             "api_key": APP_KEY,
            #                             "message": {
            #                                 "text": MESS_MEASUREMENT[name]['text'],
            #                                 "action_link": "frame/" + name,
            #                                 "action_name": MESS_MEASUREMENT[name]['action_name'],
            #                                 "action_onetime": True,
            #                                 "only_doctor": False,
            #                                 "only_patient": True,
            #                             }
            #                         }
            #
            #                         measurement['last_push'] = current_time
            #                         post_request(data)

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
                                                print('112 pattern == hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (pattern > hours_array[0]):
                                                action_deadline = (24 + int(pattern)) - int(hours_array[0])
                                                print('113 pattern > hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                        if (len_hours_array == 2):
                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(pattern)
                                                print('221 pattern < hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (pattern == hours_array[1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('222 pattern > hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            # if (pattern > hours_array[0] and pattern < hours_array[1]):
                                            #     action_deadline = hours_array[0] - pattern
                                            #     print('23 pattern < hours_array[0]', action_deadline)
                                            #     break

                                        if (len_hours_array > 2):

                                            if (pattern == hours_array[0]):
                                                action_deadline = int(hours_array[1]) - int(hours_array[0])
                                                print('331 pattern <= hours_array[0]', hours_array[0], pattern, action_deadline)
                                                break

                                            # if (pattern == hours_array[0]):
                                            #     action_deadline = hours_array[0] - pattern
                                            #     print('31 pattern <= hours_array[0]', hours_array[0], pattern,
                                            #           action_deadline)
                                            #     break

                                            if (pattern == hours_array[len_hours_array - 1]):
                                                action_deadline = (24 - int(pattern)) + int(hours_array[0])
                                                print('332 pattern >= hours_array[len_hours_array-1]', hours_array[0], pattern, action_deadline)
                                                break

                                            if (i > 0):
                                                # true_hour = hours_array[i]

                                                if (hours_array[i] == pattern):
                                                    action_deadline = int(hours_array[i + 1]) - int(hours_array[i])
                                                    print('333 hours_array[i] >= pattern', hours_array[0], pattern, action_deadline)
                                                    # break

                                    # if (action_deadline > 0):
                                    #     deadline = action_deadline

                                    print('action_deadline', action_deadline)

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

                                    print('name medicine', name)
                                    print('data_deadline medicine', data_deadline - 600)
                                    print('int(time.time()) medicine', int(time.time()))
                                    # print(Debug.delimiter())

                                    data_update_deadline = int(time.time()) - (4 * 60 * 60)

                                    print('data_update_deadline | medicine', data_update_deadline)

                                    data_update = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "action_link": "medicine/" + id,
                                        "action_deadline": data_update_deadline
                                    }

                                    try:
                                        query = '/api/agents/correct_action_deadline'
                                        # print('post request')
                                        # print('MAIN_HOST + query', MAIN_HOST + query)
                                        # # print('data', data)
                                        response = requests.post(MAIN_HOST + query, json=data_update)
                                        print('response', response.status_code)

                                        if (response.status_code == 200):
                                            print('requests.post', response.text)
                                    except Exception as e:
                                        print('error requests.post', e)

                                    print('data_update medicine', data_update)
                                    print(Debug.delimiter())

                                    query_str = "UPDATE medicines set last_push = '" + \
                                                str(datetime.datetime.fromtimestamp(current_time).isoformat()) + Aux.quote() + \
                                                " WHERE id = '" + str(id) + Aux.quote()

                                    DB.query(query_str)



                                    post_request(data)

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

        for row in records:
            name = row[2]
            params = row[6]

            # print('params', params)
            # print(Debug.delimiter())

            if (name == 'systolic_pressure'):
                constants['max_systolic'] = params['max_systolic']
                constants['min_systolic'] = params['min_systolic']
                constants['max_diastolic'] = params['max_diastolic']
                constants['min_diastolic'] = params['min_diastolic']
                constants['max_pulse'] = params['max_pulse']
                constants['min_pulse'] = params['min_pulse']

            if (name == 'weight'):
                try:
                    constants['max_weight'] = params['max']
                    constants['min_weight'] = params['min']
                except Exception as e:
                    constants['max_weight'] = MAX_WEIGHT_DEFAULT
                    constants['min_weight'] = MIN_WEIGHT_DEFAULT

            if (name == 'shin_volume_left'):
                try:
                    constants['max_shin_left'] = params['max']
                    constants['min_shin_left'] = params['min']
                except Exception as e:
                    constants['max_shin_left'] = MAX_SHIN
                    constants['min_shin_left'] = MIN_SHIN

            if (name == 'shin_volume_right'):
                try:
                    constants['max_shin_right'] = params['max']
                    constants['min_shin_right'] = params['min']
                except Exception as e:
                    constants['max_shin_right'] = params['max']
                    constants['min_shin_right'] = params['min']

            if (name == 'temperature'):
                try:
                    constants['max_temperature'] = MAX_SHIN
                    constants['min_temperature'] = MIN_SHIN
                except Exception as e:
                    constants['max_temperature'] = MAX_TEMPERATURE_DEFAULT
                    constants['min_temperature'] = MIN_TEMPERATURE_DEFAULT

            if (name == 'glukose'):
                try:
                    constants['max_glukose'] = params['max']
                    constants['min_glukose'] = params['min']
                except Exception as e:
                    constants['max_glukose'] = MAX_GLUKOSE_DEFAULT
                    constants['min_glukose'] = MIN_GLUKOSE_DEFAULT

            if (name == 'pain_assessment'):
                try:
                    constants['max_pain'] = params['max']
                    constants['min_pain'] = params['min']
                except Exception as e:
                    constants['max_pain'] = 10
                    constants['min_pain'] = 0

            if (name == 'spo2'):
                try:
                    constants['max_spo2'] = params['max']
                    constants['min_spo2'] = params['min']
                except Exception as e:
                    constants['max_spo2'] = 100
                    constants['min_spo2'] = 93

            if (name == 'waist'):
                try:
                    constants['max_waist'] = params['max']
                    constants['min_waist'] = params['min']
                except Exception as e:
                    constants['max_waist'] = 100
                    constants['min_waist'] = 93

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = (SELECT id FROM measurements WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = 'systolic_pressure') ORDER BY time ASC"

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
            contract_id) + Aux.quote() + " and mr.value < " + Aux.quote() + str(constants['max_systolic']) + Aux.quote() + " and m.name = 'systolic_pressure' GROUP BY m.id"

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

        systolic_dic = {
            "x": array_x,
            "y": array_y,
            "sys_max_value": int(sys_max_value),
            "sys_min_value": int(sys_min_value),
            "sys_avg_value": int(sys_avg_value),
            "sys_slice_normal": int(sys_slice_normal),
            "sys_slice_critical": int(sys_slice_critical),
            "sys_max_week": int(sys_max_week),
            "sys_min_week": int(sys_min_week),
            "sys_avg_week": int(sys_avg_week),
            "sys_slice_normal_week": int(sys_slice_normal_week),
            "sys_slice_critical_week": int(sys_slice_critical_week),
            "sys_max_month": int(sys_max_month),
            "sys_min_month": int(sys_min_month),
            "sys_avg_month": int(sys_avg_month),
            "sys_slice_normal_month": int(sys_slice_normal_month),
            "sys_slice_critical_month": int(sys_slice_critical_month),
            "comments": comments,
            "name": "Верхнее давление"
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
            contract_id) + Aux.quote() + " and mr.value < " + Aux.quote() + str(constants['max_diastolic']) + Aux.quote() + " and m.name = " + Aux.quote() + str(name) + Aux.quote() + " GROUP BY m.id"

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

        diastolic_dic = {
            "x": array_x,
            "y": array_y,
            "dia_max_value": int(dia_max_value),
            "dia_min_value": int(dia_min_value),
            "dia_avg_value": int(dia_avg_value),
            "dia_slice_normal": int(dia_slice_normal),
            "dia_slice_critical": int(dia_slice_critical),
            "dia_max_month": int(dia_max_month),
            "dia_min_month": int(dia_min_month),
            "dia_avg_month": int(dia_avg_month),
            "dia_slice_normal_month": int(dia_slice_normal_month),
            "dia_slice_critical_month": int(dia_slice_critical_month),
            "dia_max_week": int(dia_max_week),
            "dia_min_week": int(dia_min_week),
            "dia_avg_week": int(dia_avg_week),
            "dia_slice_normal_week": int(dia_slice_normal_week),
            "dia_slice_critical_week": int(dia_slice_critical_week),
            "name": "Нижнее давление"
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

        pulse_dic = {
            "x": array_x,
            "y": array_y,
            "name": "Пульс"
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

        pain_assessment_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Оценка боли"
        }

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

        weight_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Вес"
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

        temperature_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Температура"
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

        glukose_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Глюкоза"
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

        spo2_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Мониторинг насыщения крови кислородом"
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

        waist_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Объем талии"
        }

        waist_series = waist_dic

        # shin_left_dic

        param_name = 'shin_volume_left'

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = (SELECT id FROM measurements WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = 'shin_volume_left') ORDER BY time ASC"

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

        shin_left_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Измерение объема голени на левой ноге"
        }

        shin_left = shin_left_dic

        print('shin_left', shin_left)

        # shin_right_dic

        param_name = 'shin_volume_right'

        query_str = "SELECT * FROM measurements_results WHERE measurements_id = (SELECT id FROM measurements WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = 'shin_volume_right') ORDER BY time ASC"

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

        shin_right_dic = {
            "x": array_x,
            "y": array_y,
            "comments": comments,
            "name": "Измерение объема голени на правой ноге"
        }

        shin_right = shin_right_dic

        print('shin_right', shin_right)

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
        print('contract_id', contract_id)
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

    query_str = "SELECT m.name, m.dosage, m.amount, m.id, m.timetable, m.show, m.last_push, m.created_at, m.mode FROM medicines m  WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()
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

    print('measurements', measurements)

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

    if (auth == 'ERROR_KEY'):
        print('/frame ERROR_KEY')
        return ERROR_KEY

    if (auth == 'ERROR_CONTRACT'):
        print('/frame ERROR_CONTRACT')
        return ERROR_CONTRACT

    if(pull == 'shin'):
        constants = {}

        constants['shin_max'] = MAX_SHIN
        constants['shint_min'] = MIN_SHIN

        return render_template('shin.html', tmpl=pull, constants=constants)

    if (pull == 'pressure'):
        constants = {}

        constants['sys_max'] = MAX_SYSTOLIC
        constants['sys_min'] = MIN_SYSTOLIC
        constants['dia_max'] = MAX_DIASTOLIC
        constants['dia_min'] = MIN_DIASTOLIC
        constants['pulse_max'] = MAX_PULSE
        constants['pulse_min'] = MIN_PULSE

        return render_template('pressure.html', tmpl=pull, constants=constants)

    if (pull == 'pain_assessment'):
        return render_template('pain_assessment.html', tmpl=pull)

    if (pull == 'spo2'):
        return render_template('spo2.html', tmpl=pull)

    if (pull == 'waist'):
        return render_template('waist.html', tmpl=pull)

    return render_template('measurement.html', tmpl=pull)


# POST ROUTES

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
            print('measurement', measurement)
            print(Debug.delimiter())

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


@app.route('/init', methods=['POST', 'GET'])
def init():
    new_contract = True

    try:
        data = request.json

        # print('data', data)

        if (data == None):
            print('None')
            return 'None'

        if data['api_key'] != APP_KEY:
            print('invalid key')
            return 'invalid key'

        contract_id = data['contract_id']

        query_str = "SELECT * FROM actual_bots WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()

        records = DB.select(query_str)

        id = 0

        for row in records:
            id = row[1]

        if id > 0:
            new_contract = False
            query_str = "UPDATE actual_bots SET actual = true WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

        if (new_contract == True):
            query_str = "INSERT INTO actual_bots VALUES(nextval('actual_bots$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "true ," + \
                        "(select * from now()), (select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                print('ERROR')
                return result

            # Варианты параметра preset следующие:
            # heartfailure - измерение веса, давления, обхвата талии и голени раз в день;
            # stenocardia или fibrillation - измерение веса, давления раз в день.

            preset = None

            if data['preset']:
                preset = data['preset']

            # print('preset', preset)

            #  *************************************************************** SYS

            params = '{"max_systolic":140,"min_systolic":90,"max_diastolic":90,"min_diastolic":60,"max_pulse":80,"min_pulse":50}'
            timetable = '{"days_month":[{"day":1,"hour":10}],"days_week":[{"day":1,"hour":10}],"hours":[{"value": 10}]}'

            if (preset == 'heartfailure' or preset == 'stenocardia' or preset == 'fibrillation'):
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'systolic_pressure'," + \
                            "'верхнее давление'," + \
                            "'daily'," + \
                            "'мм рт ст'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "true," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

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

                # print('data preset pressure', data)
                delayed(1, post_request, [data])
            else:
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'systolic_pressure'," + \
                            "'верхнее давление'," + \
                            "'daily'," + \
                            "'мм рт ст'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "false," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** DIA

            params = '{}'

            query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "'diastolic_pressure'," + \
                        "'нижнее давление'," + \
                        "'daily'," + \
                        "'мм рт ст'," + \
                        Aux.quote() + params + Aux.quote() + "," + \
                        Aux.quote() + timetable + Aux.quote() + "," + \
                        "false," + \
                        "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** PULSE

            params = '{}'

            query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "'pulse'," + \
                        "'пульс'," + \
                        "'daily'," + \
                        "'уд в мин'," + \
                        Aux.quote() + params + Aux.quote() + "," + \
                        Aux.quote() + timetable + Aux.quote() + "," + \
                        "false," + \
                        "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** TEMPERATURE

            params = '{"max":37,"min":35}'

            query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "'temperature'," + \
                        "'температура'," + \
                        "'daily'," + \
                        "'град'," + \
                        Aux.quote() + params + Aux.quote() + "," + \
                        Aux.quote() + timetable + Aux.quote() + "," + \
                        "false," + \
                        "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** GLUKOSE

            params = '{"max":7,"min":5}'

            query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "'glukose'," + \
                        "'глюкоза'," + \
                        "'daily'," + \
                        "'моль/л'," + \
                        Aux.quote() + params + Aux.quote() + "," + \
                        Aux.quote() + timetable + Aux.quote() + "," + \
                        "false," + \
                        "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** WEIGHT

            params = '{}'

            if (preset == 'heartfailure' or preset == 'stenocardia' or preset == 'fibrillation'):
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'weight'," + \
                            "'вес'," + \
                            "'daily'," + \
                            "'кг'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "true," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

                name = 'weight'

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

                # print('data preset weight', data)
                delayed(1, post_request, [data])
            else:
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'weight'," + \
                            "'вес'," + \
                            "'daily'," + \
                            "'кг'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "false," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** WAIST

            params = '{"max":0,"min":0}'

            if (preset == 'heartfailure'):
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'waist'," + \
                            "'обхват талии для сердечно-сосудистых пациентов'," + \
                            "'daily'," + \
                            "'см'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "true," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

                name = 'waist'

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

                # print('data preset waist', data)
                delayed(1, post_request, [data])
            else:
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'waist'," + \
                            "'обхват талии для сердечно-сосудистых пациентов'," + \
                            "'daily'," + \
                            "'см'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "false," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** SPO2

            params = '{"max":100,"min":93}'

            query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "'spo2'," + \
                        "'мониторинг насыщения крови кислородом'," + \
                        "'daily'," + \
                        "'%'," + \
                        Aux.quote() + params + Aux.quote() + "," + \
                        Aux.quote() + timetable + Aux.quote() + "," + \
                        "false," + \
                        "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** PAIN_ASSESSMENT

            params = '{"max":10,"min":0}'

            query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                        Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                        "'pain_assessment'," + \
                        "'оценка боли'," + \
                        "'daily'," + \
                        "'балл(а)(ов)'," + \
                        Aux.quote() + params + Aux.quote() + "," + \
                        Aux.quote() + timetable + Aux.quote() + "," + \
                        "false," + \
                        "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** SHIN_LEFT

            params = '{"max":35,"min":10}'

            if (preset == 'heartfailure'):
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'shin_volume_left'," + \
                            "'измерение обхвата голени левой'," + \
                            "'daily'," + \
                            "'см'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "true," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

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

                # print('data preset shin', data)
                delayed(1, post_request, [data])
            else:
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'shin_volume_left'," + \
                            "'измерение обхвата голени левой'," + \
                            "'daily'," + \
                            "'см'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable + Aux.quote() + "," + \
                            "false," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** SHIN_RIGHT

            timetable_empty = '{}'
            params = '{}'

            if (preset == 'heartfailure'):
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'shin_volume_right'," + \
                            "'измерение обхвата голени правой'," + \
                            "'daily'," + \
                            "'см'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable_empty + Aux.quote() + "," + \
                            "true," + \
                            "(select * from now()),(select * from now()),(select * from now()))"
            else:
                query_str = "INSERT INTO measurements VALUES(nextval('measurements$id$seq')," + \
                            Aux.quote() + str(contract_id) + Aux.quote() + "," + \
                            "'shin_volume_right'," + \
                            "'измерение обхвата голени правой'," + \
                            "'daily'," + \
                            "'см'," + \
                            Aux.quote() + params + Aux.quote() + "," + \
                            Aux.quote() + timetable_empty + Aux.quote() + "," + \
                            "false," + \
                            "(select * from now()),(select * from now()),(select * from now()))"

            result = DB.query(query_str)

            if (result != 'SUCCESS_QUERY'):
                return result

            # *************************************************************** NEXT MEASUREMENT

    except Exception as e:
        print('error', e)
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
            print('id', id)
            id = row[1]

        if id > 0:
            query_str = "UPDATE actual_bots SET actual = false WHERE contract_id = " + Aux.quote() + str(contract_id) + Aux.quote()

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
            shin_left = Defaults.max_shin_default()
            print('Exception int(shin_left)', e)

        try:
            shin_right = int(shin_right)
        except Exception as e:
            shin_right = Defaults.max_shin_default()
            print('Exception int(shin_right)', e)

        if (shin_left < MIN_SHIN or shin_left > MAX_SHIN):
            return ERROR_OUTSIDE_SHIN

        if (shin_right < MIN_SHIN or shin_right > MAX_SHIN):
            return ERROR_OUTSIDE_SHIN

        query_str = "select params from measurements where contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = 'shin_volume_left'"

        records = DB.select(query_str)

        for row in records:
            params = row[0]

        max_shin = params['max']
        min_shin = params['min']

        try:
            max_shin = int(max_shin)
            min_shin = int(min_shin)
        except Exception as e:
            max_shin = Defaults.max_shin_default()
            min_shin = Defaults.min_shin_default()
            print("WARNING_NOT_INT", e)

        if (shin_left < min_shin or shin_left > max_shin) or (shin_right < min_shin or shin_right > max_shin):
            delayed(1, warning, [contract_id, 'shin', shin_left, shin_right])

        # insert shin_left
        query_str = "select id from measurements where contract_id = " + str(contract_id) + " and name = 'shin_volume_left'"

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(id) + ",(select * from now())," + str(shin_left) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"

        DB.query(query_str)

        delayed(1, add_record, [contract_id, 'leg_circumference_left', shin_left, int(time.time())])

        # insert shin_right
        query_str = "select id from measurements where contract_id = " + str(contract_id) + " and name = 'shin_volume_right'"

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(id) + ",(select * from now())," + str(shin_right) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"

        DB.query(query_str)

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
            return ERROR_OUTSIDE_SYSTOLIC

        if (diastolic < MIN_DIASTOLIC or diastolic > MAX_DIASTOLIC):
            return ERROR_OUTSIDE_DIASTOLIC

        if (pulse_ < MIN_PULSE or pulse_ > MAX_PULSE):
            return ERROR_OUTSIDE_PULSE

        query_str = "select params from measurements where contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = 'systolic_pressure'"

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

        query_str = "select id from measurements where contract_id = " + str(contract_id) + " and name = 'systolic_pressure'"

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(id) + ",(select * from now())," + str(systolic) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"

        DB.query(query_str)

        # add_record(contract_id, 'systolic_pressure', systolic, int(time.time()))

        delayed(1, add_record, [contract_id, 'systolic_pressure', systolic, int(time.time())])

        query_str = "select id from measurements where contract_id = " + str(contract_id) + " and name = 'diastolic_pressure'"

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(id) + ",(select * from now())," + str(diastolic) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"

        DB.query(query_str)

        # add_record(contract_id, 'diastolic_pressure', diastolic, int(time.time()))

        delayed(1, add_record, [contract_id, 'diastolic_pressure', diastolic, int(time.time())])

        query_str = "select id from measurements where contract_id = " + str(contract_id) + " and name = 'pulse'"

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(id) + ",(select * from now())," + str(pulse_) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"

        DB.query(query_str)

        # add_record(contract_id, 'pulse', pulse_, int(time.time()))

        delayed(1, add_record, [contract_id, 'pulse', pulse_, int(time.time())])

    else:
        if check_float(param_value) == False:
            return ERROR_FORM

        query_str = "select params from measurements where contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = " + Aux.quote() + str(pull) + Aux.quote()

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

        if (param == 'spo2' and (param_value < MIN_SPO2 or param_value > MAX_SPO2)):
            return ERROR_OUTSIDE_SPO2

        if (param == 'waist' and (param_value < MIN_WAIST or param_value > MAX_WAIST)):
            return ERROR_OUTSIDE_WAIST

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

        query_str = "select id from measurements where contract_id = " + Aux.quote() + str(contract_id) + Aux.quote() + " and name = " + Aux.quote() + str(pull) + Aux.quote()

        records = DB.select(query_str)

        for row in records:
            id = row[0]

        query_str = "INSERT INTO measurements_results VALUES(nextval('measurements_results$id$seq')," + str(id) + ",(select * from now())," + str(param_value) + ",(select * from now()),(select * from now())," + Aux.quote() + str(comments) + Aux.quote() + ")"

        DB.query(query_str)

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




