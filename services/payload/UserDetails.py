from flask import current_app as app
from flask import request
from services.models.models import UserModel, RoleModel, UserType, ZoneModel, SessionKeyModel
from services import db
import services.utils.ED_AES256 as aes
import services.utils.LDAPAuth as ldapauth
from services.utils import sessionkeygen
import json
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, \
    lam_api_key_missing
import services.utils.mailservice as ms
from services.utils.decoder import decode, encode


# UserManagement
@app.route('/api/users/createUser', methods=['POST'])
def createUser(*args):
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            # Check User Already Exist
            User = UserModel.query.filter(UserModel.username == data['username']).first()
            email = UserModel.query.filter(UserModel.emailid == data['emailid']).first()
            if email is not None:
                return {"message": f"emailid Already Exist", "type": "failure"}
            if User is None:
                role = RoleModel.query.filter(RoleModel.roleid == data['role']).first()
                user_type = UserType.query.filter(UserType.typename == data['usertype']).first()

                k = '@ut0!ntell!'.encode()
                defaultPwd = "NxtGen@123".encode()
                new_user = UserModel(
                    firstname=data['firstname'],
                    lastname=data['lastname'],
                    emailid=data['emailid'],
                    username=data['username'],
                    phonenumber=data['phonenumber'],
                    fk_roleid=role.roleid,
                    fk_usertype=user_type.typeid,
                    fk_timezone_id=data['time_zone'],
                    password=aes.encrypt(defaultPwd, k).decode('utf-8'),
                    attempts=0,
                    first_time_login="N" if data["usertype"].strip().lower() == "ldap" else "Y")

                msub = "New User Registration"
                mto = data['emailid']
                mcc = data['emailid']

                mbody = ("Thanks for registering  <BR/>User ID: {0}<BR/>Use this password, <B>NxtGen@123</B> to do "
                         "first time login").format(
                    data['username'])
                mlbody = "Thanks for registering <BR/>User ID: {0}<BR/>Password: AD Password".format(data['username'])

                """passw = "mailpswd"

                print({"pass":encode('auto!ntell!',passw)})"""

                if new_user.first_time_login == 'N':
                    pass

                    # ms.sendmail(msub, mto, mcc, mlbody)

                else:
                    pass

                    # ms.sendmail(msub, mto, mcc, mbody)

                db.session.add(new_user)
                db.session.commit()

                return {"message": f"User {new_user.firstname} registered successfully", "type": "success"}, 201
            else:
                return {"message": f"User Already Exist", "type": "failure"}
        else:
            return {"message": f"Request payload is not in json format", "type": "failure"}
    else:
        return {"message": f"Method Not Allowed", "type": "failure"}


@app.route('/api/users/getSingleUser', methods=['GET'])
def getSingleUser(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):

            try:
                data = request.args
                User = UserModel.query.filter(UserModel.userid == data['userid']).first()

                if User is not None:

                    Role = RoleModel.query.filter(RoleModel.roleid == User.fk_roleid).first()
                    Zone = ZoneModel.query.filter(ZoneModel.zone_id == User.fk_timezone_id).first()
                    Usertype = UserType.query.filter(UserType.typeid == User.fk_usertype).first()

                    if Role and Zone and Usertype is not None:
                        results = {
                            "userid": data['userid'],
                            "first_name": User.firstname,

                            "lastname": User.lastname,
                            "emailid": User.emailid,
                            "phonenumber": User.phonenumber,
                            "rolename": Role.rolename,
                            "zoneid": Zone.zone_id,
                            "country_code": Zone.country_code,
                            "time_zone": Zone.time_zone,
                            "user_type_desc": Usertype.typename

                        }

                        return {"type": "success", "data": results}
                    else:
                        return {"type": "failure", "message": "User details are missing from database"}
                else:
                    return {"type": "failure", "message": "User id not found"}


            except Exception as e:

                print(str(e))
                return json.dumps({'result': 'failure', "message": "Unable to fetch data from database."})

        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/users/login', methods=['POST'])
def checkLogin():
    data = request.get_json()
    try:
        sLExp = ""
        # License Expiry
        # bLicense = licensing.checkExpiry()
        bLicense = True
        if bLicense == False:
            sLExp = "License Expired"

            # return json.dumps({'result': 'failure', 'data': 'License Expired'})
        username = data['username']
        password = data['password']
        User = UserModel.query.filter(UserModel.username == username).first()
        if User is not None:

            Usertype = UserType.query.filter(UserType.typeid == User.fk_usertype).first()
            if Usertype.typename == "LDAP":
                k = '@ut0!ntell!'.encode()
                fromClient = password.encode()
                pass_de = aes.decrypt(fromClient, k).decode('utf-8')
                if username.find('\r'):
                    x = username.replace('\r', '\\r')
                elif username.find('\n'):
                    x = username.replace('\n', '\\n')
                dRetLDAP = ldapauth.authenticate(x.split('@')[0], pass_de)
                if dRetLDAP["result"] == "success":
                    dFinalData = {}
                    role = RoleModel.query.filter(RoleModel.roleid == User.fk_roleid).first()
                    Zone = ZoneModel.query.filter(ZoneModel.zone_id == User.fk_timezone_id).first()
                    user_type = UserType.query.filter(UserType.typeid == User.fk_usertype).first()

                    results = {
                        "firstname": User.firstname,
                        "lastname": User.lastname,
                        "emailid": User.emailid,
                        "username": User.username,
                        "phonenumber": User.phonenumber,
                        "role": role.rolename,
                        "usertype": user_type.typename,
                        "time_zone": Zone.time_zone,
                    }
                    dFinalData.update(results)  # UserInfo
                    # Attach Session Key
                    dRetKey = sessionkeygen.createSession(User.userid)
                    dFinalData['session_id'] = dRetKey['data']
                    """if dRetKey["result"] == "success":
                        pRoleName = results['role_name']
                        dRetMap = getRoleMappers(pRoleName)
                        dFinalData['mapper'] = dRetMap['data']
                        dFinalData["result"] = "success"
                        dFinalData['license'] = sLExp"""

                    return json.dumps(dFinalData)
                # else:
                # return {"type":"failure", "message":"Failed accepting request. Try after sometime."}"""

                else:
                    return {"type": "failure", "message": "Failed fetching profile. Try after sometime."}
            else:
                dFinalData = {}
                """if username.lower() != "admin":
                    attempts=User.attempts
                    if attempts >= 3:
                        return json.dumps({'result': 'failure', 'data': 'Account locked! Contact Administrator.'})"""

                k = '@ut0!ntell!'.encode()
                cmp1 = password

                fromDB = (User.password).encode()
                # print(fromDB)
                cmp2 = aes.decrypt(fromDB, k).decode('utf-8')
                print(cmp2)
                if cmp1 == cmp2:
                    role = RoleModel.query.filter(RoleModel.roleid == User.fk_roleid).first()
                    Zone = ZoneModel.query.filter(ZoneModel.zone_id == User.fk_timezone_id).first()
                    user_type = UserType.query.filter(UserType.typeid == User.fk_usertype).first()
                    results = {
                        "user_id": User.userid,
                        "first_name": User.firstname,
                        "last_name": User.lastname,
                        "email_id": User.emailid,
                        "phone_number": User.phonenumber,
                        "role_name": role.rolename,
                        "country_code": Zone.country_code,
                        "time_zone": Zone.time_zone,
                        "gmt_offset": Zone.gmt_offset,
                        "user_type_desc": Usertype.typename,

                    }
                    dFinalData.update(results)  # UserInfo

                    # Attach Session Key
                    dRetKey = sessionkeygen.createSession(User.userid)

                    dFinalData['session_id'] = dRetKey['data']

                    """if dRetKey["result"] == "success":
                        # Send role details along to customize UI

                        pRoleName = results['role_name']
                        dRetMap = getRoleMappers(pRoleName)

                        dFinalData['mapper'] = dRetMap['data']

                        dFinalData["result"] = "success"
                        dFinalData['license'] = sLExp"""

                    return {"data": dFinalData}
                    # else:
                    # return {"type":"failure", "message":"Failed accepting request. Try after sometime."}
                else:
                    User.attempts = User.attempts + 1
                    db.session.add(User)
                    db.session.commit()
                    return {"type": "failure", "message": " 'Wrong Password! entered by {0}".format(username)}
        else:
            return {"type": "failure", "message": "User doesn't exists"}
    except Exception as e:
        return json.dumps({'result': 'failure', "message": "Exception: {0}".format(str(e))})


@app.route('/api/users/deleteUser', methods=['DELETE'])
def deleteUser(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                data = request.args
                User = UserModel.query.filter(UserModel.userid == data['userid']).first()
                if User is not None:
                    session = SessionKeyModel.query.filter(SessionKeyModel.fk_user_id == data['userid']).all()
                    for i in range(len(session)):
                        SessionKeyModel.query.filter(
                            SessionKeyModel.pk_session_key_id == session[i].pk_session_key_id).delete()

                    UserModel.query.filter(UserModel.userid == data['userid']).delete()
                    db.session.commit()

                    return {"type": "success", "message": "User has been removed successfully"}

                else:
                    return {"type": "failure", "message": "User id not found"}

            except Exception as e:
                print(str(e))
                return json.dumps({'result': 'failure', "message": "Unable to delete user from database."})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/users/logout', methods=['PUT'])
def logout():
    # print("Header",request.headers)
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            data = request.args
            User = UserModel.query.filter(UserModel.userid == data['userid']).first()
            if User is not None:

                try:

                    key = request.headers["SESSIONKEY"]
                    sessionupdate = SessionKeyModel.query.filter(SessionKeyModel.session_key == key.strip()).first()
                    sessionupdate.active_yn = "N"
                    db.session.add(sessionupdate)
                    db.session.commit()
                    return json.dumps({"result": "success", "data": "Successfully logged out"})

                except:

                    return json.dumps({'result': 'failure', "message": "Unable to logout."})
            else:
                return ({"result": "failure", "message": "user not found"})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/users/passwordReset', methods=['PUT'])
def firstTimeLoginPwdReset():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                data = request.get_json()
                lAttr = ["username", "new_password"]
                lPayErr = [1 if i in lAttr else 0 for i in data.keys()]
                if not 0 in lPayErr:
                    k = '@ut0!ntell!'.encode()
                    cmp1 = data['new_password']
                    fromDB = UserModel.query.filter(UserModel.username == data['username']).first()

                    fromDB = (fromDB.password).encode()
                    # print(fromDB)
                    cmp2 = aes.decrypt(fromDB, k).decode('utf-8')
                    print(cmp2)
                    if cmp1 == cmp2:
                        return {"result": "failure", "data": "new password should be different from old password"}

                    k = '@ut0!ntell!'.encode()

                    pwd = data["new_password"].encode()
                    password = aes.encrypt(pwd, k).decode('utf-8')
                    User = UserModel.query.filter(UserModel.username == data['username']).first()
                    User.password = password
                    User.first_time_login = 'N'
                    db.session.add(User)
                    db.session.commit()
                    return {"result": "success", "data": "Password has been changed"}
                else:
                    return {"result": "failure", "message": "Required parameter missing"}


            except Exception as e:
                return json.dumps({'result': 'failure', "message": e})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}


@app.route('/api/users/updateUser', methods=['PUT'])
def updateUserById(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                data = request.get_json()
                userid = request.args['userid']
                User = UserModel.query.get(userid)

                if User:
                    # Update user attributes based on the JSON data
                    for key, value in data.items():
                        # Check if the field exists in the UserModel and update it
                        if hasattr(User, key):
                            setattr(User, key, value)

                    db.session.commit()
                    return {"result": "success", "data": "User information has been updated"}
                else:
                    return {"result": "failure", "message": "User with ID not found"}

            except Exception as e:
                return json.dumps({'result': 'failure', "message": "Failed to update user"})
        else:
            return {"result": "failure", "data": "Invalid API key"}
    else:
        return {"result": "failure", "data": "API key missing"}


@app.route('/api/users/getAllUser', methods=['GET'])
def getAllUser(*args):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):

            try:
                User = UserModel.query.all()
                Userdetails = []

                if User != []:
                    for i in range(len(User)):
                        role = RoleModel.query.filter(RoleModel.roleid == User[i].fk_roleid).first()
                        Zone = ZoneModel.query.filter(ZoneModel.zone_id == User[i].fk_timezone_id).first()
                        user_type = UserType.query.filter(UserType.typeid == User[i].fk_usertype).first()

                        if role and Zone and user_type is not None:
                            results = {
                                "userid": User[i].userid,
                                "first_name": User[i].firstname,
                                "last_name": User[i].lastname,
                                "email_id": User[i].emailid,
                                "phone_number": User[i].phonenumber,
                                "role_name": role.rolename,
                                "country_code": Zone.country_code,
                                "time_zone": Zone.time_zone,
                                "gmt_offset": Zone.gmt_offset,
                                "user_type_desc": user_type.typename,

                            }
                            Userdetails.append(results)

                    return {"type": "success", "Userdetails": Userdetails}

            except Exception as e:

                print(str(e))
                return json.dumps({'result': 'failure', "message": "Unable to fetch data from database."})
        else:
            return {"result": "failure", "data": "invalid api-key"}
    else:
        return {"result": "failure", "data": "api-key missing"}
