import Task
import numpy as np
import Config
class Mvn:
    def __init__(self,id_bus,frequency,coordinates,delta_time):
        self.frequency=frequency
        self.task=[]
        self.coordinates=coordinates
        self.delta_time=delta_time
        self.id_bus=id_bus
        self.nn=0
        self.id=-2
    def get_frequency(self):
        return self.frequency
    def set_frequency(self,frequency):
        self.frequency=frequency
    def get_rm(self):
        return self.nn
    def set_rm(self):
        rms=[]
        for i in self.coordinates:
            di=np.around(np.sqrt(np.power(i[0]-Config.X0,2)+np.power(i[1]-Config.Y0,2))*0.3048/1000,1)
            rms.append((pow(2,-Config.Rm/Config.W)-1)*Config.o2/(pow(di,-Config.a)))
        self.nn=np.round(np.average(rms))
    def get_task(self):
        return self.task
    def set_task(self,task):
        self.task=task
    def get_coordinates(self):
        return self.coordinates
    def set_coordinates(self,coordinates):
        self.coordinates=coordinates
    def get_delta_time(self):
        return self.delta_time
    def set_delta_time(self,delta_time):
        self.delta_time=delta_time
    def get_id(self):
        return self.id
    def set_id(self,id):
        self.id=id