from config import *
import requests
from classes.colorok import *
# from init import db

def add_task(contract_id, text, target_number=1, date=None, important=False, action_link=None):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "text": text,
        "number": target_number,
        "important": important
    }

    if date:
        data['date'] = date

    if action_link:
        data['action_link'] = action_link

    print('data = ', MAIN_HOST, data)

    try:
        response = requests.post(MAIN_HOST + '/api/agents/tasks/add', json=data)
        print('add_task response = ', response)
        answer = response.json()
        print('add_task answer = ', answer)
        return answer['task_id']
    except Exception as e:
        error('Error in method add_task()')
        print(e)

def make_task(contract_id, task_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "task_id": task_id,
    }

    try:
        answer = requests.post(MAIN_HOST + '/api/agents/tasks/done', json=data).json()

        info_green('success make_task()')
        print(answer)

        return answer['is_done']

    except Exception as e:
        error('Error function make_task()')
        print(e)

def delete_task(contract_id, task_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "task_id": task_id,
    }

    try:
        requests.post(MAIN_HOST + '/api/agents/tasks/delete', json=data)
        print('success delete_task')
    except Exception as e:
        print('error delete_task', e)

# def delete_all_task(contract_id):
#     data = {
#         "contract_id": contract_id,
#         "api_key": APP_KEY,
#         "task_id": task_id,
#     }
#
#     try:
#         requests.post(MAIN_HOST + '/api/agents/tasks/delete', json=data)
#         print('success delete_task')
#     except Exception as e:
#         print('error delete_task', e)

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
        print('connection error', e)

def get_records(contract_id, category_name, time_from=None, time_to=None, limit=None, offset=None):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "category_name": category_name,
    }

    if limit:
        data['limit'] = limit
    if offset:
        data['offset'] = offset
    if time_from:
        data['from'] = time_from
    if time_to:
        data['to'] = time_to

    try:
        result = requests.post(MAIN_HOST + '/api/agents/records/get', json=data)
        return result.json()
    except Exception as e:
        print('connection error', e)
        return {}