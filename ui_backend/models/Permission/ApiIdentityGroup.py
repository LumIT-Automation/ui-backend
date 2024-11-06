from ui_backend.models.Permission.backend.ApiIdentityGroup import ApiIdentityGroup as Backend


class ApiIdentityGroup:



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################
    @staticmethod
    def add(username: str, data: dict, headers: dict = None) -> dict:
        headers = headers or {}

        try:
            return Backend.add(username, data, headers)
        except Exception as e:
            raise e



    @staticmethod
    def list(username: str, headers: dict = None) -> list:
        headers = headers or {}

        try:
            return Backend.list(username, headers)
        except Exception as e:
            raise e
