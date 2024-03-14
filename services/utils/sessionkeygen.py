#import secrets
#from services.utils.ConnPostgreSQL import returnSelectQueryResult, returnInsertResult
import binascii
import os
from services import db
from services.models.models import SessionKeyModel, UserModel, ZoneModel


def createSession(sUserID):
    try:
        #k = secrets.token_hex(64)
        k = binascii.hexlify(os.urandom(64))
        k = k.decode('utf-8')
        new_session=SessionKeyModel(
            session_key=k,
            active_yn='Y',
            fk_user_id=sUserID

        )
        db.session.add(new_session)
        db.session.commit()

        return {"result": "success", "data": k}

    except:
        return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}



def getUserDetailsBasedWithSessionKey(sKey):

    try:
        userid = SessionKeyModel.query.filter(SessionKeyModel.session_key==sKey).filter(SessionKeyModel.active_yn=='Y').first()

        user = UserModel.query.filter(UserModel.pk_user_details_id==userid.fk_user_id).first()

        TimeZone=ZoneModel.query.filter(ZoneModel.pk_zone_id==user.fk_time_zone_id).first()
        results=[{
           " user_id":user.user_id,
            "time_zone":TimeZone.time_zone
        }]

        return {"results":results}


    except:
        return {"results": "failure", "data": "unable to fetch user's timezone based on sessionkey"}

def chkSessionAvailability(key):
    sQuery = "select * from tbl_session_keys where session_key='" + key.strip() + "' and active_yn='Y'"
    dRet = returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        return {"result": "success", "data": "Yes"}
    else:
        return {"result": "failure", "data": "Session expired. Re-Login once again"}

def destroySession(key):
    sQuery = "update tbl_session_keys set active_yn='N' where session_key='" + key + "'"
    dRet = returnInsertResult(sQuery)
    if dRet["result"] == "success":
        if dRet["data"] > 0:
            return {"result": "success", "data": "logged out"}
        else:
            return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}
    else:
        return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}



