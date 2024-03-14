import requests
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from services.models.models import ConfigModel

from services.utils import ED_AES256 as aes


urllib3.disable_warnings(InsecureRequestWarning)
projects = {
  "ACTIVEPLUSREADER": "198",
  "ACTIVEREADER": "198",
  "ALERTCLUSTERSERVER": "118",
  "ALERTCLUSTERSERVER32": "118",
  "ALERTSERVER": "118",
  "ALERTSERVER32": "118",
  "ALGOSERVERTI": "204",
  "AQUITASREADER": "198",
  "AS4-TO-IRESS": "162",
  "ASICTI": "141",
  "ASX24READER": "198",
  "ASX24TI": "141",
  "ASXREADER": "198",
  "ASXTI": "141",
  "NZXTI": "141",
  "BESTEXECUTIONBUILDER": "198",
  "BESTEXECUTIONBUILDER32": "198",
  "BLOOMBERGREADER": "198",
  "BOARDROOMRADIOREADER": "198",
  "BOON": "203",
  "BOONPLUS": "203",
  "BOONWEB": "203",
  "CHIAUSREADER": "198",
  "CHICAREADER": "198",
  "CHINEWREADER": "198",
  "CLUSTERSERVER": "203",
  "CRYSTALREPORTSSERVER": "118",
  "CRYSTALREPORTSSERVICES": "118",
  "CSEREADER": "198",
  "CURRENEXREADER": "198",
  "CURRENEXTI": "141",
  "CXATI": "141",
  "DATAFEEDIMPORTER": "140",
  "DATAFEEDPROCESSOR": "140",
  "DATAFEEDSERVER": "198",
  "DELAYEDDATABUILDER": "198",
  "DEPTHSRV": "118",
  "DEPTHSRV32": "118",
  "DEPTHSRV64": "118",
  "DFSAGENT": "417",
  "DFSAGENTREP": "417",
  "DFSAGENTREP64": "417",
  "DFSMONITOR": "417",
  "DJREADER": "198",
  "DOWNLOADUTILITY": "198",
  "ECONOMICSREADER": "198",
  "EDIREFERENCEDATAREADER": "198",
  "ETS": "112",
  "ETSSERVER": "112",
  "FILEREADER": "198",
  "FIXCONNECT": "166",
  "FIXCONNECTI": "141",
  "FIXPLUSSRE": "142",
  "FIXPLUSTE": "142",
  "FIXPLUSTI": "166",
  "FIXREADER": "198",
  "FIXSERVER": "142",
  "FIXSRV": "142",
  "FIXTI": "166",
  "FPMREADER": "198",
  "FUNDREADER": "198",
  "FXCMREADER": "198",
  "GBSTINTERFACE": "203",
  "GBSTINTERFACED": "203",
  "GBSTWEBSERVICEINTERFACE": "203",
  "IDS": "118",
  "IDWSPages": "118",
  "IMS [-Production]": "417",
  "INDCRYPTOREADER": "198",
  "INDEXBUILDER": "198",
  "INSTINETREADER": "198",
  "INTERACTIVEREADER": "198",
  "INVASTREADER": "198",
  "IOS": "239",
  "IOSPLUSADAPTER": "203",
  "IOSPLUSINTERFACE": "239",
  "IOSPLUSSRE": "203",
  "IOSPLUSTE": "203",
  "IOSPLUSTI": "203",
  "IOSTEST": "417",
  "IOSWEB": "239",
  "IPSSERVER": "112",
  "IQFIX": "142",
  "IRESSWATCHDOG": "417",
  "IRESSFEEDREADER": "198",
  "IRESSSERVICEMONITOR": "166",
  "IRESSSERVICEMONITOR4": "166",
  "LEWISREADER": "198",
  "LIMITINTERFACE": "203",
  "LSEREADER": "198",
  "MARKERDATABUILDER": "198",
  "MARKETDATABUILDER": "198",
  "MARKETREPLAYEXSRV": "118",
  "MARKETREPLAYSERVER": "118",
  "MESSAGESERVER": "118",
  "MESSAGESERVER32": "118",
  "MITTI": "141",
  "MONTREALREADER": "198",
  "MVISREADER": "198",
  "NSXREADER": "198",
  "NSXTI": "141",
  "NZREADER": "198",
  "NZXREADER": "198",
  "OCHREADER": "198",
  "OMEGAREADER": "198",
  "ONEZEROREADER": "198",
  "OPINIONREADER": "198",
  "ORH": "150",
  "ORH64": "150",
  "PAGEREADER": "118",
  "PASTER": "239",
  "PDSREADER": "198",
  "PHOENIX": "118",
  "PHOENIX32": "118",
  "PLUSCOMPARE": "417",
  "PLUSSERVERMANAGER": "203",
  "PNXSRV": "118",
  "PNXSRV32": "118",
  "PNXSRV64": "118",
  "QHREADER": "198",
  "QHREFMANAGER": "198",
  "QUOTEEXTRABUILDER": "198",
  "QUOTEEXTRASERVER": "118",
  "QUOTEEXTRASERVER32": "118",
  "QUOTEEXTRASERVER64": "118",
  "QUOTESRV": "118",
  "QUOTESRV32": "118",
  "QUOTESRV64": "118",
  "REPLICATIONSERVER": "118",
  "REPLICATIONSERVER32": "118",
  "SECIDMANAGER": "118",
  "SECIDSRV": "118",
  "SECIDSRV32": "118",
  "SECSRV": "118",
  "SFEREADER": "198",
  "SGXREADER": "198",
  "SGXTI": "141",
  "SGXNEWSREADER": "198",
  "SOKDRV": "118",
  "SOKDRV32": "118",
  "SOLACTIVEREADER": "198",
  "STAMPREADER": "198",
  "STRATEGYTI": "204",
  "SQL": "417",
  "SYNTHETICBUILDER": "118",
  "TMGDATAMANAGER": "198",
  "TRADEREPOSITORYSERVER": "118",
  "TRADESRV": "118",
  "TRADESRV32": "118",
  "TRADESRV64": "118",
  "TRIACTREADER": "198",
  "TSBUILDER": "198",
  "UPLOADSERVER": "203",
  "WEALTHTI": "141",
  "WEBDRV": "222"
}

def getConfig():
    Conn = ConfigModel.query.filter(ConfigModel.configname=='JIRA').first()

    if Conn is not None:
        configip = Conn.configip
        configport = Conn.configport
        arconuser = Conn.username
        # arconpwd  = decoder.decode('auto!ntell!', dRet['data'][0]['password'])
        arconpwd = aes.decrypt((Conn.password).encode(), '@ut0!ntell!'.encode()).decode('utf-8')
        commtype = Conn.communicationtype
        proxy = Conn.proxy

        return (configip, configport, arconuser, arconpwd, commtype, proxy)


def createJIRATicket(desc, appname, notes):
    try:
        configip, configport, arconuser, arconpwd, commtype, proxy = getConfig()
        url = "{0}://{1}:{2}/rest/api/2/issue".format(commtype, configip, configport)
        print(url)
        headers = {'Content-Type': 'application/json'}
        cust_field = projects[appname] if appname in projects else "417"
        payload = {
            "fields": {
                "summary": desc,
                "project": {
                    "id": "22804"
                },
                "issuetype": {
                    "id": "10600"
                },
                "customfield_10800": cust_field,
                "description": notes
            }
        }

        del proxy['ftp']


        res = requests.post(url=url, auth=(arconuser, arconpwd), data=json.dumps(payload), headers=headers, verify=False,
                            proxies=proxy)
        if res.status_code == 200 or res.status_code == 201:
          outJS = json.loads(res.text)
          if "key" in outJS:
            return {'result': 'success', 'data': {"jira_id": outJS['key']}}
          else:
            return {'result': 'failure', 'data': 'unable to create jira. try after sometime.'}
        else:
          return {'result': 'failure', 'data': 'unable to create jira. try after sometime.'}
    except Exception as e:

              return {"result": "failure", "data": str(e)}