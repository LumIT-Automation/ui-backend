from django.db import connection

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Database import Database as DBHelper
from ui_backend.helpers.Log import Log


class Privilege:

    # Table: privilege

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `privilege` varchar(64) NOT NULL UNIQUE KEY,
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> list:
        c = connection.cursor()
        try:
            c.execute("SELECT * FROM privilege")

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
