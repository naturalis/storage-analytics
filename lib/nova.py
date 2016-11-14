from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client
from . import log


class KeyStone:
    def __init__(self,auth_url,ks_username,ks_password,project_name):
        auth = v3.Password(auth_url=auth_url,
                           username=ks_username,
                           password=ks_password,
                           project_name=project_name,
                           user_domain_name='Default',
                           project_domain_id='Default')

        sess = session.Session(auth=auth)
        self.ksclient = client.Client(session=sess)
        self.member_role_id = self.ksclient.roles.list(name='_member_')[0].id

        log.logger.debug("enumbering access for groups in projects")
        self.grouplist = self.ksclient.groups.list()
