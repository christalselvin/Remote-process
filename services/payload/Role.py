# import jwt
# import nmap
from flask import current_app as app
from flask import request, abort, Response, jsonify
# from passlib.handlers.sha2_crypt import sha256_crypt
# from sqlalchemy.orm import scoped_session, sessionmaker

from services import db
3.20
from services.models.models import CredModel, RoleModel, UserModel, TabModel, PermissionModel, SessionKeyModel, \
    RoleMappingModel
import services.utils.ConnMQ as connmq
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info


@app.route('/api/getAllTabs', methods=['GET'])
def getAllTabs(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                TAB = TabModel.query.filter(TabModel.active_yn == 'Y').all()
                results = []
                for tab in TAB:
                    results.append(tab.tab_name)
                return {"type": "success", "tab_name": results}

            except Exception as e:
                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/getAllPermission', methods=['GET'])
def getAllPermission(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                Permission = PermissionModel.query.filter(PermissionModel.active_yn == 'Y').all()
                results = []
                for p in Permission:
                    results.append(p.permission_name)
                return {"type": "success", "permission_name": results}

            except Exception as e:
                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/role/create', methods=['POST'])
def createRole(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):

            try:

                data = request.get_json()

                Role = RoleModel.query.filter(RoleModel.rolename == data['rolename']).first()

                if Role is None:
                    new_role = RoleModel(
                        rolename=data['rolename'],
                    )
                    db.session.add(new_role)
                    db.session.commit()

                    dMapper = data["mapping"]
                    # print("this" +data)
                    for key in dMapper.keys():
                        role = RoleModel.query.filter(RoleModel.rolename == data['rolename']).first()
                        tab = TabModel.query.filter(TabModel.tab_name == key).first()
                        permission = PermissionModel.query.filter(
                        PermissionModel.permission_name == dMapper[key]).first()
                        new_map = RoleMappingModel(

                            fk_roleid=role.roleid,
                            fk_tabid=tab.pk_tab_id,
                            fk_permissionid=permission.pk_permission_id,
                            active_yn='Y'

                        )
                        db.session.add(new_map)
                        db.session.commit()

                    return {"type": "success", "message": "Role added sucessfully"}
                else:
                    return {"type": "failure", "message": "Role {0} already exists".format(data['rolename'])}

            except Exception as e:
                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})

        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/role/getAllRoles', methods=['GET'])
def getAllRoles(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                ROLE = RoleModel.query.all()
                if ROLE is not None:
                    results = []
                    for role in ROLE:
                        results.append(role.rolename)

                    return {"type": "success", "Roles": results}

                else:
                    return {"type": "failure", "message": "Role doesn't exists"}


            except Exception as e:
                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/role/removeRole', methods=['DELETE'])
def removeRole(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                data = request.get_json()
                # Role = RoleModel.query.filter(RoleModel.rolename == data['rolename']).first()

                ROLE = RoleModel.query.filter(RoleModel.rolename == data['rolename']).first()

                if ROLE is None:
                    return {"type": "failure", "message": "Role {0} doesnt exists".format(data['rolename'])}
                else:

                    sChkDependecies = UserModel.query.filter(UserModel.fk_roleid == ROLE.roleid).first()
                    if sChkDependecies:
                        return {"type": "failure",
                                "message": "Deleting role: {0} failed. There are users with this role.".format(
                                    data['rolename'])}

                    else:
                        RoleMappingModel.query.filter(RoleMappingModel.fk_roleid == ROLE.roleid).delete()

                        RoleModel.query.filter(RoleModel.rolename == data['rolename']).delete()
                        db.session.commit()
                        return {"type": "success", "message": "Role deleted successfully!"}
            except Exception as e:
                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/role/updateRole', methods=['PUT'])
def updateRole(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                data = request.get_json()

                role = RoleModel.query.filter(RoleModel.rolename == data['rolename']).first()

                if role is not None:
                    # Update existing role attributes
                    role.rolename = data['rolename']
                    db.session.commit()

                    # Clear existing role mappings
                    RoleMappingModel.query.filter_by(fk_roleid=role.roleid).delete()

                    dMapper = data["mapping"]
                    for key in dMapper.keys():
                        tab = TabModel.query.filter(TabModel.tab_name == key).first()
                        permission = PermissionModel.query.filter(
                            PermissionModel.permission_name == dMapper[key]).first()

                        new_map = RoleMappingModel(
                            fk_roleid=role.roleid,
                            fk_tabid=tab.pk_tab_id,
                            fk_permissionid=permission.pk_permission_id,
                            active_yn='Y'
                        )
                        db.session.add(new_map)

                    db.session.commit()

                    return {"type": "success", "message": "Role updated successfully"}
                else:
                    return {"type": "failure", "message": "Role {0} does not exist".format(data['rolename'])}

            except Exception as e:
                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})

            else:
                return {"result": "failure", "data": "invalid api-key"}
        else:
            return {"result": "failure", "data": "api-key missing"}

@app.route('/api/role/getRolesMappers', methods=['GET'])
def getRolesMappers(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:

                list = PermissionModel.query.filter(PermissionModel.active_yn == 'Y').all()
                if list is not None:
                    results = []
                    for i in range(len(list)):
                        role = RoleModel.query.filter(RoleModel.roleid == list[i].fk_role_id).first()
                        Tab = TabModel.query.filter(TabModel.pk_tab_id == list[i].fk_tab_id).first()
                        Permission = PermissionModel.query.filter(
                            PermissionModel.pk_permission_id == list[i].fk_permission_id).first()
                        results.append({"Role_name": role.role_name, "Tab_name": Tab.tab_name,
                                        "Permission": Permission.permission_name})

                    return {"type": "success", "data": results}
                else:
                    return {"type": "success", "data": "No data found"}

            except Exception as e:

                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/role/getRoleMappers', methods=['GET'])
def getRoleMappers(*args):
    data = request.get_json()
    try:
        results = []
        role = RoleModel.query.filter(RoleModel.rolename == data['rolename']).first()
        if role is not None:
            list = PermissionModel.query.filter(PermissionModel.pk_permission_id == role.roleid).first()
            Tab = TabModel.query.filter(TabModel.pk_tab_id == list.fk_tab_id).first()
            Permission = PermissionModel.query.filter(PermissionModel.pk_permission_id == list.fk_permission_id).first()

            results.append(
                {"Rolename": role.role_name, "tab_name": Tab.tab_name, "Permission": Permission.permission_name})

            return {"type": "success", "data": results}
        else:
            return {"type": "success", "data": "No data found"}

    except Exception as e:

        print(str(e))
        return {"data": "Something Went Wrong", "result": "failure"}


@app.route('/api/role/getOneRoleMappers', methods=['GET'])
def getOneRoleMappers(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:

                data = request.get_json
                Role = RoleModel.query.filter(RoleModel.rolename == data['rolename']).filter(
                    RoleModel.active_yn == 'Y').first()

                if Role is not None:
                    roleid = Role.pk_role_id
                    RoleMap = PermissionModel.query.filter(PermissionModel.fk_role_id == roleid).filter(
                        PermissionModel.active_yn == 'Y').all()
                    if RoleMap is not None:
                        results = []
                        for i in range(len(RoleMap)):
                            role = RoleModel.query.filter(RoleModel.pk_role_id == RoleMap[i].fk_role_id).first()
                            Tab = TabModel.query.filter(TabModel.pk_tab_id == RoleMap[i].fk_tab_id).first()
                            Permission = PermissionModel.query.filter(
                                PermissionModel.pk_permission_id == RoleMap[i].fk_permission_id).first()
                            results.append({"Rolename": role.role_name, "tab_name": Tab.tab_name,
                                            "Permission": Permission.permission_name})

                        return {"type": "success", "message": results}
                    else:
                        return {"type": "success", "message": "No data found"}
                else:

                    return {"type": "success", "message": "Role not found"}


            except Exception as e:

                print(str(e))
                return jsonify({"Message": "Something Went Wrong", "result": "failure"})

        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}
