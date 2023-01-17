from threading import Thread
from src.json_io import JsonIO
from src.segregation_system import SegregationSystem


if __name__ == '__main__':

    segregation_system = Thread(target=SegregationSystem.get_instance().run, args=())
    segregation_system.start()

    JsonIO.get_instance().listener("0.0.0.0", "5000")



