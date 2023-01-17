from threading import Thread
from src.development_system import DevelopmentSystem
from src.json_io import JsonIO


if __name__ == '__main__':
    # new thread for development system execution
    run_thread = Thread(target=DevelopmentSystem().run, args=())
    run_thread.start()

    # rest server in main thread
    JsonIO.get_instance().listen('0.0.0.0', 5000)
