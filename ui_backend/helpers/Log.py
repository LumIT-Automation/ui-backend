import logging
import traceback
from datetime import datetime
from django.conf import settings


class Log:
    @staticmethod
    def log(o: any, title: str = "") -> None:
        # Sends input logs to the "ui_backend" logger (settings).
        log = logging.getLogger("django")
        if title:
            if title == "_":
                for j in range(80):
                    title = title + "_"
            log.debug(title)

        log.debug(o)

        if title:
            log.debug(title)



    @staticmethod
    def logException(e: Exception) -> None:
        # Logs the stack trace information and the raw output if any.
        Log.log(traceback.format_exc(), 'Error')

        try:
            Log.log(e.raw, 'Raw AWX data')
        except Exception:
            pass



    @staticmethod
    def actionLog(o: any, user: dict = {}) -> None:
        # Sends input logs to the "awx" logger (settings).
        log = logging.getLogger("django")
        if not ("username" in user):
            user['username'] = "system"

        log.debug("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + settings.TIME_ZONE + "] " + "[" + user['username'] + "] " + o)
