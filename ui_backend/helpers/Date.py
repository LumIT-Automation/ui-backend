from datetime import datetime
from random import randrange


class Date:
    @staticmethod
    def getWorkflowId() -> str:
        return str(datetime.now().strftime("%Y%m%d:%H%M-")) + str(randrange(0, 9999))
