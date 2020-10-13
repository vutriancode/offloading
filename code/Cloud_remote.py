import Task
class Cloud_remote:
    def __init__(self,frequency,r):
        self.frequency=frequency
        self.tasks=[]
        self.r=r
    def get_frequency(self):
        return self.frequency
    def set_frequency(self,frequency):
        self.frequency=frequency
    def get_tasks(self):
        return self.tasks
    def set_tasks(self,tasks):
        self.task=tasks
    def get_r(self):
        return self.r
    def set_r(self,r):
        self.r=r