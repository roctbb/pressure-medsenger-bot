import threading
# from flask_bootstrap import Bootstrap

class Debug:
    @staticmethod
    def delimiter():
        return '-------------------------------------------------------------------------------'


class Aux:
    @staticmethod
    def quote():
        return "'"

    @staticmethod
    def doublequote():
        return '"'

def dump(data, label):
    print('dump: ' + label + ' ', data)


def delayed(delay, f, args):
    timer = threading.Timer(delay, f, args=args)
    timer.start()


def check_float(number):
    try:
        number = number.replace(',', '.')
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


def check_str(val):
    try:
        str(str)
        return True
    except:
        return False