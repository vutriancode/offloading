class Task:
    def __init__(self, di, wi, response):
        self.di = di
        self.wi = wi
        self.server_id = -2
        self.response = response

    def get_di(self):
        return self.di

    def set_di(self, di):
        self.di = di

    def get_wi(self):
        return self.wi

    def set_wi(self, wi):
        self.wi = wi

    def get_res(self):
        return self.response

    def set_res(self, wi):
        self.response = wi
