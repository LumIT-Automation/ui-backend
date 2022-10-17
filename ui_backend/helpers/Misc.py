from datetime import datetime
from random import randrange


class Misc:
    @staticmethod
    def getWorkflowCorrelationId() -> str:
        return str(datetime.now().strftime("%Y%m%d:%H%M-")) + str(randrange(0, 9999))
