from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient import client
from . import log


class Nova():

    def __init__(self,auth_url,username,password,tenant_name,cacert):
        auth = v2.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           tenant_name=tenant_name)
        sess = session.Session(auth=auth,verify=cacert)
        self.nova = client.Client("2",session=sess)
