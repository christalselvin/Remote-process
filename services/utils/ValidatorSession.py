import json
from flask import request

from services.models.models import SessionKeyModel
from services.utils.ConnLog import create_log_file

import services.utils.LFColors as lfc
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
   CERROR("Not able to create logfile")
   exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def lam_api_key_missing():
    return {"result": "failure", "data": "api-key missing"}

def lam_api_key_invalid():
    return {"result": "failure", "data": "invalid api-key"}

def chkValidRequest(key):

    key = SessionKeyModel.query.filter(SessionKeyModel.session_key == request.headers["SESSIONKEY"]).filter(SessionKeyModel.active_yn=='Y').first()
    if key is not None:
        logINFO("New Session {0}".format(key))
        return True
    else:
        logWARN("Invalid session access {0}".format(key))
        return False


def chkKeyExistsInHeader(key):
    try:
        tmp = request.headers[key]
        return True
    except KeyError as e:
        logWARN("Foreign Entry")
        return False
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return False

