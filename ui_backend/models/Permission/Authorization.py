from ui_backend.models.Permission.IdentityGroup import IdentityGroup

from ui_backend.helpers.Log import Log


class Authorization:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groups: list) -> dict:
        permissions = list()
        combinedPermissions = dict()

        # Superadmin's permissions override.
        for gr in groups:
            if gr.lower() == "automation.local":
                combinedPermissions = {
                    "any": [
                        {
                            "workflow_id": 0,
                            "workflow_name": "any"
                        }
                    ]
                }

        if not combinedPermissions:
            o = IdentityGroup.listWithRelated(True)

            # Collect every permission related to the group in groups.
            for identityGroup in groups:
                for el in o:
                    if "identity_group_identifier" in el:
                        if el["identity_group_identifier"].lower() == identityGroup.lower():
                            permissions.append(el["privileges_workflow"])

            # Clean up structure.
            for el in permissions:
                for k, v in el.items():

                    # Initialize list if not already done.
                    if not str(k) in combinedPermissions:
                        combinedPermissions[k] = list()

                    for innerEl in v:
                        if innerEl not in combinedPermissions[k]:
                            combinedPermissions[k].append(innerEl)

            # {
            #     'exec': [
            #         {'workflow_id': '2', 'workflow_name': 'stub'},
            #         {'workflow_id': '1', 'workflow_name': 'checkpoint_remove_host'}
            #      ]
            # }

        return combinedPermissions
