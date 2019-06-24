import datetime
import time
from threading import Thread
from flask import Flask, request, render_template
import json
import requests
import hashlib, uuid
from config import *

app = Flask(__name__)

contracts = {}
available_modes = ['daily', 'weekly']


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


def get_key():
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((APP_KEY + salt).encode('utf8')).hexdigest()
    return str(hashed_password)


def check_digit(number):
    try:
        float(number)
        return True
    except:
        return False


load()


@app.route('/init', methods=['POST'])
def init():
    data = request.json

    if data['key'] != APP_KEY:
        return 'invalid key'
    contract_id = str(data['contract'])

    contracts[contract_id] = {
        "measurements": [],
        "mode": "daily",
        "requests": {},
        "last_push": -1
    }
    save()

    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    data = request.json
    contract_id = str(data['contract'])

    if data['key'] != APP_KEY:
        return 'invalid key'
    if contract_id not in contracts:
        return "<strong>Ошибка</strong>"

    del contracts[contract_id]
    save()

    return 'ok'


@app.route('/settings', methods=['GET'])
def settings():
    key = request.args.get('key', '')
    contract_id = request.args.get('contract', '')

    if key != APP_KEY:
        return "<strong>Ошибка</strong>"
    if contract_id not in contracts:
        print(contracts)
        print(contract_id)
        return "<strong>Ошибка not in contracts</strong>"

    current_mode = contracts[contract_id]['mode']

    return render_template('settings.html', current_mode=current_mode)

@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'

@app.route('/settings', methods=['POST'])
def setting_save():
    key = request.args.get('key', '')
    contract_id = request.args.get('contract', '')

    if key != APP_KEY:
        return "<strong>Ошибка</strong>"
    if contract_id not in contracts:
        return "<strong>Ошибка</strong>"

    answer = request.form.get('mode', '')

    if answer == '':
        return "<strong>Заполните форму</strong><br><a onclick='history.go(-1);'>Назад</a>"

    if answer not in available_modes:
        return "<strong>Ошибка</strong>"

    contracts[contract_id]['mode'] = answer

    save()

    return 'ok'


def send(contract_id):
    check_key = get_key()
    contracts[contract_id]['requests'][check_key] = time.time()

    data = {
        "contract": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": "Не забудьте померять давление сегодня.",
            "action_link": HOST + "/frame?key={}&contract={}".format(check_key,
                                                                                   contract_id),
            "action_name": "Записать давление"
        }
    }
    try:
        result = requests.post(HOST + '/api/agents/message', json=data)
        contracts[contract_id]['last_push'] = time.time()
        print('sent to ' + contract_id)
    except:
        print('connection error')

    save()


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

@app.route('/debug_getlink', methods=['GET'])
def debug_getlink():
    contract_id = list(contracts.keys())[0]
    check_key = get_key()
    contracts[contract_id]['requests'][check_key] = time.time()
    return HOST + "/frame?key={}&contract={}".format(check_key, contract_id)


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['key']
    contract_id = str(data['contract'])

    if key != APP_KEY:
        print('invalid key')
        return "<strong>Ошибка</strong>"
    if contract_id not in contracts:
        print('invalid contract')
        return "<strong>Ошибка</strong>"
    """
    text = data['message']['text']

    for word in contracts[contract_id]['keywords']:
        if word in text.lower():
            data = {
                "contract": data['contract'],
                "api_key": data['key'],
                "message": {
                    "text": "Срочно обратитесь к врачу",
                    "action_link": HOST + "/frame?key={}&contract={}".format(contracts[contract_id]['key'], contract_id)
                }
            }

            result = requests.post(HOST + '/api/agents/message', json=data)
    """

    return "ok"


@app.route('/frame', methods=['GET'])
def action():
    key = request.args.get('key', '')
    contract_id = str(request.args.get('contract', ''))

    if contract_id not in contracts:
        print('invalid contract', contract_id, contracts.keys())
        return "<strong>Ошибка</strong>"
    if key not in contracts[contract_id]['requests']:
        return "<strong>Эта ссылка уже использована.</strong>"

    return render_template('measurement.html')


@app.route('/frame', methods=['POST'])
def action_save():
    key = request.args.get('key', '')
    contract_id = request.args.get('contract', '')

    if contract_id not in contracts:
        print('invalid contract', contract_id, contracts.keys())
        return "<strong>Ошибка</strong>"
    if key not in contracts[contract_id]['requests']:
        return "<strong>Эта ссылка уже использована.</strong>"

    del contracts[contract_id]['requests'][key]

    answer = {}
    print(request.form)
    for param in ['AD1', 'AD2', 'PU']:
        result = request.form.get(param, '')
        if result != '' and check_digit(result):
            answer[param] = float(result)
    answer['time'] = time.time()

    contracts[contract_id]['measurements'].append(answer)
    save()

    return """
    <strong>Спасибо, окно можно закрыть</strong></strong>
    """

@app.route('/graph', methods=['GET'])
def graph():
    contract_id = request.args.get('contract', '')
    if contract_id not in contracts:
        print('invalid contract', contract_id, contracts.keys())
        return "<strong>Ошибка</strong>"

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

    return render_template('graph.html', AD1=json.dumps(AD1), AD2=json.dumps(AD2), PU=json.dumps(PU), times=json.dumps(times))


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
