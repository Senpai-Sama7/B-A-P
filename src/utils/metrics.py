import time

class Metrics:
    def __init__(self):
        self.metrics = {}

    def record(self, name: str, value: float):
        self.metrics[name] = value

    def get(self, name: str):
        return self.metrics.get(name)

metrics = Metrics()
