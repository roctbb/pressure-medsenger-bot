from colorama import Fore, Back, Style

def out_red(text):
    print(Fore.RED + str(text))
    print(Style.RESET_ALL)
def out_red_light(text):
    print(Fore.LIGHTRED_EX + str(text))
    print(Style.RESET_ALL)
def out_yellow(text):
    # print("\033[33m {}".format(text))
    print(Fore.YELLOW + str(text))
    print(Style.RESET_ALL)
def out_blue(text):
    print(Fore.BLUE + str(text))
    print(Style.RESET_ALL)
def out_green(text):
    print(Fore.GREEN + str(text))
    print(Style.RESET_ALL)
def out_green_light(text):
    print(Fore.LIGHTGREEN_EX + str(text))
    print(Style.RESET_ALL)
def out_cyan_light(text):
    print(Fore.LIGHTCYAN_EX + str(text))
    print(Style.RESET_ALL)
def out_magenta_light(text):
    print(Fore.LIGHTMAGENTA_EX + str(text))
    print(Style.RESET_ALL)