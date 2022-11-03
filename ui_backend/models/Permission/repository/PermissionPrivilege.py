import json
from typing import List, Dict

from django.db import connection

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Database import Database as DBHelper


class PermissionPrivilege:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(filterGroups: list = None, showPrivileges: bool = False) -> list:
        # List identity groups with related information, and optionally detailed privileges' descriptions.
        filterGroups = filterGroups or []
        groupWhere = ""
        j = 0

        c = connection.cursor()

        try:
            # Build WHERE clause when filterGroups is specified.
            if filterGroups:
                groupWhere = "WHERE ("
                for _ in filterGroups:
                    groupWhere += "identity_group.identity_group_identifier = %s || "
                groupWhere = groupWhere[:-4] + ") "

            c.execute(
                "SELECT identity_group.*, " 

                "IFNULL(GROUP_CONCAT( "
                    "DISTINCT CONCAT(role.role,'::',workflow.id,'::',workflow.name) " 
                    "ORDER BY role.id "
                    "SEPARATOR ',' "
                "), '') AS roles_workflow, "
                      
                "IFNULL(GROUP_CONCAT( "
                    "DISTINCT CONCAT(privilege.privilege,'::',workflow.id,'::',workflow.name) " 
                    "ORDER BY privilege.id "
                    "SEPARATOR ',' "
                "), '') AS privileges_workflow "  

                "FROM identity_group "
                "LEFT JOIN group_role_workflow ON group_role_workflow.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_workflow.id_role "
                "LEFT JOIN `workflow` ON `workflow`.id = group_role_workflow.id_workflow "
                "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                + groupWhere +
                "GROUP BY identity_group.id",
                      filterGroups
            )

            items: List[Dict] = DBHelper.asDict(c)
            for ln in items:
                if "roles_workflow" in items[j]:
                    if "," in ln["roles_workflow"]:
                        items[j]["roles_workflow"] = ln["roles_workflow"].split(",")
                    else:
                        items[j]["roles_workflow"] = [ln["roles_workflow"]]

                    rolesStructure = dict()
                    for rls in items[j]["roles_workflow"]:
                        if "::" in rls:
                            rlsList = rls.split("::")
                            if not str(rlsList[0]) in rolesStructure:
                                # Initialize list if not already done.
                                rolesStructure[rlsList[0]] = list()

                            rolesStructure[rlsList[0]].append({
                                "workflow_id": rlsList[1],
                                "workflow_name": rlsList[1],
                            })

                    items[j]["roles_workflow"] = rolesStructure

                if showPrivileges:
                    # Add detailed privileges' descriptions to the output.
                    if "privileges_workflow" in items[j]:
                        if "," in ln["privileges_workflow"]:
                            items[j]["privileges_workflow"] = ln["privileges_workflow"].split(",")
                        else:
                            items[j]["privileges_workflow"] = [ ln["privileges_workflow"] ]

                        ppStructure = dict()
                        for pls in items[j]["privileges_workflow"]:
                            if "::" in pls:
                                pList = pls.split("::")
                                if not str(pList[0]) in ppStructure:
                                    ppStructure[pList[0]] = list()

                                ppStructure[pList[0]].append({
                                    "workflow_id": pList[1],
                                    "workflow_name": pList[2],
                                })

                        items[j]["privileges_workflow"] = ppStructure
                else:
                    del items[j]["privileges_workflow"]

                j = j + 1

            return items
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def countUserPermissions(groups: list, action: str, workflowName: str = "") -> tuple:
        if action and groups:
            args = groups.copy()
            workflowWhere = ""

            c = connection.cursor()

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for _ in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                if workflowName:
                    args.append(workflowName)
                    workflowWhere = "AND workflow.name = %s "

                args.append(action)

                c.execute(
                    "SELECT COUNT(*) AS c, group_role_workflow.details "
                    "FROM identity_group "
                    "LEFT JOIN group_role_workflow ON group_role_workflow.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_workflow.id_role "
                    "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                    "LEFT JOIN workflow ON workflow.id = group_role_workflow.id_workflow "                      
                    "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                    "WHERE ("+groupWhere[:-4]+") " +
                    workflowWhere +
                    "AND privilege.privilege = %s ",
                        args
                )

                o = DBHelper.asDict(c)[0]

                try:
                    details = json.loads(o["details"])
                except Exception:
                    details = {}

                return o["c"], details
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
