from datetime import datetime

import dependency


@dependency.requires("time_api")
class TimeDisplayClient():
    def __init__(self):
        pass

    def get_current_time(self):
        return self.time_api.now()


@dependency.provider("time_api")
class TimeAPI():
    def __init__(self):
        pass

    def now(self):
        return datetime.utcnow()


if __name__ == "__main__":
    TimeAPI()
    print(TimeDisplayClient().get_current_time())
