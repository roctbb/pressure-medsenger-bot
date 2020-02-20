ERROR_KEY = "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
ERROR_CONTRACT = "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."
ERROR_FORM = "<strong>Ошибки при заполнении формы.</strong> Пожалуйста, что все поля заполнены.<br><a class='btn btn-success' onclick='history.go(-1);'>Назад</a>"

ERRORS = {'ERROR_KEY': ERROR_KEY, 'ERROR_CONTRACT': ERROR_CONTRACT, 'ERROR_FORM': ERROR_FORM}

MESS_THANKS = """<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"""
MESS_GLUKOSE_PATIENT = "Ваш уровень глюкозы ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_GLUKOSE_DOCTOR = "Уровень глюкозы пациента ({}) выходит за допустимый диапазон."

MESS_WEIGHT_PATIENT = "Ваш вес ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_WEIGHT_DOCTOR = "Вес пациента ({}) выходит за допустимый диапазон."

MESS_TEMPERATURE_PATIENT = "Ваша температура ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_TEMPERATURE_DOCTOR = "Температура пациента ({}) выходит за допустимый диапазон."

MESS_PRESSURE_PATIENT = "Ваше давление ({} / {}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_PRESSURE_DOCTOR = "Давление пациента ({} / {}) выходит за допустимый диапазон."

MESS_PRESSURE_REMINDER = "Не забудьте померить давление сегодня."
MESS_PRESSURE_TITLE = "Записать давление"

MESS_TEMPERATURE_REMINDER = "Не забудьте померить температуру сегодня."
MESS_TEMPERATURE_TITLE = "Записать температуру"

MESS_WEIGHT_REMINDER = "Не забудьте измерить вес сегодня."
MESS_WEIGHT_TITLE = "Записать вес"

MESS_GLUKOSE_REMINDER = "Не забудьте проверить уровень глюкозы."
MESS_GLUKOSE_TITLE = "Уровень глюкозы"

MESS_MEDICINE = {'text': 'Не забудьте принять лекарство, назначенное врачом.', 'action_link': 'medicine/{}', 'action_name': 'Подтвердить прием: {0} {1}'}
MESS_MEASUREMENT = {
    'pressure': {'text': MESS_PRESSURE_REMINDER, 'action_name': MESS_PRESSURE_TITLE},
    'weight': {'text': MESS_WEIGHT_REMINDER, 'action_name': MESS_WEIGHT_TITLE},
    'glukose': {'text': MESS_GLUKOSE_REMINDER, 'action_name': MESS_GLUKOSE_TITLE},
    'temperature': {'text': MESS_TEMPERATURE_REMINDER, 'action_name': MESS_TEMPERATURE_TITLE},
}
NONE_MEASUREMENTS = "<strong>Измерений еще не проводилось.</strong>"

AVAILABLE_MEASUREMENTS = ['pressure', 'weight', 'glukose', 'temperature']
AVAILABLE_MODES = ['daily', 'weekly', 'monthly', 'none']
FORM_INPUTS = ['systolic', 'diastolic', 'weight', 'pulse_', 'glukose']