import datetime
import time
from threading import Thread
from flask import Flask, request, render_template
import json
import requests
import hashlib, uuid
from config import *
import threading

app = Flask(__name__)

contracts = {}
available_modes = ['daily', 'weekly', 'none']


def delayed(delay, f, args):
    timer = threading.Timer(delay, f, args=args)
    timer.start()


def load():
    global contracts
    try:
        with open('data.json', 'r') as f:
            contracts = json.load(f)

        # updater
        for contract in contracts:
            if "medicines" not in contract:
                contract["medicines"] = []
            if "done_medicines" not in contract:
                contract["done_medicines"] = []
            if "last_medicine_sends" not in contract:
                contract["done_medicines"] = {}
    except:
        save()


def save():
    global contracts
    with open('data.json', 'w') as f:
        json.dump(contracts, f)


def check_digit(number):
    try:
        int(number)
        return True
    except:
        return False


load()


@app.route('/init', methods=['POST'])
def init():
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'
    contract_id = str(data['contract_id'])

    contracts[contract_id] = {
        "measurements": [],
        "mode": "daily",
        "min_AD1": 111,
        "max_AD1": 135,
        "min_AD2": 78,
        "max_AD2": 86,
        "medicines": [],
        "done_medicines": [],
        "last_medicine_sends": {},
        "last_push": -1
    }
    save()

    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    data = request.json
    contract_id = str(data['contract_id'])

    if data['api_key'] != APP_KEY:
        return 'invalid key'
    if contract_id not in contracts:
        return "<strong>Ошибка</strong>"

    del contracts[contract_id]
    save()

    return 'ok'


@app.route('/settings', methods=['GET'])
def settings():
    key = request.args.get('api_key', '')
    print(key)
    contract_id = request.args.get('contract_id', '')

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    return render_template('settings.html', contract=contracts[contract_id],
                           medicines_json=json.dumps(contracts[contract_id]['medicines']))


@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/settings', methods=['POST'])
def setting_save():
    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."
    print(request.form)
    data = json.loads(request.form.get('json'))

    answer = data.get('mode', '')
    min_AD1 = data.get('min_AD1', '')
    min_AD2 = data.get('min_AD2', '')
    max_AD1 = data.get('max_AD1', '')
    max_AD2 = data.get('max_AD2', '')

    if answer not in available_modes or False in map(check_digit, [min_AD1, min_AD2, max_AD1, max_AD2]):
        return "<strong>Ошибки при заполнении формы.</strong> Пожалуйста, что все поля заполнены.<br><a onclick='history.go(-1);'>Назад</a>"

    contracts[contract_id]['mode'] = answer
    contracts[contract_id]['medicines'] = data.get('medicines', [])
    contracts[contract_id]['min_AD1'] = int(min_AD1)
    contracts[contract_id]['min_AD2'] = int(min_AD2)
    contracts[contract_id]['max_AD1'] = int(max_AD1)
    contracts[contract_id]['max_AD2'] = int(max_AD2)

    for record in contracts[contract_id]['medicines']:
        if "uid" not in record:
            record["uid"] = str(uuid.uuid4())

    save()

    return "ok"


def send_medicine(contract_id, medicine):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": f"Не забудьте принять лекарство, назначенное врачом: {medicine['name']}.",
            "action_link": f"medicine/{medicine['uid']}",
            "action_name": "Лекарство принято",
            "action_onetime": True,
            "action_deadline": int(time.time()) + 3 * 60 * 60,
            "only_doctor": False,
            "only_patient": True,
        }
    }
    try:
        result = requests.post(MAIN_HOST + '/api/agents/message', json=data)
        print('medicine sent to ' + contract_id)
    except Exception as e:
        print('connection error', e)

    save()


def send(contract_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Не забудьте померить давление сегодня.",
            "action_link": "frame",
            "action_name": "Записать давление",
            "action_onetime": True,
            "only_doctor": False,
            "only_patient": True,
        }
    }
    try:
        result = requests.post(MAIN_HOST + '/api/agents/message', json=data)
        contracts[contract_id]['last_push'] = time.time()
        print('sent to ' + contract_id)
    except Exception as e:
        print('connection error', e)

    save()


def send_warning(contract_id, a, b):
    data1 = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Ваше давление ({} / {}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу.".format(
                a, b),
            "is_urgent": True,
            "only_patient": True,
        }
    }

    data2 = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Давление пациента ({} / {}) выходит за допустимый диапазон.".format(a, b),
            "is_urgent": True,
            "only_doctor": True,
            "need_answer": True
        }
    }
    try:
        print('sending')
        result1 = requests.post(MAIN_HOST + '/api/agents/message', json=data1)
        result1 = requests.post(MAIN_HOST + '/api/agents/message', json=data2)
    except Exception as e:
        print('connection error', e)


def sender():
    while True:
        weekday = datetime.datetime.today().weekday() + 1
        hour = datetime.datetime.today().hour
        for contract_id, contract in contracts.items():
            if contract['mode'] == 'daily':
                if time.time() - contract['last_push'] > 60 * 60 * 24:
                    send(contract_id)
            if contract['mode'] == 'weekly':
                if time.time() - contract['last_push'] > 60 * 60 * 24 * 7:
                    send(contract_id)

            for medicine in contract['medicines']:
                for record in medicine['timetable']:
                    if hour == record['hour'] and weekday == record['day'] and time.time() - contract[
                        'last_medicine_sends'].get(medicine['uid'], 0) > 60 * 60:
                        send_medicine(contract_id, medicine)
                        contract['last_medicine_sends'][medicine['uid']] = int(time.time())
                        save()
        time.sleep(60 * 60)


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']
    contract_id = str(data['contract_id'])

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    return "ok"


@app.route('/medicine/<uid>', methods=['GET'])
def medicine_done(uid):
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    medicines = list(filter(lambda m: m['uid'] == uid, contracts[contract_id]['medicines']))
    if medicines:
        contracts[contract_id]['done_medicines'].append({
            "name": medicines[0]['name'],
            "time": int(time.time())
        })
        save()

    return """
        <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>
        """


@app.route('/frame', methods=['GET'])
def action():
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    return render_template('measurement.html')


@app.route('/frame', methods=['POST'])
def action_save():
    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    answer = {}
    AD1 = request.form.get('AD1', '')
    AD2 = request.form.get('AD2', '')
    PU = request.form.get('PU', '')

    if False in map(check_digit, [AD1, AD2, PU]):
        return "<strong>Ошибки при заполнении формы.</strong> Пожалуйста, что все поля заполнены.<br><a onclick='history.go(-1);'>Назад</a>"
    for param in ['AD1', 'AD2', 'PU']:
        result = request.form.get(param, '')
        answer[param] = int(result)
    answer['time'] = time.time()

    if not (contracts[contract_id]['min_AD1'] <= answer['AD1'] <= contracts[contract_id]['max_AD1'] and
            contracts[contract_id]['min_AD2'] <= answer['AD2'] <= contracts[contract_id]['max_AD2']):
        delayed(1, send_warning, [contract_id, AD1, AD2])

    contracts[contract_id]['measurements'].append(answer)
    save()

    return """
    <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>
    """


@app.route('/graph', methods=['GET'])
def graph():
    contract_id = request.args.get('contract_id', '')
    key = request.args.get('api_key', '')

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    AD1 = []
    AD2 = []
    PU = []
    times = []

    mx = []
    medicines_names = []
    medicines_times = []

    for measurment in contracts[contract_id]['measurements']:
        AD1.append(measurment['AD1'])
        AD2.append(measurment['AD2'])
        PU.append(measurment['PU'])
        t = measurment['time']
        times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

    for medicine in contracts[contract_id]['done_medicines']:
        mx.append(50)
        medicines_names.append(medicine['name'])
        medicines_times.append(datetime.datetime.fromtimestamp(medicine["time"]).strftime("%Y-%m-%d %H:%M:%S"))

    if len(times) > 0:
        end_left = datetime.datetime.fromtimestamp(contracts[contract_id]['measurements'][0]['time'] - 60 * 60 * 12).strftime("%Y-%m-%d %H:%M:%S")
        end_right = datetime.datetime.fromtimestamp(contracts[contract_id]['measurements'][-1]['time'] + 60 * 60 * 12).strftime("%Y-%m-%d %H:%M:%S")
        return render_template('graph.html', AD1=json.dumps(AD1), AD2=json.dumps(AD2), PU=json.dumps(PU),
                               times=json.dumps(times), end_dates=json.dumps([end_left, end_right]),
                               l_level=contracts[contract_id]['min_AD2'], u_level=contracts[contract_id]['max_AD1'],
                               medicines_x=json.dumps(mx), medicines_names=str(medicines_names), medicines_times=json.dumps(medicines_times))
    else:
        return "<strong>Измерений еще не проводилось.</strong>"


t = Thread(target=sender)
t.start()
actions = [{
    "name": "График давления",
    "link": HOST + "/graph"
}]
print(json.dumps(actions))
app.run(port='9091', host='0.0.0.0')
