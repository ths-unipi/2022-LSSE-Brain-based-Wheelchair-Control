from src.monitoring_system import MonitoringSystem
from src.json_io import JsonIO
from threading import Thread



if __name__ == '__main__':

    MonitoringSystem().run()
'''
    new_thread = Thread(target=MonitoringSystem.get_instance().run, args=())
    new_thread.start()

    # start the listener
    JsonIO.get_instance().listener("0.0.0.0", "5000")
'''