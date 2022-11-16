from django.conf import settings

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



    @staticmethod
    def listWorkflowAssets(groups: list, workflow: str, role: str="exec") -> list:
        from ui_backend.models.Permission.Permission import Permission
        allowedAssets = dict()
        assets = list()
        techs = list()

        try:
            for k in settings.API_BACKEND_BASE_URL.keys():
                techs.append(k)

            # Superadmin's group.
            for gr in groups:
                if gr.lower() == "automation.local":
                    for tech in techs:
                        allowedAssets[tech] = "any"

            if not allowedAssets:

                perm = Permission.permissionsDataList(filter={"identityGroups": groups, "role": role, "workflow": workflow})
                details = perm[0]["details"]
                for tech in techs:
                    if tech in details:
                        allowedAssets[tech] = details[tech].get("allowed_asset_ids", [])

            # Filter the technology assets list by allowedAssetIds. Superadmin get all the assets.
            for tech in allowedAssets.keys():
                try:
                    assetsTech = Repository.getApiAssets(tech)
                except Exception:
                    assetsTech = []
                    pass

                if allowedAssets[tech] == "any":
                    assets.extend(a for a in assetsTech if a not in assets)
                else:
                    for a in assetsTech:
                        if a["id"] in allowedAssets[tech] and a not in assets:
                            assets.append(a)

            return assets
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
