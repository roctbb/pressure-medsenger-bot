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

medicines_data = []
measurements_data = []
medicines = {}
todos = {}
# contracts = {}

def dump(data, label = ''):
    print('dump: ' + label + ' ', data)

def delayed(delay, f, args):
    print('args', args)
    timer = threading.Timer(delay, f, args=args)
    timer.start()

def load():
    global medicines_data
    global measurements_data
    # global contracts
    global todos

    try:
        # with open('data.json', 'r') as f:
        #     contracts = json.load(f)

        with open('data.json', 'r') as f_test:
            todos = json.load(f_test)

        # save_data()
    except Exception as e:
        print('error load()', e)
        # save_data()

def save_data():
    global todos

    try:
        with open('data.json', 'w', encoding = 'UTF-8') as f:
            json.dump(todos, f, ensure_ascii = False)
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

load()

def  post_request(data, query='/api/agents/message'):
    try:
        print('post request')
        return requests.post(MAIN_HOST + query, json=data)
    except Exception as e:
        print('error post_request', e)

def warning(contract_id, param, param_value, param_value_2 = ''):
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

def sender__():
    # day = 60 * 60 * 24
    # week = 60 * 60 * 24 * 7
    # month = 60 * 60 * 24 * 30
    deadline = 3 * 60 * 60

    while True:
        for todo in todos['contracts']:
            for contract_id in todo:
                measurements_data = todo[contract_id]['measurements']

                for measurement in measurements_data:
                    show = measurement['show']

                    if (show == False):
                        continue

                    timetable = measurement['timetable']
                    mode = measurement.get('mode')
                    measurement_name = measurement['name']
                    last_push = measurement['last_push']

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
                                        # print('Время измерения', b, measurement_name, push_time - control_time)

                                        if control_time > push_time:
                                            data = {
                                                "contract_id": contract_id,
                                                "api_key": APP_KEY,
                                                "message": {
                                                    "text": MESS_MEASUREMENT[measurement_name]['text'],
                                                    "action_link": "frame/" + measurement_name,
                                                    "action_name": MESS_MEASUREMENT[measurement_name]['action_name'],
                                                    "action_onetime": True,
                                                    "only_doctor": False,
                                                    "only_patient": True,
                                                }
                                            }

                                            measurement['last_push'] = current_time
                                            post_request(data)
                                            print('data mesurement weekly', data)

                    if mode == 'daily':
                        for item in timetable:
                            hours = item['hours']
                            # timestamp = datetime.date.today()
                            # print('timestamp', timestamp)

                            for hour in hours:
                                date = datetime.date.fromtimestamp(time.time())
                                a = hour['value']
                                b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)
                                control_time = b.timestamp()
                                current_time = time.time()
                                push_time = last_push

                                # print('1) a, b, control_time, measurement_name', a, b, control_time, measurement_name)

                                diff_current_control = current_time - control_time

                                if diff_current_control > 0:
                                    # print(control_time, 'control_time')
                                    # print(push_time, 'push_time')

                                    if control_time > push_time:
                                        data = {
                                            "contract_id": contract_id,
                                            "api_key": APP_KEY,
                                            "message": {
                                                "text": MESS_MEASUREMENT[measurement_name]['text'],
                                                "action_link": "frame/" + measurement_name,
                                                "action_name": MESS_MEASUREMENT[measurement_name]['action_name'],
                                                "action_onetime": True,
                                                "only_doctor": False,
                                                "only_patient": True,
                                            }
                                        }

                                        measurement['last_push'] = current_time
                                        post_request(data)
                                        print('data', data)

                    save_data()

                medicines_data = todo[contract_id]['medicines']

                for medicine in medicines_data:
                    show = medicine['show']

                    if (show == False):
                        continue

                    medicine_dosage = medicine['dosage']

                    timetable = medicine['timetable']
                    mode = medicine.get('mode')
                    medicine_name = medicine['name']
                    last_sent = medicine['last_sent']

                    if mode == 'weekly':
                        for item in timetable:
                            days_week = item['days_week']

                            for day_hour in days_week:
                                date = datetime.date.fromtimestamp(time.time())
                                day_week = date.today().isoweekday()
                                day_week__ = int(day_hour['day'])

                                # print('day_hour', type(day_week__), type(day_week))

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
                                                    "text": MESS_MEDICINE['text'].format(medicine_name),
                                                    "action_link": MESS_MEDICINE['action_link'].format(medicine['uid']),
                                                    "action_name": MESS_MEDICINE['action_name'].format(medicine_name,
                                                                                                       medicine_dosage),
                                                    "action_onetime": True,
                                                    "action_deadline": int(time.time()) + deadline,
                                                    "only_doctor": False,
                                                    "only_patient": True,
                                                }
                                            }

                                            medicine['last_sent'] = current_time
                                            post_request(data)
                                            print('data medicine weekly', data)

                    if mode == 'daily':
                        for item in timetable:
                            hours = item['hours']

                            for hour in hours:
                                date = datetime.date.fromtimestamp(time.time())
                                a = hour['value']
                                b = datetime.datetime(date.year, date.month, date.day, int(a), 0, 0)

                                # print('Прием лекарств', b, medicine_name)

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
                                                "text": MESS_MEDICINE['text'].format(medicine_name),
                                                "action_link": MESS_MEDICINE['action_link'].format(medicine['uid']),
                                                "action_name": MESS_MEDICINE['action_name'].format(medicine_name,
                                                                                                   medicine_dosage),
                                                "action_onetime": True,
                                                "action_deadline": int(time.time()) + deadline,
                                                "only_doctor": False,
                                                "only_patient": True,
                                            }
                                        }

                                        medicine['last_sent'] = current_time
                                        post_request(data)
                                        print('data medicine', data)

                    save_data()

                    # print('medicines =====================================')

        time.sleep(20)

def quard():
    global todos

    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')

    if key != APP_KEY:
        return 'ERROR_KEY'

    for todo in todos['contracts']:
        if contract_id in todo:
            return contract_id

    return 'ERROR_CONTRACT'

def create_trace(**data):
    trace = {}

    for key, value in data.items():
        if (key == 'x'):
            trace.update(x=value)

        if (key == 'y'):
            trace.update(y=value)

        if (key == 'fill'):
            trace.update(fill=value)

        if (key == 'text'):
            trace.update(text=value)

        if (key == 'type'):
            trace.update(type=value)

        if (key == 'mode'):
            trace.update(mode=value)

        if (key == 'name'):
            trace.update(name=value)

        if (key == 'line'):
            trace.update(line=value)

        if (key == 'marker'):
            trace.update(marker=value)

        if (key == 'opacity'):
            trace.update(opacity=value)

        if (key == 'lot_bgcolor'):
            trace.update(lot_bgcolor=value)

    return trace

@app.route('/settings', methods=['GET'])
def settings():
    global todos
    global medicines_data
    global measurements_data

    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')

    if key != APP_KEY:
        return ERROR_KEY

    quard()

    # if contract_id not in todos['contracts']:
    #     return ERROR_CONTRACT

    for todo in todos['contracts']:
        for tod in todo:
            if (contract_id in todo):
                medicines_data = todo[tod]['medicines']
                measurements_data = todo[tod]['measurements']

    return render_template('settings.html',
        medicines_data=json.dumps(medicines_data),
        measurements_data=json.dumps(measurements_data))

@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'

@app.route('/medicine/<uid>', methods=['GET'])
def medicine_done(uid):
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return ERROR_KEY

    quard()

    # if contract_id not in todos['contracts']:
    #     return ERROR_CONTRACT

    for todo in todos['contracts']:
        if contract_id in todo:
            for medicine in todo[contract_id]['medicines']:
                if uid in medicine['uid']:
                    medicine['times'].append(time.time())

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

    return  MESS_THANKS

@app.route('/graph-test', methods=['GET'])
def graph():
    contract_id = request.args.get('contract_id', '')
    key = request.args.get('api_key', '')

    if key != APP_KEY:
        return ERROR_KEY

    quard()

    # if contract_id not in todos['contracts']:
    #     print('graph-test')
    #     return ERROR_CONTRACT

    constants = {}
    AD1 = []
    AD2 = []
    PU = []
    pulse = []
    glukose = []
    weight = []
    temperature = []
    times = []
    pressure_timestamp = []
    pulse_trace_times = []
    glukose_times = []
    weight_times = []
    glukose_trace_times = []
    weight_trace_times = []
    temperature_trace_times = []
    mx = []
    medicines_x = []
    medicines_x_pulse = []
    medicines_names = []
    medicines_times = []
    medicines_trace_times = []
    medicines_trace_data = {}
    medicines_times_ = []
    max_array = []
    min_array = []
    interval = 60 * 60 * 2
    time_placeholder = "%Y-%m-%d %H:%M:%S"
    max_pulse = ''
    min_pulse = ''
    max_PU = ''
    min_PU = ''
    dosage = []
    amount = []

    for todo in todos['contracts']:
        if contract_id in todo:
            measurements = todo[contract_id]['measurements']
            medicines = todo[contract_id]['medicines']

            # print('measurements', measurements)

            for measurement in measurements:
                if (measurement['name'] == 'pressure'):
                    results = measurement['results']

                    max_AD1 = measurement['max_systolic']
                    min_AD1 = measurement['min_systolic']
                    max_AD2 = measurement['max_diastolic']
                    min_AD2 = measurement['min_diastolic']

                    max_PU = measurement['max_pulse']
                    min_PU = measurement['min_pulse']

                    constants['max_systolic'] = max_AD1
                    constants['min_systolic'] = min_AD1
                    constants['max_diastolic'] = max_AD2
                    constants['min_diastolic'] = min_AD2
                    constants['max_PU'] = max_PU
                    constants['min_PU'] = min_PU

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            AD1.append(result['values']['systolic'])
                            AD2.append(result['values']['diastolic'])
                            PU.append(result['values']['pulse_'])

                            t = result['time']
                            times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))
                            pressure_timestamp.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

                if (measurement['name'] == 'glukose'):
                    results = measurement['results']
                    max_glukose = measurement['max']
                    min_glukose = measurement['min']
                    constants['max_glukose'] = max_glukose
                    constants['min_glukose'] = min_glukose

                    alias = measurement['alias']

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            glukose.append(result['value'])
                            t = result['time']
                            glukose_times.append(t)
                            glukose_trace_times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

                if (measurement['name'] == 'weight'):
                    results = measurement['results']
                    max_weight = measurement['max']
                    min_weight = measurement['min']
                    constants['max_weight'] = max_weight
                    constants['min_weight'] = min_weight

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            weight.append(result['value'])
                            t = result['time']
                            weight_times.append(t)
                            weight_trace_times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

                if (measurement['name'] == 'temperature'):
                    results = measurement['results']
                    constants['max_temperature'] = measurement['max']
                    constants['min_temperature'] = measurement['min']

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            temperature.append(result['value'])
                            temperature_trace_times.append(datetime.datetime.fromtimestamp(result['time']).strftime("%Y-%m-%d %H:%M:%S"))

            # print('medicines', medicines)

            for medicine in medicines:
                # print('medicine', medicine)

                for time__ in medicine['times']:
                    # print('time__', time__)

                    max_array.append(time__)
                    min_array.append(time__)

                    medicines_x.append(40)
                    medicines_x_pulse.append(20)
                    mx.append(medicine['dosage'])
                    medicines_times.append(time__)
                    date_format = datetime.datetime.fromtimestamp(time__).strftime("%Y-%m-%d %H:%M:%S")
                    medicines_trace_times.append(date_format)
                    medicines_times_.append(date_format)

                if (medicine['show'] == True):
                    medicines_names.append(medicine['name'])
                    medicines_trace_data[medicine['name']] = {'medicines_times_': medicines_times_, 'dosage': medicine['dosage'], 'amount': medicine['amount']}

                # print('medicines_times 1', medicines_times)

                medicines_times_ = []

    # print('medicines_trace_times', medicines_trace_times)

    if len(times) > 0 or len(medicines_trace_times) > 0 or len(glukose_trace_times) or len(weight_trace_times) or (temperature_trace_times):
        color_pulse = "#000099"
        color_systolic = "#ff5050"
        color_diastolic = "#0099ff"
        color_medicine = "brown"
        color_glukose = "#336600"
        color_danger = "#F2734C"

        systolic = {
            "x": times,
            "y": AD1,
            "name": "Верхнее давление",
            "type": "scatter",
            "mode": 'lines+markers',
            "line": {
                "color": color_systolic
            },
            'marker': {
                'size': 8
            }
        }

        diastolic = {
            "x": times,
            "y": AD2,
            "name": "Нижнее давление",
            "type": "scatter",
            "mode": 'lines+markers',
            "line": {"color": color_diastolic},
            'marker': {
                'size': 8
            }
        }

        pulse_ = {
            "x": times,
            "y": PU,
            "name": "Пульс",
            "type": "scatter",
            "mode": 'lines+markers',
            "line": {
                "dash": "dot",
                "color": color_pulse
            },
            'marker': {
                'size': 8
            }
        }

        trace_medicines = {
            "x": medicines_trace_times,
            "y": mx,
            "text": medicines_names,
            "dosage": dosage,
            "amount": amount,
            "type": 'skatter',
            "mode": 'markers',
            "lot_bgcolor": "rgba(200,255,0,0.1)",
            "line": {"color": color_medicine},
            "marker": {"size": 26},
            "name": 'Лекарства'
        }

        # Формирование данных по измерению веса

        weight_series = {
            "x": weight_trace_times,
            "y": weight,
            "name": 'Вес'
        }

        # Формирование данных по измерению температуры

        temperature_series = {
            "x": temperature_trace_times,
            "y": temperature,
            "name": 'Температура'
        }

        # Формирование данных по уровню глюкозы

        glukose_series = {
            "x": glukose_trace_times,
            "y": glukose,
            "name": "Глюкоза"
        }

        return render_template('graph-test.html',
                               constants=constants,
                               systolic=systolic,
                               diastolic=diastolic,
                               pulse_=pulse_,
                               glukose=glukose_series,
                               weight=weight_series,
                               temperature=temperature_series,
                               medicine=trace_medicines,
                               medicine_trace_data=medicines_trace_data
                               )
    else:
        return "<strong>Измерений еще не проводилось.</strong>"

    return "ok"

@app.route('/graph', methods=['GET'])
def graph_test():
    contract_id = request.args.get('contract_id', '')
    key = request.args.get('api_key', '')

    if key != APP_KEY:
        return ERROR_KEY

    quard()

    # if contract_id not in todos['contracts']:
    #     print('graph-test')
    #     return ERROR_CONTRACT

    constants = {}
    AD1 = []
    AD2 = []
    PU = []
    pulse = []
    glukose = []
    weight = []
    temperature = []
    times = []
    pressure_timestamp = []
    pulse_trace_times = []
    glukose_times = []
    weight_times = []
    glukose_trace_times = []
    weight_trace_times = []
    temperature_trace_times = []
    mx = []
    medicines_x = []
    medicines_x_pulse = []
    medicines_names = []
    medicines_times = []
    medicines_trace_times = []
    medicines_trace_data = {}
    medicines_times_ = []
    max_array = []
    min_array = []
    interval = 60 * 60 * 2
    time_placeholder = "%Y-%m-%d %H:%M:%S"
    max_pulse = ''
    min_pulse = ''
    max_PU = ''
    min_PU = ''
    dosage = []
    amount = []

    for todo in todos['contracts']:
        if contract_id in todo:
            measurements = todo[contract_id]['measurements']
            medicines = todo[contract_id]['medicines']

            # print('measurements', measurements)

            for measurement in measurements:
                if (measurement['name'] == 'pressure'):
                    results = measurement['results']

                    max_AD1 = measurement['max_systolic']
                    min_AD1 = measurement['min_systolic']
                    max_AD2 = measurement['max_diastolic']
                    min_AD2 = measurement['min_diastolic']

                    max_PU = measurement['max_pulse']
                    min_PU = measurement['min_pulse']

                    constants['max_systolic'] = max_AD1
                    constants['min_systolic'] = min_AD1
                    constants['max_diastolic'] = max_AD2
                    constants['min_diastolic'] = min_AD2
                    constants['max_PU'] = max_PU
                    constants['min_PU'] = min_PU

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            AD1.append(result['values']['systolic'])
                            AD2.append(result['values']['diastolic'])
                            PU.append(result['values']['pulse_'])

                            t = result['time']
                            times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))
                            pressure_timestamp.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

                if (measurement['name'] == 'glukose'):
                    results = measurement['results']
                    max_glukose = measurement['max']
                    min_glukose = measurement['min']
                    constants['max_glukose'] = max_glukose
                    constants['min_glukose'] = min_glukose

                    alias = measurement['alias']

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            glukose.append(result['value'])
                            t = result['time']
                            glukose_times.append(t)
                            glukose_trace_times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

                if (measurement['name'] == 'weight'):
                    results = measurement['results']
                    max_weight = measurement['max']
                    min_weight = measurement['min']
                    constants['max_weight'] = max_weight
                    constants['min_weight'] = min_weight

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            weight.append(result['value'])
                            t = result['time']
                            weight_times.append(t)
                            weight_trace_times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

                if (measurement['name'] == 'temperature'):
                    results = measurement['results']
                    constants['max_temperature'] = measurement['max']
                    constants['min_temperature'] = measurement['min']

                    if (results):
                        max_array.append(results[-1]['time'])
                        min_array.append(results[0]['time'])

                        for result in results:
                            temperature.append(result['value'])
                            temperature_trace_times.append(datetime.datetime.fromtimestamp(result['time']).strftime("%Y-%m-%d %H:%M:%S"))

            # print('medicines', medicines)

            for medicine in medicines:
                # print('medicine', medicine)

                for time__ in medicine['times']:
                    # print('time__', time__)

                    max_array.append(time__)
                    min_array.append(time__)

                    medicines_x.append(40)
                    medicines_x_pulse.append(20)
                    mx.append(medicine['dosage'])
                    medicines_times.append(time__)
                    date_format = datetime.datetime.fromtimestamp(time__).strftime("%Y-%m-%d %H:%M:%S")
                    medicines_trace_times.append(date_format)
                    medicines_times_.append(date_format)

                if (medicine['show'] == True):
                    medicines_names.append(medicine['name'])
                    medicines_trace_data[medicine['name']] = {'medicines_times_': medicines_times_, 'dosage': medicine['dosage'], 'amount': medicine['amount']}

                # print('medicines_times 1', medicines_times)

                medicines_times_ = []

    # print('medicines_trace_times', medicines_trace_times)

    if len(times) > 0 or len(medicines_trace_times) > 0 or len(glukose_trace_times) or len(weight_trace_times) or (temperature_trace_times):
        color_pulse = "#000099"
        color_systolic = "#ff5050"
        color_diastolic = "#0099ff"
        color_medicine = "brown"
        color_glukose = "#336600"
        color_danger = "#F2734C"

        systolic = {
            "x": times,
            "y": AD1,
            "name": "Верхнее давление",
            "type": "scatter",
            "mode": 'lines+markers',
            "line": {
                "color": color_systolic
            },
            'marker': {
                'size': 8
            }
        }

        diastolic = {
            "x": times,
            "y": AD2,
            "name": "Нижнее давление",
            "type": "scatter",
            "mode": 'lines+markers',
            "line": {"color": color_diastolic},
            'marker': {
                'size': 8
            }
        }

        pulse_ = {
            "x": times,
            "y": PU,
            "name": "Пульс",
            "type": "scatter",
            "mode": 'lines+markers',
            "line": {
                "dash": "dot",
                "color": color_pulse
            },
            'marker': {
                'size': 8
            }
        }

        trace_medicines = {
            "x": medicines_trace_times,
            "y": mx,
            "text": medicines_names,
            "dosage": dosage,
            "amount": amount,
            "type": 'skatter',
            "mode": 'markers',
            "lot_bgcolor": "rgba(200,255,0,0.1)",
            "line": {"color": color_medicine},
            "marker": {"size": 26},
            "name": 'Лекарства'
        }

        # Формирование данных по измерению веса

        weight_series = {
            "x": weight_trace_times,
            "y": weight,
            "name": 'Вес'
        }

        # Формирование данных по измерению температуры

        temperature_series = {
            "x": temperature_trace_times,
            "y": temperature,
            "name": 'Температура'
        }

        # Формирование данных по уровню глюкозы

        glukose_series = {
            "x": glukose_trace_times,
            "y": glukose,
            "name": "Глюкоза"
        }

        return render_template('graph-test.html',
                               constants=constants,
                               systolic=systolic,
                               diastolic=diastolic,
                               pulse_=pulse_,
                               glukose=glukose_series,
                               weight=weight_series,
                               temperature=temperature_series,
                               medicine=trace_medicines,
                               medicine_trace_data=medicines_trace_data
                               )
    else:
        return "<strong>Измерений еще не проводилось.</strong>"

    return "ok"

@app.route('/frame/<string:pull>', methods=['GET'])
def action_pull(pull):
    auth = quard()

    if (auth == 'ERROR_KEY'):
        return ERROR_KEY

    if (auth == 'ERROR_CONTRACT'):
        print('2')
        return ERROR_CONTRACT

    return render_template('measurement.html', tmpl=pull)

# POST ROUTES

@app.route('/settings', methods=['POST'])
def setting_save():
    global todos

    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')

    if key != APP_KEY:
        return ERROR_KEY

    quard()

    # if contract_id not in todos['contracts']:
    #     return ERROR_CONTRACT
    
    data = json.loads(request.form.get('json'))

    for todo in todos['contracts']:
        if contract_id in todo:
            todo[contract_id]['medicines'] = data.get('medicines_data', [])
            todo[contract_id]['measurements'] = data.get('measurements_data', [])

    for todo in todos['contracts']:
        if contract_id in todo:
            for medicine in todo[contract_id]['medicines']:
                if "uid" not in medicine:
                    medicine['uid'] = str(uuid.uuid4())

                if "created_at" not in medicine:
                    medicine['created_at'] = time.time()

    # save()
    save_data()

    return "ok"

@app.route('/init', methods=['POST'])
def init():
    global todos

    new_contract = True
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    contract_id = str(data['contract_id'])

    for todo in todos['contracts']:
        if contract_id in todo:
            new_contract = False

            todo[contract_id]['actual'] = True
            break

    if (new_contract == True):
        contract_item = {
            contract_id: {
                "measurements": [
                    {
                        "name": "pressure",
                        "alias": "Давление",
                        "mode": "daily",
                        "max_systolic": 130,
                        "min_systolic": 110,
                        "max_diastolic": 90,
                        "min_diastolic": 70,
                        "max_pulse": 90,
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
                        "max": 79,
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
                        "max": 43,
                        "min": 32,
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
        }
        todos['contracts'].append(contract_item)

    save_data()

    return 'ok'

@app.route('/remove', methods=['POST'])
def remove():
    global todos

    data = request.json
    contract_id = str(data['contract_id'])

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    quard()

    # if contract_id not in todos['contracts']:
    #     return "<strong>Ошибка</strong>"

    for todo in todos['contracts']:
        if contract_id in todo:
            todo[contract_id]['actual'] = False
            break

    # save()
    save_data()

    return 'ok'

@app.route('/frame/<string:pull>', methods=['POST'])
def action_pull_save(pull):
    print('action_pull_save()', pull)

    param = ''
    param_value = ''
    contract_id = quard()

    if (contract_id == 'ERROR_KEY'):
        return ERROR_KEY

    if (contract_id == 'ERROR_CONTRACT'):
        print('4')
        return ERROR_CONTRACT

    if (pull in AVAILABLE_MEASUREMENTS):
        param = pull
        param_value = request.form.get(param, '')

    for todo in todos['contracts']:
        if contract_id in todo:
            for measurement in todo[contract_id]['measurements']:
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

                        if not (min_systolic <= int(systolic) <= max_systolic and min_diastolic <= int(diastolic) <= max_diastolic):
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
                                # print('param_value before', param_value)

                                if (param != 'glukose') and (param != 'temperature'):
                                    param_value = int(param_value)

                                    if check_int(param_value) == False:
                                        return ERROR_FORM

                                    # print('param_value after', param_value)

                                delayed(1, warning, [contract_id, param, param_value])
                                # print('not pressure', param, param_value)
                            answer['time'] = time.time()
                            answer['value'] = param_value

                            measurement['results'].append(answer)
                    save_data()

                    break

    return MESS_THANKS

@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']
    contract_id = str(data['contract_id'])

    if key != APP_KEY:
        return ERROR_KEY

    quard()

    #
    # if contract_id not in todos['contracts']:
    #     return ERROR_CONTRACT
    
    return "ok"

t__ = Thread(target=sender__)
t__.start()

# t = Thread(target=sender)
# t.start()
actions = [{
    "name": "График давления",
    "link": HOST + "/graph"
}]
# print('json.dumps', json.dumps(actions))
app.run(port='9091', host='0.0.0.0')
