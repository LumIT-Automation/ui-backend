from ui_backend.models.Permission.backend.ApiIdentityGroup import ApiIdentityGroup as Backend


class ApiIdentityGroup:
    def __init__(self, identityGroupIdentifier: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.identity_group_identifier: str = identityGroupIdentifier
        self.technologies: list = []



    ####################################################################################################################
    # Public methods
    ####################################################################################################################
    """
    def add(self, data: dict) -> dict:
        try:
            for technology in self.technologies:
                if technology not in data.keys():
                    raise CustomException(status=400, payload={"UI-BACKEND": "Add identity group data: missing technology "+str(technology)+"."})

            return Backend.add(self.username, self.technologies, self.headers, data)
        except Exception as e:
            raise e
    """


    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(username: str, headers: dict = None) -> list:
        headers = headers or ()

        try:
            return Backend.list(username, headers)
        except Exception as e:
            raise e
