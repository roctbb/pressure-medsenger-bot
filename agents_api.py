from config import *
import requests
# from init import db

def add_task(contract_id, text, number=1, date=None, important=False, action_link=None):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "text": text,
        "number": number,
        "important": important
    }

    if date:
        data['date'] = date

    if action_link:
        data['action_link'] = action_link

    try:
        response = requests.post(MAIN_HOST + '/api/agents/tasks/add', json=data)
        print('add_task response = ', response)
        answer = response.json()
        print('add_task answer = ', answer)
        return answer['task_id']
    except Exception as e:
        print('connection error', e)

def make_task(contract_id, task_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "task_id": task_id,
    }

    try:
        answer = requests.post(MAIN_HOST + '/api/agents/tasks/done', json=data).json()

        print('success answer = ', answer)

        return answer['is_done']

    except Exception as e:
        print('error make_task: ', e)

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

def delete_all_task(contract_id):
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