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
available_modes = ['daily', 'weekly']

def delayed(delay, f, args):
    timer = threading.Timer(delay, f, args=args)
    timer.start()

def load():
    global contracts
    try:
        with open('data.json', 'r') as f:
            contracts = json.load(f)
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

    return render_template('settings.html', contract=contracts[contract_id])


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

    answer = request.form.get('mode', '')
    min_AD1 = request.form.get('min_AD1', '')
    min_AD2 = request.form.get('min_AD2', '')
    max_AD1 = request.form.get('max_AD1', '')
    max_AD2 = request.form.get('max_AD2', '')

    if answer not in available_modes or False in map(check_digit, [min_AD1, min_AD2, max_AD1, max_AD2]):
        return "<strong>Ошибки при заполнении формы.</strong> Пожалуйста, что все поля заполнены.<br><a onclick='history.go(-1);'>Назад</a>"

    contracts[contract_id]['mode'] = answer
    contracts[contract_id]['min_AD1'] = int(min_AD1)
    contracts[contract_id]['min_AD2'] = int(min_AD2)
    contracts[contract_id]['max_AD1'] = int(max_AD1)
    contracts[contract_id]['max_AD2'] = int(max_AD2)

    print(request.form)
    print(contracts[contract_id])

    save()

    return """
        <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal','*');</script>
        """


def send(contract_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Не забудьте померять давление сегодня.",
            "action_link": "frame",
            "action_name": "Записать давление",
            "only_doctor": False,
        }
    }
    try:
        result = requests.post(MAIN_HOST + '/api/agents/message', json=data)
        contracts[contract_id]['last_push'] = time.time()
        print('sent to ' + contract_id)
    except Exception as e:
        print('connection error', e)

    save()


def send_ban(contract_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Это бан.",
            "forward_to_doctor": False,
            "only_doctor": False,
        }
    }
    try:
        requests.post(MAIN_HOST + '/api/agents/message', json=data)
        print('ban to ' + contract_id)
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
        }
    }

    data2 = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Давление пациента ({} / {}) выходит за допустимый диапазон.".format(a, b),
            "is_urgent": True,
            "only_doctor": True
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
        for contract_id, contract in contracts.items():
            if contract['mode'] == 'daily':
                if time.time() - contract['last_push'] > 60 * 60 * 24:
                    send(contract_id)
            if contract['mode'] == 'weekly':
                if time.time() - contract['last_push'] > 60 * 60 * 24 * 7:
                    send(contract_id)
        time.sleep(60)


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']
    contract_id = str(data['contract_id'])

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заного подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    if "аниме" in data['message']['text'].lower():
        delayed(1, send_ban, [contract_id])

    return "ok"


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
    <strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal','*');</script>
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

    for measurment in contracts[contract_id]['measurements']:
        AD1.append(measurment['AD1'])
        AD2.append(measurment['AD2'])
        PU.append(measurment['PU'])
        t = measurment['time']
        times.append(datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

    return render_template('graph.html', AD1=json.dumps(AD1), AD2=json.dumps(AD2), PU=json.dumps(PU),
                           times=json.dumps(times))


t = Thread(target=sender)
t.start()
if not DEBUG:
    app.run(port='9091', host='0.0.0.0', ssl_context=SSL)
else:
    actions = [{
        "name": "График давления",
        "link": HOST + "/graph"
    }]
    print(json.dumps(actions))
    app.run(port='9091', host='0.0.0.0')
