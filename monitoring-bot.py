from init import *

LAST_TASK_PUSH = 0


class ContractTasks(db.Model):
    __tablename__ = 'contract_tasks'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    contract_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    last_task_push = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    action_link = db.Column(db.String(255))


class ActualBots(db.Model):
    __tablename__ = 'actual_bots'

    contract_id = db.Column(db.Integer, primary_key=True)
    actual = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    confirmation = db.Column(db.Boolean, default=False)
    patient_medicines_enabled = db.Column(db.Boolean, default=False)
    patient_medicines = db.Column(db.Text, nullable=True)
    patient_medicines_last_push = db.Column(db.Integer, default=0)


class CategoryParams(db.Model):
    __tablename__ = 'category_params'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(db.Integer)
    category = db.Column(db.String(25))
    mode = db.Column(db.String(10))
    params = db.Column(db.JSON)
    timetable = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_push = db.Column(db.DateTime)
    show = db.Column(db.Boolean)


class Medicines(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    mode = db.Column(db.String(10))
    dosage = db.Column(db.String(25))
    amount = db.Column(db.String(25))
    timetable = db.Column(db.JSON)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_push = db.Column(db.DateTime)
    show = db.Column(db.Boolean)


class MedicinesResults(db.Model):
    __tablename__ = 'medicines_results'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_push = db.Column(db.DateTime)
    show = db.Column(db.Boolean)


# METHODS

def toDate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def nowDate():
    date_now = datetime.datetime.now()
    return date_now.strftime(DATE_HOUR_FORMAT)


def drop_task(contract_id, task_id):
    if contract_id:
        try:
            delete_task(contract_id, task_id)

        except Exception as e:
            error('Error drop_tasks()')
            print(e)


def dropAllTasks():
    try:
        q = ContractTasks.query
        q.delete()
        db.session.commit()
        out_green_light('success dropAllTasks()')

    except Exception as e:
        error('Error dropAllTasks()')
        print(e)


def drop_tasks(contract_id):
    if contract_id:
        try:
            q2 = ContractTasks.query.filter_by(contract_id=contract_id)

            if (q2.count() > 0):
                q2.delete()
                db.session.commit()

        except Exception as e:
            error('Error drop_tasks()')
            print(e)


def getTaskCount(contract_id):
    query = ContractTasks.query.filter_by(contract_id=contract_id)

    return query.count()


def dateMaxMin(date):
    out = []

    try:
        date_max = date
    except Exception as e:
        error('dateMaxMin(date)')
        print(e)
        date_max = nowDate()

    delta = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(DATE_HOUR_FORMAT)
    date_min = delta
    out.append(date_max)
    out.append(date_min)

    return out


def getBotCategories():
    try:
        query = CategoryParams.query

        if query.count() != 0:
            return query.all()

        return 'EMPTY DATA'


    except Exception as e:
        error('Error getBotCategories()')
        print(e)
        return 'ERROR CONNECTION'


def getAgentToken(contract):
    try:
        data_request = {
            "api_key": APP_KEY,
            "contract_id": contract
        }

        response = requests.post(MAIN_HOST + '/api/agents/token', json=data_request)

        if (response.status_code == 200):
            return json.loads(response.text)

        return response.status_code


    except Exception as e:
        print('Error getAgentToken(): ', e)


def getCategories():
    try:
        data_request = {
            "api_key": APP_KEY
        }

        response = requests.post(MAIN_HOST + '/api/agents/records/categories', json=data_request)

        if (response.status_code == 200):
            return json.loads(response.text)

        return response.status_code


    except Exception as e:
        error('Error getCategories()')
        print(e)


def getRecords(contract_id, category_name):
    try:
        data_request = {
            "contract_id": contract_id,
            "api_key": APP_KEY,
            "category_name": category_name
        }

        response = requests.post(MAIN_HOST + '/api/agents/records/get', json=data_request)

        if (response.status_code == 200):
            return json.loads(response.text)

        return response.status_code

    except Exception as e:
        error('Error getRecords()')
        print(e)


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
        requests.post(MAIN_HOST + '/api/agents/records/add', json=data)

    except Exception as e:
        error('Error add_record()')
        print(e)


def post_request(data, query='/api/agents/message'):
    try:
        return requests.post(MAIN_HOST + query, json=data)
    except Exception as e:
        error('Error post_request()')
        print(e)


def warning(contract_id, param, param_value, param_value_2=''):
    text_patient = ''
    text_doctor = ''

    if (param == 'systolic_pressure'):
        param = 'pressure'

    if (param == 'diastolic_pressure'):
        param = 'pressure'

    if (param == 'pulse'):
        param = 'pulse'

    if (param == 'shin_volume_left'):
        param = 'shin'

    if (param == 'shin_volume_right'):
        param = 'shin'

    if (param == 'leg_circumference_left'):
        param = 'shin'

    if (param == 'leg_circumference_right'):
        param = 'shin'

    if (param == 'waist_circumference'):
        param = 'waist'

    if (param in AVAILABLE_MEASUREMENTS):
        if (param == 'pressure'):
            text_patient = MESS_PRESSURE_PATIENT.format(
                param_value, param_value_2)
            text_doctor = MESS_PRESSURE_DOCTOR.format(
                param_value, param_value_2)

        if (param == 'pulse'):
            text_patient = MESS_PULSE_PATIENT
            text_doctor = MESS_PULSE_DOCTOR

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


def quard_data_json(data):
    if (data == None):
        out_red_light('data None')
        return 'None'

    if ('api_key' not in data):
        out_red_light('key api_key not exists')
        return 'key api_key not exists'

    if (APP_KEY != data['api_key']):
        out_red_light('invalid key')
        return 'invalid key'

    if ('contract_id' not in data):
        out_red_light('key contract_id not exists')
        return 'key contract_id not exists'

    contract_id = data['contract_id']

    return contract_id

try:
    db.create_all()
except:
    print('cant create structure')

def quard():
    key = request.args.get('api_key', '')

    if key != APP_KEY:
        out_red_light('WRONG_APP_KEY')
        return 'WRONG_APP_KEY'

    try:
        contract_id = int(request.args.get('contract_id', ''))
    except Exception as e:
        error('ERROR_CONTRACT')
        print(e)
        return 'ERROR_CONTRACT'

    try:
        actual_bots = ActualBots.query.filter_by(contract_id=contract_id)

        for actual_bot in actual_bots:
            return actual_bot.contract_id

    except Exception as e:
        error('ERROR_QUARD')
        print(e)
        return 'ERROR_QUARD'

    return contract_id


def process_records():
    global LAST_TASK_PUSH
    megaTask = []
    records = CategoryParams.query.filter_by(show=True).all()
    now = datetime.datetime.now()
    go_task = now.hour == int(TASK_HOUR) and time.time() - LAST_TASK_PUSH > 60 * 60

    for record in records:
        try:
            contract_id = record.contract_id
            name = record.category

            contract = ActualBots.query.filter_by(contract_id=contract_id).first()

            if not contract or not contract.actual:
                continue

            if name in STOP_LIST:
                continue

            mode = record.mode
            timetable = record.timetable

            should_i_send = False
            same_day_hours = []

            if mode == 'daily':
                for point in timetable["hours"]:
                    hour = int(point["value"])
                    if hour == 24:
                        hour = 0

                    same_day_hours.append(hour)

                    if hour == now.hour and (now - record.last_push).total_seconds() > 60 * 60:
                        should_i_send = True
                        same_day_hours.remove(hour)

            if mode == 'weekly':
                for point in timetable["days_week"]:
                    hour = int(point["hour"])

                    if now.isoweekday() == int(point["day"]):
                        same_day_hours.append(hour)

                        if hour == now.hour and (now - record.last_push).total_seconds() > 60 * 60:
                            should_i_send = True
                            same_day_hours.remove(hour)

            if mode == 'monthly':
                for point in timetable["days_month"]:
                    hour = int(point["hour"])

                    if now.day == int(point["day"]):
                        same_day_hours.append(hour)
                        if hour == now.hour and (now - record.last_push).total_seconds() > 60 * 60:
                            should_i_send = True
                            same_day_hours.remove(hour)

            if go_task:
                megaTask.append({
                    'contract_id': contract_id,
                    'text': CATEGORY_TEXT[name],
                    'target_number': len(same_day_hours),
                    'action_link': 'frame/' + transformMeasurementName(name)
                })

            if should_i_send:
                next_hours = list(filter(lambda x: x > now.hour, same_day_hours))

                if next_hours:
                    deadline = int(time.time() + (min(next_hours) - now.hour) * 60 * 60)
                else:
                    deadline = int(time.time() + 12 * 60 * 60)

                route_name = transformMeasurementName(name)

                data = {
                    "contract_id": contract_id,
                    "api_key": APP_KEY,
                    "message": {
                        "text": MESS_MEASUREMENT[route_name]['text'],
                        "action_link": "frame/" + route_name,
                        "action_deadline": deadline,
                        "action_name": MESS_MEASUREMENT[route_name]['action_name'],
                        "action_onetime": True,
                        "only_doctor": False,
                        "only_patient": True,
                    },
                }

                record.last_push = now
                db.session.commit()

                no_message = False
                res = getRecords(contract_id, name)

                if res != 404:
                    out_yellow(name)
                    values = res['values']

                    for value in values:
                        delta = (time.time() - value['timestamp']) / 60

                        if (delta < 60):
                            no_message = True
                            print("skip record", record.id, "results exists")

                        break

                if no_message == False:
                    post_request(data)
        except Exception as e:
            print(e)
            print("problem with record", record.id)

    if go_task:
        LAST_TASK_PUSH = time.time()
        delayed(1, dayTaskPlanning, [megaTask])


def process_medicines():
    now = datetime.datetime.now()
    query_str = "SELECT * FROM medicines WHERE show = true"
    medicines = DB.select(query_str)

    for medicine in medicines:
        try:
            id = str(medicine[0])
            contract_id = medicine[1]
            name = medicine[2]
            mode = medicine[3]
            dosage = medicine[4]
            timetable = medicine[6]

            should_i_send = False
            same_day_hours = []

            if mode == 'daily':
                for point in timetable["hours"]:
                    hour = int(point["value"])
                    if hour == 24:
                        hour = 0

                    same_day_hours.append(hour)

                    if hour == now.hour and (now - medicine[8]).total_seconds() > 60 * 60:
                        should_i_send = True
                        same_day_hours.remove(hour)

            if mode == 'weekly':
                for point in timetable["days_week"]:
                    hour = int(point["hour"])

                    if now.isoweekday() == int(point["day"]):
                        same_day_hours.append(hour)

                        if hour == now.hour and (now - medicine[8]).total_seconds() > 60 * 60:
                            should_i_send = True
                            same_day_hours.remove(hour)

            if mode == 'monthly':
                for point in timetable["days_month"]:
                    hour = int(point["hour"])

                    if now.day == int(point["day"]):
                        same_day_hours.append(hour)
                        if hour == now.hour and (now - medicine[8]).total_seconds() > 60 * 60:
                            should_i_send = True
                            same_day_hours.remove(hour)

            if should_i_send:
                next_hours = list(filter(lambda x: x > now.hour, same_day_hours))

                if next_hours:
                    deadline = int(time.time() + (min(next_hours) - now.hour) * 60 * 60)
                else:
                    deadline = int(time.time() + 12 * 60 * 60)

                data = {
                    "contract_id": contract_id,
                    "api_key": APP_KEY,
                    "message": {
                        "text": MESS_MEDICINE['text'].format(name),
                        "action_link": MESS_MEDICINE['action_link'].format(id),
                        "action_name": MESS_MEDICINE['action_name'].format(name, dosage),
                        "action_onetime": True,
                        "action_deadline": deadline,
                        "only_doctor": False,
                        "only_patient": True,
                    }
                }

                query_str = "UPDATE medicines set last_push = '" + \
                            str(datetime.datetime.fromtimestamp(
                                time.time()).isoformat()) + Aux.quote() + \
                            " WHERE id = '" + str(id) + Aux.quote()

                DB.query(query_str)

                post_request(data)
        except Exception as e:
            print(e)
            print("problem with record", id)

    db.session.commit()

def process_patient_medicines():
    contracts = ActualBots.query.filter_by(actual=True, patient_medicines_enabled=True).all()

    for contract in contracts:
        if contract.patient_medicines_last_push < time.time() - 30 * 24 * 60 * 60:
            send_medicines_query(contract)
            contract.patient_medicines_last_push = int(time.time())

    db.session.commit()

def send_medicines_query(contract):

    if contract.patient_medicines:
        message = "В прошлом месяце вы сообщили, что принимаете следующие лекарства. Если этот список изменился, пожалуйста, нажмите на кнопку ниже и внесите изменения."
        message += '\n\n' + contract.patient_medicines
    else:
        message = "Какие лекарства вы принимаете? Чтобы упростить работу врача, нажмите на кнопку ниже и перечислите их в свободной форме с указанием дозировки."

    data = {
        "contract_id": contract.contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": message,
            "only_patient": True,
            "action_link": "report_medicines",
            "action_name": "Обновить список лекарств",
            "action_onetime": True,
        }
    }

    post_request(data)

def sender():
    while True:
        try:
            process_records()
            process_medicines()
            process_patient_medicines()
        except Exception as e:
            print(e)

        time.sleep(60)


def getTasks(contract_id):
    try:
        q = ContractTasks.query.filter_by(contract_id=contract_id)

        if q.count() != 0:
            return q.all()

        return []

    except Exception as e:
        error('Error get_tasks()')
        print(e)


def transformMeasurementName(name):
    if name == 'systolic_pressure':
        name = 'pressure'

    if name == 'leg_circumference_left':
        name = 'shin'

    if name == 'waist_circumference':
        name = 'waist'

    return str(name)


def dayTaskPlanning(tasks):
    dropAllTasks()

    for task in tasks:
        try:
            contract_id = task['contract_id']
            task_id = add_task(contract_id, task['text'], task['target_number'], action_link=task['action_link'])
            contract_task = ContractTasks(contract_id=contract_id,
                                          task_id=task_id,
                                          last_task_push=nowDate(),
                                          created_at=nowDate(),
                                          updated_at=nowDate(),
                                          action_link=task['action_link'])
            db.session.add(contract_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error('Error dayTaskPlanning()')
            print(e)
            raise


def initTasks(contract_id):
    drop_tasks(contract_id)

    category_params = CategoryParams.query.filter_by(contract_id=contract_id, show=True).all()

    for category_param in category_params:
        name = category_param.category
        timetable = category_param.timetable

        hours = timetable['hours']

        if name in STOP_LIST:
            continue

        text = CATEGORY_TEXT[name]

        name = transformMeasurementName(name)

        task_id = add_task(contract_id, text, len(hours), action_link='frame/' + str(name))

        try:
            contract_task = ContractTasks(contract_id=contract_id, task_id=task_id, last_task_push=nowDate(),
                                          created_at=nowDate(), updated_at=nowDate(), action_link='frame/' + str(name))
            db.session.add(contract_task)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            error('Error initTask()')
            print(e)
            raise

    info_green('Success initTask()')


# ******************************************
# ************** Testing place *************
# ******************************************


# ******************************************
# ************** END Testing place *********
# ******************************************

# ROUTES GET

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


@app.route('/actions', methods=['POST'])
def actions():
    try:
        data = request.json
        contract_id = quard_data_json(data)
    except Exception as e:
        error('Error actions()')
        print(e)

    type = 'patient'

    query_str = 'SELECT count(id) as cnt FROM medicines m WHERE contract_id = ' + str(contract_id) + ' AND show = true'
    records = DB.select(query_str)

    cnt = 0

    for row in records:
        cnt = row[0]

    answer = []

    if cnt > 0:
        answer.append({'link': 'medicines', 'type': type, 'name': 'Прием лекарств'})

    category_params = CategoryParams.query.filter_by(contract_id=contract_id, show=True).all()

    continues_list = ['diastolic_pressure', 'pulse', 'leg_circumference_right']

    descriptions = {
        'pressure': 'Записать давление',
        'weight': 'Записать вес',
        'temperature': 'Записать температуру',
        'shin': 'Записать размер обхвата голени',
        'glukose': 'Записать уровень глюкозы',
        'waist': 'Записать окружность талии',
        'spo2': 'Записать уровень насыщения крови',
        'pain_assessment': 'Записать уровень болевых ощущений'
    }

    for category_param in category_params:
        name = category_param.category

        if name in continues_list:
            continue

        if name == 'systolic_pressure':
            name = 'pressure'

        if name == 'leg_circumference_left':
            name = 'shin'

        if name == 'waist_circumference':
            name = 'waist'

        answer.append({
            'link': 'frame/' + str(name),
            'type': type,
            'name': descriptions[name]
        })

    return json.dumps(answer)


@app.route('/graph', methods=['GET'])
def graph():
    contract_id = quard()
    comments = []
    constants = {}

    medical_record_categories = getCategories()

    for item in medical_record_categories:
        category = item['name']

        if category not in CATEGORY_TEXT.keys():
            break

        CategoryParamsObj = CategoryParams.query.filter_by(category=category, contract_id=contract_id).first()
        params = CategoryParamsObj.params

        if category == 'systolic_pressure':
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

        if category == 'spo2':
            try:
                constants['max_spo2'] = params['max']
                constants['min_spo2'] = params['min']
            except Exception as e:
                constants['max_spo2'] = MAX_SPO2_DEFAULT
                constants['min_spo2'] = MIN_SPO2_DEFAULT

        if category == 'glukose':
            try:
                constants['max_glukose'] = params['max']
                constants['min_glukose'] = params['min']
            except Exception as e:
                constants['max_glukose'] = MAX_GLUKOSE_DEFAULT
                constants['min_glukose'] = MIN_GLUKOSE_DEFAULT

        if category == 'pain_assessment':
            try:
                constants['max_pain'] = params['max']
                constants['min_pain'] = params['min']
            except Exception as e:
                constants['max_pain'] = MAX_PAIN_DEFAULT
                constants['min_pain'] = MIN_PAIN_DEFAULT

        if category == 'weight':
            try:
                constants['max_weight'] = params['max']
                constants['min_weight'] = params['min']
            except Exception as e:
                constants['max_weight'] = MAX_WEIGHT_DEFAULT
                constants['min_weight'] = MIN_WEIGHT_DEFAULT

        if category == 'waist_circumference':
            try:
                constants['max_waist'] = params['max']
                constants['min_waist'] = params['min']
            except Exception as e:
                constants['max_waist'] = MAX_WAIST_DEFAULT
                constants['min_waist'] = MIN_WAIST_DEFAULT

        if category == 'leg_circumference_left' or category == 'leg_circumference_right':
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

        if category == 'temperature':
            try:
                constants['max_temperature'] = params['max']
                constants['min_temperature'] = params['min']
            except Exception as e:
                constants['max_temperature'] = MAX_TEMPERATURE_DEFAULT
                constants['min_temperature'] = MIN_TEMPERATURE_DEFAULT

        response = getRecords(contract_id, 'systolic_pressure')
        x = []
        y = []

        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        if len(x):
            date_max = x[0]
        else:
            date_max = nowDate()

        dt = time.strptime(date_max, DATE_HOUR_FORMAT)
        delta = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(DATE_HOUR_FORMAT)
        date_min = delta
        date_max = time.strftime('%Y-%m-%d', dt)
        zoomToDates = 'off'

        if (len(x) > 0):
            d1 = x[len(x) - 1]
            d2 = date_min

            if (d2 > d1):
                zoomToDates = 'on'

        if (len(y) > 0):
            max_y = max(y)
            min_y = min(y)
        else:
            max_y = 0
            min_y = 0

        systolic_dic = {
            "zoomToDates": zoomToDates,
            "x": x,
            "y": y,
            "date_max": date_max,
            "date_min": date_min,
            "sys_max_value": max_y,
            "sys_min_value": min_y,
            "comments": '',
            "name": category['description']
        }

        systolic = systolic_dic
        response = getRecords(contract_id, 'diastolic_pressure')

        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        diastolic_dic = {
            "x": x,
            "y": y,
            "name": category['description']
        }

        diastolic = diastolic_dic

        # pulse

        response = getRecords(contract_id, 'pulse')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        pulse_dic = {
            "x": x,
            "y": y,
            "name": category['description']
        }

        pulse = pulse_dic

        # medicines

        query_str = "select * from medicines m inner join medicines_results mr on m.id = mr.medicines_id " + \
                    " WHERE contract_id = " + \
                    Aux.quote() + str(contract_id) + Aux.quote() + \
                    " ORDER BY time ASC"

        records = DB.select(query_str)

        array_x = []
        array_y = []
        text = []
        medicines_data = {}

        for row in records:
            date_ = row[13]
            text.append(row[2])
            array_x.append(date_.strftime(DATE_HOUR_FORMAT))

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
                medicines_times_.append(date_.strftime(DATE_HOUR_FORMAT))

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

        # pain_assessment

        response = getRecords(contract_id, 'pain_assessment')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        pain_assessment_dic = {
            "x": x,
            "y": y,
            "date_max": date_max_min[0],
            "date_min": date_max_min[1],
            "comments": comments,
            "name": category['description']
        }

        # weight

        response = getRecords(contract_id, 'weight')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        zoomToDates = 'off'

        if (len(x) > 0):
            date_max = date_max_min[0]
            date_min = date_max_min[1]
            d1 = x[len(x) - 1]
            d2 = date_min

            if (d2 > d1):
                zoomToDates = 'on'

        else:
            date_max = nowDate()
            date_min = nowDate()

        weight_dic = {
            "zoomToDates": zoomToDates,
            "x": x,
            "y": y,
            "date_max": date_max,
            "date_min": date_min,
            "comments": comments,
            "name": category['description']
        }

        constants = {'max_shin_right': 35, 'min_waist': 30, 'min_shin_right': 10, 'min_diastolic': 30, 'max_pain': 7,
                     'max_pulse': 80, 'max_spo2': 100, 'max_diastolic': 99, 'max_waist': 150, 'min_pain': 0, 'max_shin_left': 35,
                     'min_systolic': 90, 'min_weight': 45, 'max_systolic': 140, 'max_temperature': 37, 'min_pulse': 50,
                     'min_glukose': 4, 'min_shin_left': 10, 'min_temperature': 36, 'max_weight': 150, 'max_glukose': 6.5,
                     'min_spo2': 93}

        weight_series = weight_dic

        # temperature

        response = getRecords(contract_id, 'temperature')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        temperature_dic = {
            "x": x,
            "y": y,
            "date_max": date_max_min[0],
            "date_min": date_max_min[1],
            "comments": comments,
            "name": category['description']
        }

        temperature_series = temperature_dic

        # ********************************************* glukose

        response = getRecords(contract_id, 'glukose')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        glukose_dic = {
            "x": x,
            "y": y,
            "date_max": date_max_min[0],
            "date_min": date_max_min[1],
            "comments": comments,
            "name": category['description']
        }

        glukose_series = glukose_dic

        # spo2

        response = getRecords(contract_id, 'spo2')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        spo2_dic = {
            "x": x,
            "y": y,
            "date_max": date_max_min[0],
            "date_min": date_max_min[1],
            "comments": comments,
            "name": category['description']
        }

        spo2_series = spo2_dic

        # waist_circumference

        response = getRecords(contract_id, 'waist_circumference')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        waist_dic = {
            "x": x,
            "y": y,
            "date_max": date_max_min[0],
            "date_min": date_max_min[1],
            "comments": comments,
            "name": category['description']
        }

        waist_series = waist_dic

        # leg_circumference_left

        response = getRecords(contract_id, 'leg_circumference_left')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
            y.append(value['value'])

        try:
            date_max_min = dateMaxMin(x[0])
        except Exception as e:
            date_max_min = nowDate()

        shin_left_dic = {
            "x": x,
            "y": y,
            "date_max": date_max_min[0],
            "date_min": date_max_min[1],
            "comments": comments,
            "name": category['description']
        }

        shin_left = shin_left_dic

        # leg_circumference_right

        response = getRecords(contract_id, 'leg_circumference_right')
        x = []
        y = []
        category = response['category']
        values = response['values']

        for value in values:
            date = datetime.datetime.fromtimestamp(value['timestamp'])
            x.append(date.strftime(DATE_HOUR_FORMAT))
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

    return "ok"


@app.route('/settings', methods=['GET'])
def settings():
    try:
        contract_id = quard()
    except Exception as e:
        error('Error settings()')
        return 'UNKNOWN ERROR'

    if contract_id == ERROR_KEY:
        return ERROR_KEY

    if contract_id == ERROR_CONTRACT:
        return ERROR_CONTRACT

    contract = ActualBots.query.filter_by(contract_id=contract_id).first()

    category_params = CategoryParams.query.filter_by(contract_id=contract_id).all()
    categories = getCategories()
    categories_description = {}
    categories_unit = {}

    for category in categories:
        name = category['name']
        unit = category['unit']
        description = category['description']
        categories_description[name] = description
        categories_unit[name] = unit

    measurements = []
    pressure = {}
    shin = {}

    for category_param in category_params:
        timetable = []
        measurement_new = {}
        name = category_param.category
        alias = ''
        mode = category_param.mode
        unit = categories_unit[name]
        params = category_param.params
        timetable.append(category_param.timetable)
        show = category_param.show
        last_push = category_param.last_push

        if name == 'leg_circumference_left':
            shin['name'] = 'shin'

            if name in categories_description:
                shin['alias'] = categories_description[name]
            else:
                shin['alias'] = 'измерение окружности голени'

            if name in categories_unit:
                shin['unit'] = categories_unit[name]
            else:
                shin['unit'] = unit

            shin['mode'] = mode
            shin['last_push'] = last_push.strftime("%Y-%m-%d %H:%M:%S")
            shin['timetable'] = timetable
            shin['show'] = show

            try:
                shin['max'] = params['max']
                shin['min'] = params['min']
            except Exception as e:
                shin['max'] = MAX_SHIN
                shin['min'] = MIN_SHIN

            measurements.append(shin)

        if name == 'systolic_pressure':
            pressure['name'] = 'pressure'

            if name in categories_description:
                pressure['alias'] = categories_description[name]
            else:
                pressure['alias'] = 'измерение давления'

            if name in categories_unit:
                pressure['unit'] = categories_unit[name]
            else:
                pressure['unit'] = unit

            pressure['mode'] = mode
            pressure['last_push'] = last_push.strftime("%Y-%m-%d %H:%M:%S")
            pressure['timetable'] = timetable
            pressure['show'] = show

            try:
                pressure['max_systolic'] = params['max_systolic']
                pressure['min_systolic'] = params['min_systolic']
                pressure['max_diastolic'] = params['max_diastolic']
                pressure['min_diastolic'] = params['min_diastolic']
                pressure['max_pulse'] = params['max_pulse']
                pressure['min_pulse'] = params['min_pulse']
            except Exception as e:
                pressure['max_systolic'] = MAX_SYSTOLIC_DEFAULT
                pressure['min_systolic'] = MIN_SYSTOLIC_DEFAULT
                pressure['max_diastolic'] = MAX_DIASTOLIC_DEFAULT
                pressure['min_diastolic'] = MIN_DIASTOLIC_DEFAULT
                pressure['max_pulse'] = MAX_PULSE_DEFAULT
                pressure['min_pulse'] = MIN_PULSE_DEFAULT

            measurements.append(pressure)

        out_list = ['systolic_pressure', 'diastolic_pressure', 'pulse', 'leg_circumference_left', 'leg_circumference_right']

        if name not in out_list:
            measurement_new['name'] = name

            if name in categories_description:
                measurement_new['alias'] = categories_description[name]
            else:
                measurement_new['alias'] = ''

            if name in categories_unit:
                measurement_new['unit'] = categories_unit[name]
            else:
                measurement_new['unit'] = ''

            measurement_new['mode'] = mode
            measurement_new['last_push'] = last_push.strftime("%Y-%m-%d %H:%M:%S")
            measurement_new['unit'] = ''
            measurement_new['show'] = show
            measurement_new['timetable'] = timetable

            try:
                measurement_new['max'] = params['max']
                measurement_new['min'] = params['min']
            except Exception as e:
                measurement_new['max'] = 0
                measurement_new['min'] = 0

            measurements.append(measurement_new)

    # MEDICINES

    query_str = "SELECT m.name, m.dosage, m.amount, m.id, m.timetable, m.show, m.last_push, m.created_at, m.mode FROM medicines m  WHERE contract_id = " + Aux.quote() + str(
        contract_id) + Aux.quote()
    records = DB.select(query_str)

    medicines_new = []

    for row in records:
        times = []
        timetable = []
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

    return render_template('settings.html', contract=contract,
                           medicines_data=json.dumps(medicines),
                           measurements_data=json.dumps(measurements),
                           medicines_data_new=json.dumps(medicines_new), confirmation=str(contract.confirmation).lower(),
                           patient_medicines_enabled=str(contract.patient_medicines_enabled).lower())


@app.route('/medicine/<uid>', methods=['GET'])
def medicine_done(uid):
    result = quard()

    if result in ERRORS:
        return result

    query_str = "INSERT INTO medicines_results VALUES(nextval('medicines_results$id$seq')," + Aux.quote() + str(uid) + Aux.quote() + ",(select * from now()), (select * from now()), (select * from now()))"

    result = DB.query(query_str)

    if result != 'SUCCESS_QUERY':
        return result

    return MESS_THANKS


@app.route('/medicines', methods=['GET'])
def medicines():
    contract_id = quard()
    query_str = 'SELECT m.id, m.name FROM medicines m WHERE m.contract_id = ' + Aux.quote() + str(contract_id) + Aux.quote() + ' AND show = true'
    records = DB.select(query_str)
    medicine_data = {}
    response = getAgentToken(contract_id)
    agent_token = response['agent_token']
    out_yellow(agent_token)

    for row in records:
        id = row[0]
        name = row[1]

        medicine_data[name] = {
            'id': id,
            'action_link': MAIN_HOST + '/api/client/agents/' + str(AGENT_ID) + '?action=medicine/' + str(id) + '&contract_id=' + str(contract_id) + '&agent_token=' + str(agent_token)
        }

    return render_template('medicines.html', medicine_data=medicine_data, contract_id=contract_id)


@app.route('/medicine/add', methods=['POST'])
def medicine_done_post():
    result = quard_data_json()
    return result


@app.route('/frame/<string:pull>', methods=['GET'])
def action_pull(pull):
    contract_id = quard()

    if contract_id in ERRORS:
        return contract_id

    contract = ActualBots.query.filter_by(contract_id=contract_id).first()

    constants = {}

    if pull == 'shin':
        constants['shin_max'] = MAX_SHIN
        constants['shin_min'] = MIN_SHIN

        return render_template('shin.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'pressure':
        constants['sys_max'] = MAX_SYSTOLIC
        constants['sys_min'] = MIN_SYSTOLIC
        constants['dia_max'] = MAX_DIASTOLIC
        constants['dia_min'] = MIN_DIASTOLIC
        constants['pulse_max'] = MAX_PULSE
        constants['pulse_min'] = MIN_PULSE

        return render_template('pressure.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'weight':
        constants['weight_max'] = MAX_WEIGHT
        constants['weight_min'] = MIN_WEIGHT

        return render_template('weight.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'temperature':
        constants['temperature_max'] = MAX_TEMPERATURE
        constants['temperature_min'] = MIN_TEMPERATURE

        return render_template('temperature.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'glukose':
        constants['glukose_max'] = MAX_GLUKOSE
        constants['glukose_min'] = MIN_GLUKOSE

        return render_template('glukose.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'pain_assessment':
        constants['pain_assessment_max'] = MAX_ASSESSMENT
        constants['pain_assessment_min'] = MIN_ASSESSMENT

        return render_template('pain_assessment.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'spo2':
        constants['spo2_max'] = MAX_SPO2
        constants['spo2_min'] = MIN_SPO2

        return render_template('spo2.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    if pull == 'waist':
        constants['waist_max'] = MAX_WAIST
        constants['waist_min'] = MIN_WAIST

        return render_template('waist.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())

    return render_template('measurement.html', tmpl=pull, constants=constants, confirmation=str(contract.confirmation).lower())


# ROUTES POST

@app.route('/status', methods=['POST'])
def status():
    out_yellow('status')

    try:
        data = request.json
    except Exception as e:
        error('Error status()')
        print(e)
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

    return json.dumps(answer)


@app.route('/settings', methods=['POST'])
def setting_save():
    contract_id = quard()

    if contract_id in ERRORS:
        return contract_id

    contract = ActualBots.query.filter_by(contract_id=contract_id).first()

    try:
        data = json.loads(request.form.get('json'))
    except Exception as e:
        error('Error json.loads()')
        print(e)
        return 'ERROR_JSON_LOADS'

    contract.confirmation = data['confirmation']
    contract.patient_medicines_enabled = data['patient_medicines_enabled']
    db.session.commit()

    for measurement in data['measurements_data']:
        params = {}
        name = measurement['name']

        if name == 'pressure':
            params['max_systolic'] = int(measurement['max_systolic'])
            params['min_systolic'] = int(measurement['min_systolic'])
            params['max_diastolic'] = int(measurement['max_diastolic'])
            params['min_diastolic'] = int(measurement['min_diastolic'])
            params['max_pulse'] = int(measurement['max_pulse'])
            params['min_pulse'] = int(measurement['min_pulse'])
        else:
            params['max'] = float(measurement['max'])
            params['min'] = float(measurement['min'])

        mode = measurement['mode']
        timetable = measurement['timetable'][0]

        for item in timetable:
            if item == 'hours':
                for point in timetable[item]:
                    point['value'] = int(point['value'])

            else:
                for point in timetable[item]:
                    point['hour'] = int(point['hour'])
                    point['day'] = int(point['day'])

        show = measurement['show']

        try:
            if name == 'pressure':
                name = 'systolic_pressure'

            if name == 'shin':
                name = 'leg_circumference_left'

            query = CategoryParams.query.filter_by(contract_id=contract_id, category=name)

            if query.count() != 0:
                contract = query.first()

                contract.mode = mode
                contract.params = params
                contract.timetable = timetable
                contract.show = show

                db.session.commit()
            else:
                print('No records in category_params')

        except Exception as e:
            print("error query", e)
            raise

    for medicine in data['medicines_data']:
        name = medicine['name']
        mode = medicine['mode']
        dosage = medicine['dosage']
        amount = medicine['amount']
        json__ = medicine['timetable'][0]
        timetable = json__
        show = medicine['show']

        for item in timetable:
            if item == 'hours':
                for point in timetable[item]:
                    point['value'] = int(point['value'])

            else:
                for point in timetable[item]:
                    point['hour'] = int(point['hour'])
                    point['day'] = int(point['day'])

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

@app.route('/order', methods=['POST'])
def order():
    data = request.json
    contract_id = quard_data_json(data)

    contract = ActualBots.query.filter_by(contract_id=contract_id).first()

    if contract:
        try:
            order = data['order']

            if order == "enable_monitoring" or order == "disable_monitoring":
                category = data['params']['category']

                if category != "pressure":
                    record = CategoryParams.query.filter_by(contract_id=contract_id, category=category).first()

                    if order == "disable_monitoring":
                        record.show = False
                    else:
                        timetable = data['params']['timetable']
                        mode = data['params']['mode']
                        min_value = data['params']['min']
                        max_value = data['params']['max']

                        record.show = True
                        record.timetable = timetable
                        record.params = {
                            "min": min_value,
                            "max": max_value
                        }
                        record.mode = mode
                else:
                    sp = CategoryParams.query.filter_by(contract_id=contract_id, category="systolic_pressure").first()
                    dp = CategoryParams.query.filter_by(contract_id=contract_id, category="diastolic_pressure").first()
                    pulse = CategoryParams.query.filter_by(contract_id=contract_id, category="pulse").first()

                    entries = [sp, dp, pulse]

                    if order == "disable_monitoring":
                        for e in entries:
                            e.show = False
                    else:
                        timetable = data['params']['timetable']
                        mode = data['params']['mode']
                        params = {
                            "max_systolic": data['params']['max_systolic'],
                            "min_systolic": data['params']['min_systolic'],
                            "max_diastolic": data['params']['max_diastolic'],
                            "min_diastolic": data['params']['min_diastolic'],
                            "max_pulse": data['params']['max_pulse'],
                            "min_pulse": data['params']['min_pulse']
                        }

                        for e in entries:
                            e.show = True
                            e.timetable = timetable
                            e.params = params
                            e.mode = mode
            if order == "add_medicine":
                name = data['params']['name']
                mode = data['params']['mode']
                dosage = data['params']['dosage']
                amount = data['params']['amount']
                timetable = json.dumps(data['params']['timetable'])

                query_str = "INSERT INTO medicines VALUES((select uuid_generate_v4())," + \
                            str(contract_id) + "," + \
                            Aux.quote() + str(name) + Aux.quote() + "," + \
                            Aux.quote() + str(mode) + Aux.quote() + "," + \
                            Aux.quote() + str(dosage) + Aux.quote() + "," + \
                            Aux.quote() + str(amount) + Aux.quote() + "," + \
                            Aux.quote() + str(timetable) + Aux.quote() + "," + \
                            Aux.quote() + str(True) + Aux.quote() + \
                            ", (select * from now()), (select * from now()), (select * from now()))"

                DB.query(query_str)

            if order == "remove_medicine":
                name = data['params']['name']

                query_str = "UPDATE medicines set show = " + Aux.quote() + str(False) + Aux.quote() + \
                            " WHERE name = " + Aux.quote() + str(name) + Aux.quote() + " and contract_id = " + contract.id

                DB.query(query_str)

            db.session.commit()
            return "ok"
        except Exception as e:
            print(e)
    else:
        return "error"

@app.route('/init', methods=['POST'])
def init():
    try:
        data = request.json
        contract_id = quard_data_json(data)

        contract = ActualBots.query.filter_by(contract_id=contract_id).first()

        if contract:
            contract.actual = True
            db.session.commit()

            initTasks(contract_id)
            out_green_light('Activate contract')

        else:
            contract = ActualBots(contract_id=contract_id, actual=True, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
            db.session.add(contract)
            db.session.commit()

            preset = data.get('preset')
            preset_params = data.get('params', {})

            max_systolic = int(preset_params.get('max_systolic', MAX_SYSTOLIC_DEFAULT))
            min_systolic = int(preset_params.get('min_systolic', MIN_SYSTOLIC_DEFAULT))
            max_diastolic = int(preset_params.get('max_diastolic', MAX_DIASTOLIC_DEFAULT))
            min_diastolic = int(preset_params.get('min_diastolic', MIN_DIASTOLIC_DEFAULT))
            max_pulse = int(preset_params.get('max_pulse', MAX_PULSE_DEFAULT))
            min_pulse = int(preset_params.get('min_pulse', MIN_PULSE_DEFAULT))
            min_weight = float(preset_params.get('min_weight', MIN_WEIGHT_DEFAULT))
            max_weight = float(preset_params.get('max_weight', MAX_WEIGHT_DEFAULT))
            max_waist = float(preset_params.get('max_waist', MAX_WAIST_DEFAULT))
            min_waist = float(preset_params.get('min_waist', MIN_WAIST_DEFAULT))

            if 'current_systolic' in preset_params:
                current_systolic = int(preset_params['current_systolic'])

                max_systolic = current_systolic + (current_systolic // 3)
                min_systolic = current_systolic - (current_systolic // 3)

            if 'current_diastolic' in preset_params:
                current_diastolic = int(preset_params['current_diastolic'])
                max_diastolic = current_diastolic + (current_diastolic // 3)
                min_diastolic = current_diastolic - (current_diastolic // 3)

            if 'current_pulse' in preset_params:
                current_pulse = int(preset_params['current_pulse'])
                max_pulse = current_pulse + (current_pulse // 3)
                min_pulse = current_pulse - (current_pulse // 3)

            params = {
                "max_systolic": max_systolic,
                "min_systolic": min_systolic,
                "max_diastolic": max_diastolic,
                "min_diastolic": min_diastolic,
                "max_pulse": max_pulse,
                "min_pulse": min_pulse
            }

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
            show = False

            systolic_pressure = CategoryParams(contract_id=contract_id,
                                               category='systolic_pressure',
                                               mode=mode,
                                               params=params,
                                               timetable=timetable,
                                               created_at=nowDate(),
                                               updated_at=nowDate(),
                                               last_push=toDate(0),
                                               show=show)
            diastolic_pressure = CategoryParams(contract_id=contract_id,
                                                category='diastolic_pressure',
                                                mode=mode,
                                                params=params,
                                                timetable=timetable,
                                                created_at=nowDate(),
                                                updated_at=nowDate(),
                                                last_push=toDate(0),
                                                show=show)

            pulse = CategoryParams(contract_id=contract_id,
                                   category='pulse',
                                   mode=mode,
                                   params=params,
                                   timetable=timetable,
                                   created_at=nowDate(),
                                   updated_at=nowDate(),
                                   last_push=toDate(0),
                                   show=show)

            temperature = CategoryParams(contract_id=contract_id,
                                         category='temperature',
                                         mode=mode,
                                         params={
                                             "max": MAX_TEMPERATURE_DEFAULT,
                                             "min": MIN_TEMPERATURE_DEFAULT
                                         },
                                         timetable=timetable,
                                         created_at=nowDate(),
                                         updated_at=nowDate(),
                                         last_push=toDate(0),
                                         show=show)

            glukose = CategoryParams(contract_id=contract_id,
                                     category='glukose',
                                     mode=mode,
                                     params={
                                         "max": MAX_GLUKOSE_DEFAULT,
                                         "min": MIN_GLUKOSE_DEFAULT
                                     },
                                     timetable=timetable,
                                     created_at=nowDate(),
                                     updated_at=nowDate(),
                                     last_push=toDate(0),
                                     show=show)

            weight = CategoryParams(contract_id=contract_id,
                                    category='weight',
                                    mode=mode,
                                    params={
                                        "max": max_weight,
                                        "min": min_weight
                                    },
                                    timetable=timetable,
                                    created_at=nowDate(),
                                    updated_at=nowDate(),
                                    last_push=toDate(0),
                                    show=show)

            waist_circumference = CategoryParams(contract_id=contract_id,
                                                 category='waist_circumference',
                                                 mode=mode,
                                                 params={
                                                     "max": max_waist,
                                                     "min": min_waist
                                                 },
                                                 timetable=timetable,
                                                 created_at=nowDate(),
                                                 updated_at=nowDate(),
                                                 last_push=toDate(0),
                                                 show=show)

            spo2 = CategoryParams(contract_id=contract_id,
                                  category='spo2',
                                  mode=mode,
                                  params={
                                      "max": MAX_SPO2_DEFAULT,
                                      "min": MIN_SPO2_DEFAULT
                                  },
                                  timetable=timetable,
                                  created_at=nowDate(),
                                  updated_at=nowDate(),
                                  last_push=toDate(0),
                                  show=show)

            pain_assessment = CategoryParams(contract_id=contract_id,
                                             category='pain_assessment',
                                             mode=mode,
                                             params={
                                                 "max": MAX_PAIN_DEFAULT,
                                                 "min": MIN_PAIN_DEFAULT
                                             },
                                             timetable=timetable,
                                             created_at=nowDate(),
                                             updated_at=nowDate(),
                                             last_push=toDate(0),
                                             show=show)

            leg_circumference_left = CategoryParams(contract_id=contract_id,
                                                    category='leg_circumference_left',
                                                    mode=mode,
                                                    params={
                                                        "max": MAX_SHIN_DEFAULT,
                                                        "min": MIN_SHIN_DEFAULT
                                                    },
                                                    timetable=timetable,
                                                    created_at=nowDate(),
                                                    updated_at=nowDate(),
                                                    last_push=toDate(0),
                                                    show=show)
            leg_circumference_right = CategoryParams(contract_id=contract_id,
                                                     category='leg_circumference_right',
                                                     mode=mode,
                                                     params={
                                                         "max": MAX_SHIN_DEFAULT,
                                                         "min": MIN_SHIN_DEFAULT
                                                     },
                                                     timetable=timetable,
                                                     created_at=nowDate(),
                                                     updated_at=nowDate(),
                                                     last_push=toDate(0),
                                                     show=show)

            if preset == 'heartfailure':
                leg_circumference_left.show = True
                leg_circumference_right.show = True

            if preset in ['fibrillation', 'heartfailure']:
                waist_circumference.show = True
                weight.show = True

            if preset in ['fibrillation', 'stenocardia', 'hypertensia', 'heartfailure']:
                systolic_pressure.show = True
                diastolic_pressure.show = True
                pulse.show = True

            db.session.add(leg_circumference_left)
            db.session.add(leg_circumference_right)
            db.session.add(systolic_pressure)
            db.session.add(diastolic_pressure)
            db.session.add(pulse)
            db.session.add(pain_assessment)
            db.session.add(spo2)
            db.session.add(waist_circumference)
            db.session.add(weight)
            db.session.add(glukose)
            db.session.add(temperature)
            db.session.commit()

    except:
        pass

    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    data = request.json
    contract_id = quard_data_json(data)
    query = ActualBots.query.filter_by(contract_id=contract_id)

    if query.count() != 0:
        contract = query.first()
        contract.actual = False
        db.session.commit()

        info_yellow('Deactivate contract')

        q = ContractTasks.query.filter_by(contract_id=contract_id)

        drop_tasks(contract_id)
    else:
        info_cyan('Contract not found')

    return 'ok'


@app.route('/frame/<string:pull>', methods=['POST'])
def action_pull_save(pull):
    task_id = 0
    param = ''
    param_value = ''

    contract_id = quard()

    if contract_id in ERRORS:
        return ERRORS[contract_id]

    if pull in AVAILABLE_MEASUREMENTS:
        param = pull
        param_value = request.form.get(param, '')
        comments = request.form.get('comments', '')

    if pull == 'shin':
        shin_left = request.form.get('shin_left', '')
        shin_right = request.form.get('shin_right', '')

        if False in map(check_digit, [shin_left, shin_right]):
            return ERROR_FORM

        try:
            shin_left = int(shin_left)
        except Exception as e:
            shin_left = MAX_SHIN_DEFAULT

        try:
            shin_right = int(shin_right)
        except Exception as e:
            shin_right = MAX_SHIN_DEFAULT

        if shin_left < MIN_SHIN or shin_left > MAX_SHIN:
            return ERROR_OUTSIDE_SHIN

        if shin_right < MIN_SHIN or shin_right > MAX_SHIN:
            return ERROR_OUTSIDE_SHIN

        try:
            query = CategoryParams.query.filter_by(contract_id=contract_id, category='leg_circumference_left')

            if query.count() != 0:
                contract = query.first()
                params = contract.params

            q = ContractTasks.query.filter_by(contract_id=contract_id, action_link='frame/' + pull)

            if q.count() != 0:
                task = q.first()
                task_id = task.task_id
        except Exception as e:
            error('Error frame/pull POST')
            print(e)

        try:
            max_shin = int(params['max'])
            min_shin = int(params['min'])
        except Exception as e:
            max_shin = MAX_SHIN
            min_shin = MIN_SHIN
            info_yellow("WARNING_NOT_INT")

        if (shin_left < min_shin or shin_left > max_shin) or (shin_right < min_shin or shin_right > max_shin):
            error('Сигналим врачу по голени')
            delayed(1, warning, [contract_id, 'shin', shin_left, shin_right])

        delayed(1, add_record, [contract_id, 'leg_circumference_left', shin_left, int(time.time())])
        delayed(1, add_record, [contract_id, 'leg_circumference_right', shin_right, int(time.time())])

        if task_id > 0:
            make_task(contract_id, task_id)
    elif pull == 'pressure':
        systolic = request.form.get('systolic', '')
        diastolic = request.form.get('diastolic', '')
        pulse_ = request.form.get('pulse_', '')

        if False in map(check_digit, [systolic, diastolic, pulse_]):
            return ERROR_FORM

        try:
            systolic = int(systolic)
        except Exception as e:
            systolic = 120

        try:
            diastolic = int(diastolic)
        except Exception as e:
            diastolic = 80

        try:
            pulse_ = int(pulse_)
        except Exception as e:
            pulse_ = 60

        if systolic < MIN_SYSTOLIC or systolic > MAX_SYSTOLIC:
            flash(ERROR_OUTSIDE_SYSTOLIC_TEXT)
            return action_pull(pull)

        if diastolic < MIN_DIASTOLIC or diastolic > MAX_DIASTOLIC:
            return ERROR_OUTSIDE_DIASTOLIC

        if pulse_ < MIN_PULSE or pulse_ > MAX_PULSE:
            return ERROR_OUTSIDE_PULSE

        query = CategoryParams.query.filter_by(contract_id=contract_id, category='systolic_pressure')

        if query.count() != 0:
            contract = query.first()
            params = contract.params

        q = ContractTasks.query.filter_by(contract_id=contract_id, action_link='frame/' + pull)

        if q.count() != 0:
            task = q.first()
            task_id = task.task_id

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

            out_red_light("WARNING_NOT_INT")

        if not (min_systolic <= systolic <= max_systolic and min_diastolic <= diastolic <= max_diastolic):
            error('Сигналим врачу по давлению')
            delayed(1, warning, [contract_id, 'pressure', systolic, diastolic])

        if not (min_pulse <= pulse_ <= max_pulse):
            error('Сигналим врачу по пульсу')
            delayed(1, warning, [contract_id, 'pulse', pulse_])

        delayed(1, add_record, [contract_id, 'systolic_pressure', systolic, int(time.time())])
        delayed(1, add_record, [contract_id, 'diastolic_pressure', diastolic, int(time.time())])
        delayed(1, add_record, [contract_id, 'pulse', pulse_, int(time.time())])

        if (task_id > 0):
            make_task(contract_id, task_id)
    else:
        if check_float(param_value) == False:
            error('ERROR_FORM')
            print('param_value = ', param_value)
            zzz = param_value.replace(',', '.')
            print('zzz = ', zzz)
            return ERROR_FORM

        category = pull

        if (pull == 'waist'):
            category = 'waist_circumference'

        try:
            q = CategoryParams.query.filter_by(contract_id=contract_id, category=category)

            if q.count() != 0:
                contract = q.first()
                params = contract.params

            action_link = 'frame/' + str(pull)
            q_ = ContractTasks.query.filter_by(contract_id=contract_id, action_link=action_link)

            if q_.count() != 0:
                task = q_.first()
                task_id = task.task_id

        except Exception as e:
            error('Error CategoryParams')
            print(e)

        try:
            max = params['max']
            min = params['min']
        except Exception as e:
            max = 0
            min = 0

        max = float(max)
        min = float(min)
        param_value = float(param_value.replace(',', '.'))

        if pull == 'spo2' and (param_value < MIN_SPO2 or param_value > MAX_SPO2):
            param_value_int = int(param_value)
            flash(ERROR_OUTSIDE_SPO2_TEXT, category=param_value_int)
            return action_pull(pull)

        if param == 'waist' and (param_value < MIN_WAIST or param_value > MAX_WAIST):
            param_value_int = int(param_value)
            flash(ERROR_OUTSIDE_WAIST_TEXT, category=param_value_int)
            return action_pull(pull)

        if param == 'weight' and (param_value < MIN_WEIGHT or param_value > MAX_WEIGHT):
            return ERROR_OUTSIDE_WEIGHT

        if param == 'glukose' and (param_value < MIN_GLUKOSE or param_value > MAX_GLUKOSE):
            return ERROR_OUTSIDE_GLUKOSE

        if param == 'temperature' and (param_value < MIN_TEMPERATURE or param_value > MAX_TEMPERATURE):
            return ERROR_OUTSIDE_TEMPERATURE

        param_for_record = param

        if param == 'waist':
            param_for_record = 'waist_circumference'

        if param == 'shin_volume_left':
            param_for_record = 'leg_circumference_left'

        if param == 'shin_volume_right':
            param_for_record = 'leg_circumference_right'

        if param_value < min or param_value > max:
            # Сигналим врачу
            out_yellow('Сигналим врачу')
            delayed(1, warning, [contract_id, param, param_value])

        delayed(1, add_record, [contract_id, param_for_record, param_value, int(time.time())])

        if task_id > 0:
            make_task(contract_id, task_id)

    return MESS_THANKS


@app.route('/message', methods=['POST'])
def save_message():
    data = request.json
    key = data['api_key']

    if key != APP_KEY:
        return ERROR_KEY

    return "ok"

@app.route('/report_medicines', methods=['GET'])
def report_medicines():
    contract_id = quard()
    contract = ActualBots.query.filter_by(contract_id=contract_id).first()

    if not contract:
        return "error"

    return render_template('report_medicines.html', contract=contract)

@app.route('/report_medicines', methods=['POST'])
def report_medicines_save():
    contract_id = quard()
    contract = ActualBots.query.filter_by(contract_id=contract_id).first()

    if not contract:
        return "error"

    contract.patient_medicines = request.form.get('medicines')
    db.session.commit()

    return MESS_THANKS



t = Thread(target=sender)
t.start()

app.run(port=PORT, host=HOST)
