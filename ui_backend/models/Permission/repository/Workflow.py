from django.db import connection

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Database import Database as DBHelper


class Workflow:

    # Table: workflow

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `name` varchar(64) NOT NULL,
    #   `technologies` varchar(255) NOT NULL,
    #   `description` varchar(255) DEFAULT NULL
    #
    #    UNIQUE KEY `name` (`name`);



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int = 0, name: str = "") -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT * FROM `workflow` WHERE id = %s", [id])
            if name:
                c.execute("SELECT * FROM `workflow` WHERE `name` = %s", [name])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent workflow"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM workflow")
            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
