import datetime
import time
from threading import Thread
from flask import Flask, request, render_template
import json
import requests
import uuid
from config import *
from const import *
import threading

app = Flask(__name__)

file_name = 'data.json'
data = {}
contracts = []
medicines = []
measurements = []

def dump(data, label):
    print('dump: ' + label + ' ', data)

def delayed(delay, f, args):
    print('args', args)
    timer = threading.Timer(delay, f, args=args)
    timer.start()

def load():
    global data
    global medicines_data
    global measurements_data
    global medicines
    global measurements
    global contracts

    try:
        with open(file_name, 'r') as f:
            data = json.load(f)

        contracts = data['contracts']
    except Exception as e:
        print('error load()', e)

def save_data():
    global contracts

    try:
        with open(file_name, 'w', encoding='UTF-8') as f_w:
            data['contracts'] = contracts
            json.dump(data, f_w, ensure_ascii=False)
    except Exception as e:
        print('error save_data()', e)

def check_int(number):
    try:
        int(number)
        return True
    except:
        return False

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

def post_request(data, query='/api/agents/message'):
    try:
        print('post request')
        return requests.post(MAIN_HOST + query, json=data)
    except Exception as e:
        print('error post_request', e)

def warning(contract_id, param, param_value, param_value_2=''):
    text_patient = ''
    text_doctor = ''

    if (param in AVAILABLE_MEASUREMENTS):
        if (param == 'pressure'):
            text_patient = MESS_PRESSURE_PATIENT.format(
                param_value, param_value_2)
            text_doctor = MESS_PRESSURE_DOCTOR.format(
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

def sender():
    global contracts
    global measurements

    deadline = 3 * 60 * 60

    while True:
        for contract in contracts:
            medicines = contract['medicines']
            measurements = contract['measurements']
            contract_id = contract['id']

            for measurement in measurements:
                show = measurement['show']

                if (show == False):
                    continue

                timetable = measurement['timetable']
                mode = measurement['mode']
                name = measurement['name']
                last_push = measurement['last_push']

                if mode == 'daily':
                    for item in timetable:
                        hours = item['hours']

                        for hour in hours:
                            date = datetime.date.fromtimestamp(time.time())
                            a = hour['value']
                            b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)
                            control_time = b.timestamp()
                            current_time = time.time()
                            push_time = last_push
                            diff_current_control = current_time - control_time

                            if diff_current_control > 0:
                                if control_time > push_time:
                                    data = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "message": {
                                            "text": MESS_MEASUREMENT[name]['text'],
                                            "action_link": "frame/" + name,
                                            "action_name": MESS_MEASUREMENT[name]['action_name'],
                                            "action_onetime": True,
                                            "only_doctor": False,
                                            "only_patient": True,
                                        }
                                    }

                                    measurement['last_push'] = current_time
                                    post_request(data)

                if mode == 'weekly':
                    for item in timetable:
                        days_week = item['days_week']

                        for day_hour in days_week:
                            date = datetime.date.fromtimestamp(time.time())
                            day_week = date.today().isoweekday()
                            day_week__ = int(day_hour['day'])

                            if day_week__ == day_week:
                                a = day_hour['hour']
                                b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)

                                control_time = b.timestamp()
                                current_time = time.time()
                                push_time = last_push
                                diff_current_control = current_time - control_time

                                if diff_current_control > 0:
                                    if control_time > push_time:
                                        data = {
                                            "contract_id": contract_id,
                                            "api_key": APP_KEY,
                                            "message": {
                                                "text": MESS_MEASUREMENT[name]['text'],
                                                "action_link": "frame/" + name,
                                                "action_name": MESS_MEASUREMENT[name]['action_name'],
                                                "action_onetime": True,
                                                "only_doctor": False,
                                                "only_patient": True,
                                            }
                                        }

                                        measurement['last_push'] = current_time
                                        post_request(data)

                save_data()

            for medicine in medicines:
                show = medicine['show']

                if (show == False):
                    continue

                name = medicine['name']
                mode = medicine.get('mode')
                last_sent = medicine['last_sent']
                medicine_dosage = medicine['dosage']
                timetable = medicine['timetable']

                if mode == 'daily':
                    for item in timetable:
                        hours = item['hours']

                        for hour in hours:
                            date = datetime.date.fromtimestamp(time.time())
                            a = hour['value']
                            b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)

                            control_time = b.timestamp()
                            current_time = time.time()
                            push_time = last_sent
                            diff_current_control = current_time - control_time

                            if diff_current_control > 0:
                                if control_time > push_time:
                                    data = {
                                        "contract_id": contract_id,
                                        "api_key": APP_KEY,
                                        "message": {
                                            "text": MESS_MEDICINE['text'].format(name),
                                            "action_link": MESS_MEDICINE['action_link'].format(medicine['uid']),
                                            "action_name": MESS_MEDICINE['action_name'].format(name, medicine_dosage),
                                            "action_onetime": True,
                                            "action_deadline": int(time.time()) + deadline,
                                            "only_doctor": False,
                                            "only_patient": True,
                                        }
                                    }

                                    medicine['last_sent'] = current_time
                                    post_request(data)

                if mode == 'weekly':
                    for item in timetable:
                        days_week = item['days_week']

                        for day_hour in days_week:
                            date = datetime.date.fromtimestamp(time.time())
                            day_week = date.today().isoweekday()
                            day_week__ = int(day_hour['day'])

                            if day_week__ == day_week:
                                a = day_hour['hour']
                                b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)
                                control_time = b.timestamp()
                                current_time = time.time()
                                push_time = last_sent
                                diff_current_control = current_time - control_time

                                if diff_current_control > 0:
                                    if control_time > push_time:
                                        data = {
                                            "contract_id": contract_id,
                                            "api_key": APP_KEY,
                                            "message": {
                                                "text": MESS_MEDICINE['text'].format(name),
                                                "action_link": MESS_MEDICINE['action_link'].format(
                                                    medicine['uid']),
                                                "action_name": MESS_MEDICINE['action_name'].format(
                                                    name, medicine_dosage),
                                                "action_onetime": True,
                                                "action_deadline": int(time.time()) + deadline,
                                                "only_doctor": False,
                                                "only_patient": True,
                                            }
                                        }

                                        medicine['last_sent'] = current_time
                                        post_request(data)

                save_data()

        time.sleep(10)

def quard():
    global contracts

    key = request.args.get('api_key', '')
    contract_id = int(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return 'ERROR_KEY'

    for contract in contracts:
        if (contract_id == int(contract['id'])):
            return contract_id

    return 'ERROR_CONTRACT'

load()

# GET ROUTES

@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'

@app.route('/graph', methods=['GET'])
def graph():
    global contracts

    contract_id = quard()
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

    for contract in contracts:
        medicines = contract['medicines']
        measurements = contract['measurements']

        if (contract_id == int(contract['id'])):
            for measurement in measurements:
                name = measurement['name']

                if (name == 'pressure'):
                    results = measurement['results']

                    constants['max_systolic'] = measurement['max_systolic']
                    constants['min_systolic'] = measurement['min_systolic']
                    constants['max_diastolic'] = measurement['max_diastolic']
                    constants['min_diastolic'] = measurement['min_diastolic']
                    constants['max_pulse'] = measurement['max_pulse']
                    constants['min_pulse'] = measurement['min_pulse']

                    if (results):
                        for result in results:
                            systolic.append(result['values']['systolic'])
                            diastolic.append(result['values']['diastolic'])
                            pulse.append(result['values']['pulse_'])

                            t = result['time']
                            times.append(datetime.datetime.fromtimestamp(t).strftime(time_placeholder))
                            pressure_timestamp.append(datetime.datetime.fromtimestamp(t).strftime(time_placeholder))

                if (name != 'pressure'):

                    results = measurement['results']

                    if (name == 'glukose'):
                        constants['max_glukose'] = measurement['max']
                        constants['min_glukose'] = measurement['min']

                        if (results):
                            for result in results:
                                glukose.append(result['value'])
                                t = result['time']

                                glukose_trace_times.append(
                                    datetime.datetime.fromtimestamp(t).strftime(time_placeholder))

                    if (name == 'weight'):
                        constants['max_weight'] = measurement['max']
                        constants['min_weight'] = measurement['min']

                        if (results):
                            for result in results:
                                weight.append(result['value'])
                                t = result['time']

                                weight_trace_times.append(datetime.datetime.fromtimestamp(t).strftime(time_placeholder))

                    if (name == 'temperature'):
                        constants['max_' + name] = measurement['max']
                        constants['min_' + name] = measurement['min']

                        if (results):
                            for result in results:
                                temperature.append(result['value'])
                                t = result['time']

                                temperature_trace_times.append(datetime.datetime.fromtimestamp(t).strftime(time_placeholder))

            for medicine in medicines:
                for time__ in medicine['times']:
                    date_format = datetime.datetime.fromtimestamp(time__).strftime(time_placeholder)
                    medicines_trace_times.append(date_format)
                    medicines_times_.append(date_format)

                if (medicine['show'] == True):
                    medicines_names.append(medicine['name'])
                    medicines_trace_data[medicine['name']] = {'medicines_times_': medicines_times_,
                                                              'dosage': medicine['dosage'],
                                                              'amount': medicine['amount']}

                medicines_times_ = []

    if len(times) > 0 or len(medicines_trace_times) > 0 or len(glukose_trace_times) or len(weight_trace_times) or (
    temperature_trace_times):
        systolic = {
            "x": times,
            "y": systolic,
            "name": "Верхнее давление"
        }

        diastolic = {
            "x": times,
            "y": diastolic,
            "name": "Нижнее давление"
        }

        pulse = {
            "x": times,
            "y": pulse,
            "name": "Пульс"
        }

        medicine = {
            "x": medicines_trace_times,
            "y": [],
            "text": medicines_names,
            "dosage": dosage,
            "amount": amount,
            "name": 'Лекарства',
            "medicines_data": medicines_trace_data

        }

        weight_series = {
            "x": weight_trace_times,
            "y": weight,
            "name": 'Вес'
        }

        temperature_series = {
            "x": temperature_trace_times,
            "y": temperature,
            "name": 'Температура'
        }

        glukose_series = {
            "x": glukose_trace_times,
            "y": glukose,
            "name": "Глюкоза"
        }

        return render_template('graph.html',
                               constants=constants,
                               systolic=systolic,
                               diastolic=diastolic,
                               pulse_=pulse,
                               glukose=glukose_series,
                               weight=weight_series,
                               temperature=temperature_series,
                               medicine=medicine,
                               medicine_trace_data=medicines_trace_data
                               )
    else:
        return NONE_MEASUREMENTS

    return "ok"

@app.route('/settings', methods=['GET'])
def settings():
    global contracts

    contract_id = quard()

    if (contract_id == ERROR_KEY):
        return ERROR_KEY

    if (contract_id == ERROR_CONTRACT):
        return ERROR_CONTRACT

    for contract in contracts:
        if (contract_id == int(contract['id'])):
            medicines = contract['medicines']
            measurements = contract['measurements']
            break

    return render_template('settings.html',
                           medicines_data=json.dumps(medicines),
                           measurements_data=json.dumps(measurements))

@app.route('/medicine/<uid>', methods=['GET'])
def medicine_done(uid):
    print('medicine_done(uid)', uid)

    global contracts

    contract_id = quard()

    if contract_id in ERRORS:
        return contract_id

    for contract in contracts:
        if contract_id == int(contract['id']):
            for medicine in contract['medicines']:
                if uid in medicine['uid']:
                    medicine['times'].append(time.time())
                    break

    save_data()

    # medicines = list(filter(lambda m: m['uid'] == uid, contracts[contract_id]['medicines']))
    #
    # if medicines:
    #     contracts[contract_id]['done_medicines'].append({
    #         "name": medicines[0]['name'],
    #         "time": int(time.time())
    #     })
    #     save()

    # return """
    #     <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>
    #     """

    return MESS_THANKS

@app.route('/frame/<string:pull>', methods=['GET'])
def action_pull(pull):
    auth = quard()

    if (auth == 'ERROR_KEY'):
        return ERROR_KEY

    if (auth == 'ERROR_CONTRACT'):
        return ERROR_CONTRACT

    return render_template('measurement.html', tmpl=pull)

# POST ROUTES

@app.route('/settings', methods=['POST'])
def setting_save():
    global contracts

    contract_id = quard()

    if contract_id in ERRORS:
        return contract_id

    # data = json.loads(request.json['json'])
    data = json.loads(request.form.get('json'))

    for contract in contracts:
        if contract_id == int(contract['id']):
            contract['medicines'] = data['medicines_data']
            contract['measurements'] = data['measurements_data']

            for medicine in contract['medicines']:
                if "uid" not in medicine:
                    medicine['uid'] = str(uuid.uuid4())

                if "created_at" not in medicine:
                    medicine['created_at'] = time.time()

    save_data()

    return "ok"

@app.route('/init', methods=['POST'])
def init():
    global contracts

    new_contract = True

    try:
        data = request.json

        if (data == None):
            return 'None'

        if data['api_key'] != APP_KEY:
            return 'invalid key'

        contract_id = int(data['contract_id'])

        for contract in contracts:
            if contract_id == int(contract['id']):
                new_contract = False

                contract['actual'] = True
                break

        if (new_contract == True):
            contract = {
                "id": contract_id,
                "measurements": [
                    {
                        "name": "pressure",
                        "alias": "Давление",
                        "mode": "daily",
                        "max_systolic": 140,
                        "min_systolic": 90,
                        "max_diastolic": 100,
                        "min_diastolic": 30,
                        "max_pulse": 80,
                        "min_pulse": 50,
                        "last_push": -1,
                        "timetable": [
                            {
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
                        ],
                        "results": [],
                        "show": False
                    },
                    {
                        "name": "weight",
                        "alias": "Вес",
                        "mode": "daily",
                        "max": 100,
                        "min": 50,
                        "last_push": -1,
                        "timetable": [
                            {
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
                        ],
                        "results": [],
                        "show": False
                    },
                    {
                        "name": "temperature",
                        "alias": "Температура",
                        "mode": "daily",
                        "max": 37,
                        "min": 36,
                        "last_push": -1,
                        "timetable": [
                            {
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
                        ],
                        "results": [],
                        "show": False
                    },
                    {
                        "name": "glukose",
                        "alias": "Глюкоза",
                        "mode": "daily",
                        "max": 6.5,
                        "min": 4,
                        "last_push": -1,
                        "timetable": [
                            {
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
                        ],
                        "results": [],
                        "show": False
                    }
                ],
                "medicines": [],
                "actual": True
            }

            contracts.append(contract)

    except Exception as e:
        print('error', e)

    save_data()

    return 'ok'

@app.route('/remove', methods=['POST'])
def remove():
    global contracts


    data = request.json
    contract_id = str(data['contract_id'])

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    # quard()

    for contract in contracts:
        if contract_id == int(contract['id']):
            contract['actual'] = False
            break

    save_data()

    return 'ok'

@app.route('/frame/<string:pull>', methods=['POST'])
def action_pull_save(pull):
    param = ''
    param_value = ''
    contract_id = quard()

    if (contract_id in ERRORS):
        return contract_id

    if (pull in AVAILABLE_MEASUREMENTS):
        param = pull
        param_value = request.form.get(param, '')

    for contract in contracts:
        if contract_id == int(contract['id']):
            for measurement in contract['measurements']:
                measurement_name = measurement['name']

                if (pull in measurement_name):
                    if (measurement_name == 'pressure'):
                        answer = {}
                        systolic = request.form.get('systolic', '')
                        diastolic = request.form.get('diastolic', '')
                        pulse_ = request.form.get('pulse_', '')

                        if False in map(check_digit, [systolic, diastolic, pulse_]):
                            return ERROR_FORM

                        systolic = int(systolic)
                        diastolic = int(diastolic)
                        pulse_ = int(pulse_)
                        max_systolic = int(measurement['max_systolic'])
                        min_systolic = int(measurement['min_systolic'])
                        max_diastolic = int(measurement['max_diastolic'])
                        min_diastolic = int(measurement['min_diastolic'])

                        if not (min_systolic <= int(systolic) <= max_systolic and min_diastolic <= int(
                                diastolic) <= max_diastolic):
                            delayed(1, warning, [contract_id, 'pressure', systolic, diastolic])

                        answer['time'] = time.time()
                        answer['values'] = {'systolic': systolic, 'diastolic': diastolic, 'pulse_': pulse_}
                        measurement['results'].append(answer)
                    else:
                        if check_float(param_value) == False:
                            return ERROR_FORM

                        answer = {}
                        max = float(measurement['max'])
                        min = float(measurement['min'])
                        param_value = float(param_value)

                        if param in measurement['name']:
                            if not (min <= param_value <= max):
                                if (param != 'glukose') and (param != 'temperature'):
                                    param_value = int(param_value)

                                    if check_int(param_value) == False:
                                        return ERROR_FORM

                                delayed(1, warning, [contract_id, param, param_value])

                            answer['time'] = time.time()
                            answer['value'] = param_value
                            measurement['results'].append(answer)

                    save_data()

                    break

    return MESS_THANKS

@app.route('/message', methods=['POST'])
def save_message():
    global contracts

    data = request.json
    key = data['api_key']
    # contract_id = str(data['contract_id'])

    if key != APP_KEY:
        return ERROR_KEY

    return "ok"

t = Thread(target=sender)
t.start()

app.run(port='9091', host='0.0.0.0')