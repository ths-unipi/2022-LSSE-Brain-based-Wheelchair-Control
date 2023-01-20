RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
YELLOW_COLOR = "\033[93m"
BLUE_COLOR = "\033[94m"
PURPLE_COLOR = "\033[95m"
CYAN_COLOR = "\033[96m"
WHITE_COLOR = "\033[97m"
DEFAULT_COLOR = WHITE_COLOR


def red(string):
    return RED_COLOR + string + DEFAULT_COLOR


def blue(string):
    return BLUE_COLOR + string + DEFAULT_COLOR


def green(string):
    return GREEN_COLOR + string + DEFAULT_COLOR


def cyan(string):
    return CYAN_COLOR + string + DEFAULT_COLOR


def yellow(string):
    return YELLOW_COLOR + string + DEFAULT_COLOR
