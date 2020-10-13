import Task
class Server:
    def __init__(self,frequency):
        self.frequency=frequency
        self.tasks=[]
    def get_frequency(self):
        return self.frequency
    def set_frequency(self,frequency):
        self.frequency=frequency
    def get_tasks(self):
        return self.tasks
    def set_tasks(self,tasks):
        self.task=tasks