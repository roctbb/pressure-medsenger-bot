backhistory = "<br><a style='font-family: Arial; cursor: pointer; border: 0px solid #ccc; top-padding: 3px;' class='btn btn-success' onclick='history.go(-1);'><strong><< Назад</strong></a>"
open_tag = "<p style='font-family: Arial;'>"
close_tag = "</p>"

DATE_HOUR_FORMAT = '%Y-%m-%d %H:%M:%S'
STOP_LIST = ['diastolic_pressure', 'pulse', 'leg_circumference_right']



CATEGORY_TRNSFORM = ['', '', '', '', '']
CATEGORY_TEXT = {
    'leg_circumference_right':'Обхват голени',
    'leg_circumference_left':'Обхват голени',
    'pain_assessment':'Оценка боли',
    'spo2':'Мониторинг насыщения крови кислородом',
    'waist_circumference':'Окружность талии',
    'weight':'Вес',
    'glukose':'Глюкоза',
    'temperature':'Температура',
    'pulse':'Пульс в покое',
    'diastolic_pressure':'Диастолическое (нижнее) артериальное давление',
    'systolic_pressure':'Артериальное давление',
    'pressure': 'Давление'
}

MAX_SPO2 = 100
MIN_SPO2 = 50
MAX_WAIST = 250
MIN_WAIST = 30
MAX_WEIGHT = 400
MIN_WEIGHT = 1
MAX_TEMPERATURE = 42
MIN_TEMPERATURE = 35
MAX_SYSTOLIC = 270
MIN_SYSTOLIC = 80
MAX_DIASTOLIC = 150
MIN_DIASTOLIC = 20
MAX_PULSE = 250
MIN_PULSE = 30
MAX_GLUKOSE = 30
MIN_GLUKOSE = 1
MAX_SHIN = 50
MIN_SHIN = 5
MAX_PAIN = 10
MIN_PAIN = 0

MAX_SHIN_DEFAULT = 35
MIN_SHIN_DEFAULT = 10

MAX_WEIGHT_DEFAULT = 250
MIN_WEIGHT_DEFAULT = 0

MAX_SYSTOLIC_DEFAULT = 180
MIN_SYSTOLIC_DEFAULT = 80

MAX_DIASTOLIC_DEFAULT = 120
MIN_DIASTOLIC_DEFAULT = 50

MAX_PULSE_DEFAULT = 120
MIN_PULSE_DEFAULT = 40

MAX_TEMPERATURE_DEFAULT = 37
MIN_TEMPERATURE_DEFAULT = 36

MAX_GLUKOSE_DEFAULT = 6.5
MIN_GLUKOSE_DEFAULT = 4

MAX_PAIN_DEFAULT = 7
MIN_PAIN_DEFAULT = 0

MAX_SPO2_DEFAULT = 100
MIN_SPO2_DEFAULT = 93

MAX_WAIST_DEFAULT = 150
MIN_WAIST_DEFAULT = 30

MAX_ASSESSMENT = 10
MIN_ASSESSMENT = 0

TASK_HOUR = 3

ERROR_KEY = open_tag + "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой." + close_tag
ERROR_CONTRACT = open_tag + "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой." + close_tag
ERROR_FORM = open_tag + "<strong>Ошибки при заполнении формы.<br></strong> Пожалуйста, проверьте, что все поля заполнены." + close_tag + backhistory

ERROR_OUTSIDE_TEMPERATURE_TEXT = "Допустимый диапазон температуры " + str(MIN_TEMPERATURE) + "-" + str(MAX_TEMPERATURE) + " градуса по Цельсию."
ERROR_OUTSIDE_TEMPERATURE = open_tag + ERROR_OUTSIDE_TEMPERATURE_TEXT + close_tag + backhistory

ERROR_OUTSIDE_SYSTOLIC_TEXT = "Допустимый диапазон верхнего давления " + str(MIN_SYSTOLIC) + "-" + str(MAX_SYSTOLIC) + " мм рт ст."
ERROR_OUTSIDE_SYSTOLIC = open_tag + ERROR_OUTSIDE_SYSTOLIC_TEXT + close_tag + backhistory

ERROR_OUTSIDE_DIASTOLIC_TEXT = open_tag + "Допустимый диапазон нижнего давления " + str(MIN_DIASTOLIC) + "-" + str(MAX_DIASTOLIC) + " мм рт ст." + close_tag + backhistory
ERROR_OUTSIDE_DIASTOLIC = open_tag + ERROR_OUTSIDE_DIASTOLIC_TEXT + close_tag + backhistory

ERROR_OUTSIDE_PULSE_TEXT = "Допустимый диапазон пульса " + str(MIN_PULSE) + "-" + str(MAX_PULSE) + " ударов в минуту."
ERROR_OUTSIDE_PULSE = open_tag + ERROR_OUTSIDE_PULSE_TEXT + close_tag + backhistory

ERROR_OUTSIDE_WEIGHT_TEXT = "Допустимый диапазон измерений веса " + str(MIN_WEIGHT) + "-" + str(MAX_WEIGHT) + " кг."
ERROR_OUTSIDE_WEIGHT = open_tag + ERROR_OUTSIDE_WEIGHT_TEXT + close_tag + backhistory

ERROR_OUTSIDE_GLUKOSE_TEXT = "Допустимый диапазон показаний глюкозы " + str(MIN_GLUKOSE) + "-" + str(MAX_GLUKOSE) + " моль/л."
ERROR_OUTSIDE_GLUKOSE = open_tag + ERROR_OUTSIDE_GLUKOSE_TEXT + close_tag + backhistory

ERROR_OUTSIDE_SPO2_TEXT = "Допустимый уровень насыщения не менее " + str(MIN_SPO2) + "% и не более 100%."
ERROR_OUTSIDE_SPO2 = open_tag + ERROR_OUTSIDE_SPO2_TEXT + close_tag + backhistory

ERROR_OUTSIDE_WAIST_TEXT = "Допустимый обхват талии " + str(MIN_WAIST) + "-" + str(MAX_WAIST) + " см."
ERROR_OUTSIDE_WAIST = open_tag + ERROR_OUTSIDE_WAIST_TEXT + close_tag + backhistory

ERROR_OUTSIDE_SHIN_TEXT = "Допустимый диапазон измерения обхвата голени " + str(MIN_SHIN) + "-" + str(MAX_SHIN) + " см."
ERROR_OUTSIDE_SHIN = open_tag + ERROR_OUTSIDE_SHIN_TEXT + close_tag + backhistory

ERRORS = {'ERROR_KEY': ERROR_KEY, 'ERROR_CONTRACT': ERROR_CONTRACT, 'ERROR_FORM': ERROR_FORM}



MESS_THANKS = "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"
MESS_GLUKOSE_PATIENT = "Ваш уровень глюкозы ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_GLUKOSE_DOCTOR = "Уровень глюкозы пациента ({}) выходит за допустимый диапазон."

MESS_WEIGHT_PATIENT = "Ваш вес ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_WEIGHT_DOCTOR = "Вес пациента ({}) выходит за допустимый диапазон."

MESS_PAIN_PATIENT = "Ваша оценка болевых ощущений ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_PIAN_DOCTOR = "Оценка болевых ощущений пациента ({}) выходит за допустимый диапазон."

MESS_TEMPERATURE_PATIENT = "Ваша температура ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_TEMPERATURE_DOCTOR = "Температура пациента ({}) выходит за допустимый диапазон."

MESS_PRESSURE_PATIENT = "Ваше давление ({} / {}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_PRESSURE_DOCTOR = "Давление пациента ({} / {}) выходит за допустимый диапазон."

MESS_PULSE_PATIENT = "Ваш пульс ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_PULSE_DOCTOR = "Пульс пациента ({}) выходит за допустимый диапазон."

MESS_SPO2_PATIENT = "Ваш уровень насыщения крови кислородом ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_SPO2_DOCTOR = "Уровень насыщения крови кислородом пациента ({}) выходит за допустимый диапазон."

MESS_WAIST_PATIENT = "Окружность талии ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_WAIST_DOCTOR = "Окружность талии пациента ({}) выходит за допустимый диапазон."

MESS_SHIN_PATIENT = "Ваш обхват голени ({} / {}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_SHIN_DOCTOR = "Обхват голени пациента ({} / {}) выходит за допустимый диапазон."



MESS_PRESSURE_REMINDER = "Не забудьте измерить давление сегодня."
MESS_PRESSURE_TITLE = "Записать давление"

MESS_TEMPERATURE_REMINDER = "Не забудьте измерить температуру сегодня."
MESS_TEMPERATURE_TITLE = "Записать температуру"

MESS_WEIGHT_REMINDER = "Не забудьте измерить вес сегодня."
MESS_WEIGHT_TITLE = "Записать вес"

MESS_GLUKOSE_REMINDER = "Не забудьте проверить уровень глюкозы."
MESS_GLUKOSE_TITLE = "Уровень глюкозы"

MESS_PAIN_REMINDER = "Не забудьте оценить болевые ощущения."
MESS_PAIN_TITLE = "Оценка болевых ощущений"

MESS_SPO2_REMINDER = "Не забудьте проверить уровень насыщения крови кислородом."
MESS_SPO2_TITLE = "Насыщение крови кислородом"

MESS_WAIST_REMINDER = "Не забудьте измерить окружность талии."
MESS_WAIST_TITLE = "Окружность талии"

MESS_MEDICINE = {'text': 'Не забудьте принять лекарство, назначенное врачом.', 'action_link': 'medicine/{}', 'action_name': 'Подтвердить прием: {0} {1}'}

MESS_SHIN_REMINDER = "Не забудьте измерить обхват голени."
MESS_SHIN_TITLE = "Записать обхват голени"



MESS_MEASUREMENT = {
    'waist': {'text': MESS_WAIST_REMINDER, 'action_name': MESS_WAIST_TITLE},
    'spo2': {'text': MESS_SPO2_REMINDER, 'action_name': MESS_SPO2_TITLE},
    'pain_assessment': {'text': MESS_PAIN_REMINDER, 'action_name': MESS_PAIN_TITLE},
    'systolic_pressure': {'text': MESS_PRESSURE_REMINDER, 'action_name': MESS_PRESSURE_TITLE},
    'diastolic_pressure': {'text': MESS_PRESSURE_REMINDER, 'action_name': MESS_PRESSURE_TITLE},
    'pulse': {'text': MESS_PRESSURE_REMINDER, 'action_name': MESS_PRESSURE_TITLE},
    'pressure': {'text': MESS_PRESSURE_REMINDER, 'action_name': MESS_PRESSURE_TITLE},
    'weight': {'text': MESS_WEIGHT_REMINDER, 'action_name': MESS_WEIGHT_TITLE},
    'glukose': {'text': MESS_GLUKOSE_REMINDER, 'action_name': MESS_GLUKOSE_TITLE},
    'temperature': {'text': MESS_TEMPERATURE_REMINDER, 'action_name': MESS_TEMPERATURE_TITLE},
    'shin': {'text': MESS_SHIN_REMINDER, 'action_name': MESS_SHIN_TITLE},
}

NONE_MEASUREMENTS = "<strong>Измерений еще не проводилось.</strong>"



AVAILABLE_MEASUREMENTS = ['pressure', 'pulse', 'weight', 'glukose', 'temperature', 'pain_assessment', 'spo2', 'waist', 'shin']
AVAILABLE_MODES = ['daily', 'weekly', 'monthly', 'none']
FORM_INPUTS = ['systolic', 'diastolic', 'weight', 'pulse_', 'glukose', 'spo2', 'waist', 'shin']
SUPPORTED_SCENARIOS = ['heartfailure', 'stenocardia', 'fibrillation']