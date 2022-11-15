from ui_backend.models.Asset.repository.ApiAsset import ApiAsset as Repository
from ui_backend.helpers.Log import Log


class ApiAsset:
    def __init__(self, technology, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.technology = technology
        self.id = int(assetId)
        self.address = ""
        self.fqdn = ""
        self.baseurl = ""
        self.tlsverify = ""
        self.datacenter = ""
        self.environment = ""
        self.position = ""

        self.__load()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(technology: str) -> list:
        try:
            return Repository.getApiAssets(technology)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            data = Repository.getApiAssets(self.technology)
            for assetData in data:
                if assetData["id"] == self.id:
                    for k, v in assetData.items():
                        setattr(self, k, v)
        except Exception as e:
            raise e
