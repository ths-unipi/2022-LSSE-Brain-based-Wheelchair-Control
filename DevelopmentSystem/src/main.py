import sys
from threading import Thread
from src.development_system import DevelopmentSystem
from src.json_io import JsonIO


if __name__ == '__main__':
    # start the development system controller
    DevelopmentSystem().run()
