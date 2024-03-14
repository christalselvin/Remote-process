import datetime
import json
import sys

from sqlalchemy.orm import sessionmaker

# sys.path.append("/root")
from services import db


class UserModel(db.Model):
    __tablename__ = 'ai_ra_users'

    userid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    emailid = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), primary_key=True)
    phonenumber = db.Column(db.String(), nullable=False)
    fk_roleid = db.Column(db.Integer, db.ForeignKey('ai_ra_roles.roleid'))
    fk_usertype = db.Column(db.Integer, db.ForeignKey('ai_ra_usertype.typeid'))
    fk_timezone_id = db.Column(db.Integer, db.ForeignKey('ai_ra_zone.zone_id'))
    password = db.Column(db.String(), nullable=False)
    attempts = db.Column(db.Integer)
    first_time_login = db.Column(db.String(), nullable=False)

    # _init_create a new data
    # self using binding data
    def init(self, firstname, lastname, emailid, username, phonenumber, fk_roleid, fk_usertype, password,
                 fk_timezone_id, attempts, first_time_login):
        self.firstname = firstname
        self.lastname = lastname
        self.emailid = emailid
        self.username = username
        self.phonenumber = phonenumber
        self.fk_roleid = fk_roleid
        self.fk_usertype = fk_usertype
        self.password = password
        self.fk_timezone_id = fk_timezone_id
        self.first_time_login = first_time_login
        self.attempts = attempts

    def repr(self):
        return f"<User {self.userid}>"


class ConfigModel(db.Model):
    __tablename__ = 'ai_ra_configuration'

    configid = db.Column(db.Integer, primary_key=True)
    configname = db.Column(db.String(), nullable=False)
    dbname = db.Column(db.String(), nullable=True)
    username = db.Column(db.String(), nullable=True)
    password = db.Column(db.String(), nullable=True)
    configtype = db.Column(db.String(), nullable=False)
    configip = db.Column(db.String(), nullable=False)
    configport = db.Column(db.Integer, nullable=False)
    communicationtype = db.Column(db.String(), nullable=False)

    def init(self, configname, configip, configport, dbname, username, password, communicationtype, configtype):

        self.configname = configname
        self.configip = configip
        self.configport = configport
        self.dbname = dbname
        self.username = username
        self.password = password
        self.communicationtype = communicationtype
        self.configtype = configtype

    def repr(self):
        return f"<Configuration {self.config_id}"


class RoleModel(db.Model):
    __tablename__ = 'ai_ra_roles'

    roleid = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(), nullable=False)

    def init(self, rolename):
        self.rolename = rolename

    def repr(self):
        return f"{self.role_id}"



class UserType(db.Model):
    __tablename__ = 'ai_ra_usertype'

    typeid = db.Column(db.Integer, primary_key=True)
    typename = db.Column(db.String(), nullable=False)

    def init(self, typename, active_yn):
        self.typename = typename

    def repr(self):
        return f"{self.typeid}"


class CredModel(db.Model):
    __tablename__ = 'ai_ra_credentials'

    credid = db.Column(db.Integer, primary_key=True)
    credname = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    privatekey = db.Column(db.String(), nullable=False)
    passphrase = db.Column(db.String(), nullable=False)
    protocol = db.Column(db.String(), nullable=False)

    def init(self, cred_name, username, password, privatekey, passphrase, protocol):
        self.cred_name = cred_name
        self.username = username
        self.password = password
        self.privatekey = privatekey
        self.passphrase = passphrase
        self.protocol = protocol

    def repr(self):
        return f"<Credid {self.credid}>"


class ConnModel(db.Model):
    __tablename__ = 'ai_ra_connection'

    connectionid = db.Column(db.Integer, primary_key=True)
    conn_name = db.Column(db.String(), nullable=False)
    protocol = db.Column(db.String(), nullable=False)
    fk_credid = db.Column(db.Integer, db.ForeignKey('ai_ra_credentials.credid'))
    Port = db.Column(db.Integer, nullable=False)

    def init(self, conn_name, protocol, fk_credid, Port):
        self.conn_name = conn_name
        self.protocol = protocol
        self.fk_credid = fk_credid
        self.Port = Port

    def repr(self):
        return f"<Credid {self.connection_id}>"


class MappingUserConnection(db.Model):
    __tablename__ = 'ai_ra_user_connection_mapping'

    mappingid = db.Column(db.Integer, primary_key=True)
    fk_userid = db.Column(db.Integer, db.ForeignKey('ai_ra_users.userid'))
    fk_connectionid = db.Column(db.Integer, db.ForeignKey('ai_ra_connection.connectionid'))

    def init(self, fk_userid, fk_connectionid):
        self.fk_userid = fk_userid
        self.fk_connectionid = fk_connectionid

    def repr(self):
        return f"< {self.mappingid}>"


class ZoneModel(db.Model):
    __tablename__ = 'ai_ra_zone'

    zone_id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(5), nullable=False)
    country_name = db.Column(db.String(50), nullable=False)
    time_zone = db.Column(db.String(100), nullable=False)
    gmt_offset = db.Column(db.String(20), nullable=False)
    active_yn = db.Column(db.String(1), nullable=False)
    is_daylightsaved = db.Column(db.String)

    def init(self, country_code, country_name, time_zone, gmt_offset, active_yn, is_daylightsaved):
        self.country_code = country_code
        self.country_name = country_name
        self.time_zone = time_zone
        self.gmt_offset = gmt_offset
        self.active_yn = active_yn
        self.is_daylightsaved = is_daylightsaved

    def repr(self):
        return f"<Zone {self.pk_zone_id}"


class SessionKeyModel(db.Model):
    __tablename__ = 'tbl_session_keys'

    pk_session_key_id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(), nullable=False)
    active_yn = db.Column(db.String(1), nullable=False)
    fk_user_id = db.Column(db.Integer)

    def init(self, session_key, active_yn, fk_user_id):
        self.session_key = session_key
        self.fk_user_id = fk_user_id
        self.active_yn = active_yn

    def repr(self):
        return f"<key {self.pk_session_key_id}"


class TabModel(db.Model):
    __tablename__ = 'tab_model'

    pk_tab_id = db.Column(db.Integer, primary_key=True)
    tab_name = db.Column(db.String(), nullable=False)
    active_yn = db.Column(db.String(), nullable=False)

    def init(self, tab_name, active_yn):
        self.tab_name = tab_name
        self.active_yn = active_yn

    def repr(self):
        return f"{self.pk_tab_id}"



class PermissionModel(db.Model):
    __tablename__ = 'permission_model'

    pk_permission_id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(), nullable=False)
    active_yn = db.Column(db.String(), nullable=False)

    def init(self, permission_name, active_yn):
        self.permission_name = permission_name
        self.active_yn = active_yn

    def repr(self):
        return f"{self.pk_permission_id}"



class RoleMappingModel(db.Model):
    __tablename__ = 'RoleMapping'

    pk_map_id = db.Column(db.Integer, primary_key=True)
    fk_roleid = db.Column(db.Integer, nullable=False)
    fk_tabid = db.Column(db.Integer, nullable=False)
    fk_permissionid = db.Column(db.Integer, nullable=False)
    active_yn = db.Column(db.String(), nullable=False)

    def init(self, fk_roleid, fk_tabid, fk_permissionid, active_yn):
        self.fk_roleid = fk_roleid
        self.fk_tabid = fk_tabid
        self.fk_permissionid = fk_permissionid
        self.active_yn = active_yn

    def repr(self):
        return f"{self.pk_map_id}"