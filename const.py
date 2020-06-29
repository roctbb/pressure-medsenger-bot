backhistory = "<br><a style='font-family: Arial; cursor: pointer; border: 0px solid #ccc; top-padding: 3px;' class='btn btn-success' onclick='history.go(-1);'><strong><< Назад</strong></a>"
open_tag = "<p style='font-family: Arial;'>"

ERROR_KEY = "<p style='font-family: Arial;'><strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой.</p>"
ERROR_CONTRACT = "<p style='font-family: Arial;'><strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой.</p>"
ERROR_FORM = "<p style='font-family: Arial;'><strong>Ошибки при заполнении формы.<br></strong> Пожалуйста, проверьте, что все поля заполнены.</p>" + backhistory

ERROR_OUTSIDE_TEMPERATURE = "<p style='font-family: Arial;'>Допустимый диапазон температуры 35-42 градуса по Цельсию.</p>" + backhistory
ERROR_OUTSIDE_SYSTOLIC = "<p style='font-family: Arial;'>Допустимый диапазон верхнего давления 40-300 мм рт ст.</p>" + backhistory
ERROR_OUTSIDE_DIASTOLIC = "<p style='font-family: Arial;'>Допустимый диапазон нижнего давления 15-150 мм рт ст.</p>" + backhistory
ERROR_OUTSIDE_PULSE = "<p style='font-family: Arial;'>Допустимый диапазон пульса 10-200 уд в мин.</p>" + backhistory
ERROR_OUTSIDE_WEIGHT = "<p style='font-family: Arial;'>Допустимый диапазон измерений веса 2-150 кг.</p>" + backhistory
ERROR_OUTSIDE_GLUKOSE = "<p style='font-family: Arial;'>Допустимый диапазон показаний глюкозы 1-30 моль/л.</p>" + backhistory
ERROR_OUTSIDE_SPO2 = "<p style='font-family: Arial;'>Допустимый уровень насыщения крови кислородом не менее 50%.</p>" + backhistory
ERROR_OUTSIDE_WAIST = "<p style='font-family: Arial;'>Допустимый объем талии не более 120 см, не менее 25 см.</p>" + backhistory
ERROR_OUTSIDE_SHIN = "Допустимый диапазон измерения объема голени от 5 см до 50 см." + backhistory
ERRORS = {'ERROR_KEY': ERROR_KEY, 'ERROR_CONTRACT': ERROR_CONTRACT, 'ERROR_FORM': ERROR_FORM}



MESS_THANKS = """<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"""
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

MESS_SPO2_PATIENT = "Ваш уровень насыщения крови кислородом ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_SPO2_DOCTOR = "Уровень насыщения крови кислородом пациента ({}) выходит за допустимый диапазон."

MESS_WAIST_PATIENT = "Ваш объем талии ({}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_WAIST_DOCTOR = "Объем талии пациента ({}) выходит за допустимый диапазон."

MESS_SHIN_PATIENT = "Ваш объем голени ({} / {}) выходит за допустимый диапазон. Мы уже направили уведомление вашему врачу."
MESS_SHIN_DOCTOR = "Объем голени пациента ({} / {}) выходит за допустимый диапазон."



MESS_PRESSURE_REMINDER = "Не забудьте померить давление сегодня."
MESS_PRESSURE_TITLE = "Записать давление"

MESS_TEMPERATURE_REMINDER = "Не забудьте померить температуру сегодня."
MESS_TEMPERATURE_TITLE = "Записать температуру"

MESS_WEIGHT_REMINDER = "Не забудьте измерить вес сегодня."
MESS_WEIGHT_TITLE = "Записать вес"

MESS_GLUKOSE_REMINDER = "Не забудьте проверить уровень глюкозы."
MESS_GLUKOSE_TITLE = "Уровень глюкозы"

MESS_PAIN_REMINDER = "Не забудьте оценить болевые ощущения."
MESS_PAIN_TITLE = "Оценка болевых ощущений"

MESS_SPO2_REMINDER = "Не забудьте проверить уровень насыщения крови кислородом."
MESS_SPO2_TITLE = "Насыщение крови кислородом"

MESS_WAIST_REMINDER = "Не забудьте измерить объем талии."
MESS_WAIST_TITLE = "Объем талии для сердечно-сосудистых пациентов"

MESS_MEDICINE = {'text': 'Не забудьте принять лекарство, назначенное врачом.', 'action_link': 'medicine/{}', 'action_name': 'Подтвердить прием: {0} {1}'}

MESS_SHIN_REMINDER = "Не забудьте измерить объем голени."
MESS_SHIN_TITLE = "Записать объем голени"



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



AVAILABLE_MEASUREMENTS = ['pressure', 'weight', 'glukose', 'temperature', 'pain_assessment', 'spo2', 'waist', 'shin']
AVAILABLE_MODES = ['daily', 'weekly', 'monthly', 'none']
FORM_INPUTS = ['systolic', 'diastolic', 'weight', 'pulse_', 'glukose', 'spo2', 'waist', 'shin']