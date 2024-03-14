
#import services.utils.ConnPostgreSQL as con
from services.models.models import ConfigModel
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ED_AES256 as aes
import ldap3

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def authenticate(username, password):
    sIP, sPort, sCommType = "", "", ""
    try:
        # Fetch LDAP or LDAPS details from database
        LDAP = ConfigModel.query.filter(ConfigModel.configname=='LDAP').first()

        if LDAP is not None:
            sIP = LDAP.configip
            sPort = LDAP.configport
            sCommType = LDAP.communicationtype
            sUsername = LDAP.username
            sPassword = LDAP.password
            sBaseDN = ""
        else:
            return {"result": "failure", "data": "LDAP Config Fetch Failed"}
    except Exception as e:
        return {"result": "failure", "data": "LDAP Config Fetch: Err: {0}".format(str(e))}


    try:
        # Service Account Details
        SERVER = sIP
        BASEDN = None
        USER = sUsername
        k = '@ut0!ntell!'.encode()
        fromDB = (sPassword).encode()
        #PWD = aes.decrypt(fromDB, k).decode('utf-8')
        PWD=""

        #PWD = aes.decrypt(sPassword.encode(), '@ut0!ntell!'.encode()).decode('utf-8')   # Password for Service Account

        SEARCHFILTER = '(&(|(userPrincipalName=' + username + ')(samaccountname=' + username + ')(mail=' + username + '))(objectClass=person))'
        USER_DN = ""
        ldap_server = ldap3.Server(SERVER, get_info=ldap3.ALL)
        conn = ldap3.Connection(ldap_server, USER, PWD, auto_bind=True)
        conn.search(search_base=BASEDN,
                search_filter=SEARCHFILTER,
                search_scope=ldap3.SUBTREE,
                attributes=['cn', 'givenName'],
                paged_size=5)
        for entry in conn.response:
            if entry.get("dn") and entry.get("attributes"):
                if entry.get("attributes").get("cn"):
                    USER_DN = entry.get("dn")

        if USER_DN == "":
            return {"result": "failure", "data": "User doesn't exists"}

        auth_conn = ldap3.Connection(ldap_server, USER_DN, password)

        if not auth_conn.bind():
            logERROR("Authentication Failed, reason: {0}".format(auth_conn.result))
            return {"result": "failure", "data": "Authentication Failed"}
        else:
            return {"result": "success", "data": "Successfully authenticated"}
    except Exception as e:
        return {"result": "failure", "data": "LDAP Config Fetch: Err: {0}".format(str(e))}
