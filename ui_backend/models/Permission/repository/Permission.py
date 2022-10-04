from django.db import connection

from ui_backend.helpers.Log import Log
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Database import Database as DBHelper


class Permission:

    # IdentityGroupRoleWorkflow

    # Table: group_role_workflow

    #   `id` int(255) NOT NULL AUTO_INCREMENT,
    #   `id_group` int(11) NOT NULL KEY,
    #   `id_role` int(11) NOT NULL KEY,
    #   `id_workflow` int(11) NOT NULL KEY
    #
    #   PRIMARY KEY (`id_group`,`id_role`,`id_workflow`)
    #
    #   CONSTRAINT `grp_group` FOREIGN KEY (`id_group`) REFERENCES `identity_group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    #   CONSTRAINT `grp_workflow` FOREIGN KEY (`id_workflow`) REFERENCES `workflow` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    #   CONSTRAINT `grp_role` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def modify(permissionId: int, identityGroupId: int, roleId: int, workflowId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("UPDATE group_role_workflow SET id_group=%s, id_role=%s, id_workflow=%s WHERE id=%s", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                workflowId,
                permissionId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(permissionId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_role_workflow WHERE id = %s", [
                permissionId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def countUserPermissions(groups: list, action: str, workflowName: str = "") -> int:
        if action and groups:
            args = groups.copy()
            workflowWhere = ""

            c = connection.cursor()

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for g in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                if workflowName:
                    args.append(workflowName)
                    workflowWhere = "AND workflow.name = %s "

                args.append(action)

                c.execute(
                    "SELECT COUNT(*) AS count "
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

                return DBHelper.asDict(c)[0]["count"]
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return False



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT "
                    "group_role_workflow.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    "role.role AS role, "
                    "workflow.name AS workflow_name, "
                    "workflow.id AS workflow_id "
                "FROM identity_group "
                "LEFT JOIN group_role_workflow ON group_role_workflow.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_workflow.id_role "
                "LEFT JOIN workflow ON workflow.id = group_role_workflow.id_workflow "
                "WHERE role.role IS NOT NULL")

            l = DBHelper.asDict(c)
            for el in l:
                el["workflow"] = {
                    "id": el["workflow_id"],
                    "name": el["workflow_name"]
                }

                del(el["workflow_id"])
                del(el["workflow_name"])

            return l
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, roleId: int, workflowId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO group_role_workflow (id_group, id_role, id_workflow) VALUES (%s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                workflowId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
