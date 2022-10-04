from django.db import connection

from ui_backend.helpers.Log import Log
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Database import Database as DBHelper


class Role:

    # Table: role

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `role` varchar(64) NOT NULL UNIQUE KEY,
    #   `description` varchar(255) DEFAULT NULL



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(roleName: str) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM role WHERE role = %s", [
                roleName
            ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM role")
            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
