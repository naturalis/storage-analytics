from keystoneclient.auth.identity import v3
from keystoneclient import session
from cinderclient import client
from utils import log



class Cinder():

    def __init__(self,auth_url,username,password,project_name,cacert,project_id):
        # auth = v2.Password(auth_url=auth_url,
        #                    username=username,
        #                    password=password,
        #                    tenant_id=project_id)
        auth = v3.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           project_id=project_id,
                           user_domain_name='Default',
                           project_domain_id='Default')
        sess = session.Session(auth=auth,verify=cacert)
        self.cinder = client.Client("2",session=sess)


    def update_quota(self,project_id,items):
        updates = self.__quota_compare(project_id,items)
        if updates != {}:
            updates.update({"tenant_id": project_id})
            try:
                self.cinder.quotas.update(**updates)
                log.logger.info("trying to update project_id: %s with quota: %s" % (project_id,updates))
            except Exception as e:
                log.logger.warning(e)

    def __get_quota(self,project_id):
        return self.cinder.quotas.get(project_id)

    def __quota_compare(self,project_id,items):
        current = self.__get_quota(project_id)
        new = {}
        for key,value in items.iteritems():
            try:
                if value != getattr(current,key):
                    new.update({key: value})
            except Exception as e:
                log.logger.warning("Could not parse quota of project %s with quota setting %s" % (project_id,key))
        return new

    def get_volume_info(self):
        """
        Get info about volumes in a project
        * Needs project_id
        Return array with objects with id, attached, attached_to, size, type
        """
        # possible keys
        # ['attachments', 'links', 'availability_zone', 'os-vol-host-attr:host', 'encrypted', 'os-volume-replication:extended_status', 'manager', 'replication_status', 'snapshot_id', 'id', 'size', 'user_id', 'os-vol-tenant-attr:tenant_id', 'os-vol-mig-status-attr:migstat', 'metadata', 'status', 'description', 'multiattach', 'source_volid', 'consistencygroup_id', 'os-vol-mig-status-attr:name_id', 'name', 'bootable', 'created_at', 'os-volume-replication:driver_data', '_info', 'volume_type', '_loaded']
        payload = []
        for v in self.cinder.volumes.list():
            if v.status == 'in-use':
                attached_to_id = v.attachments[0]['server_id']
            else:
                attached_to_id = ''

            payload.append({'id': v.id,
                            'name': v.name,
                            'size': v.size*1024*1024*1024,
                            'attached_to_id': attached_to_id,
                            'status': v.status })

        return payload
        #{'attachments': [{u'server_id': u'02d64dd8-de03-4279-aed5-e55c4d98b94b', u'attachment_id': u'2bc92745-91ee-428b-b5f9-f3f19f174adf', u'host_name': None, u'volume_id': u'd011b97d-fe50-456e-855d-9fb7f1babed4', u'device': u'/dev/vdb', u'id': u'd011b97d-fe50-456e-855d-9fb7f1babed4'}], 'status': u'in-use', 'size': 1073741824000, 'id': u'd011b97d-fe50-456e-855d-9fb7f1babed4', 'name': u'LeonData'}
    # def flavor_access(self,flavor):
    #     return self.__get_flavor_access_list(flavor)
    #
    # def grant_to_flavor(self,flavorname,projectid):
    #     try:
    #         flid = self.__get_flavor_id(flavorname)
    #         self.nova.flavor_access.add_tenant_access(flid,projectid)
    #         return True
    #     except Exception as e:
    #         log.logger.debug(e)
    #         return False
    #
    #
    # def update_quota(self,project_id,items):
    #     kwargs = self.__quota_compare(project_id,items)
    #     if kwargs != {}:
    #         kwargs.update({"tenant_id": project_id})
    #         try:
    #             self.nova.quotas.update(**kwargs)
    #             log.logger.debug("trying to update project_id: %s with quota: %s" % (project_id,kwargs))
    #             return True
    #         except Exception as e:
    #             log.logger.debug(e)
    #             return False
    #     else:
    #         return None
    #
    #
    # def __quota_compare(self,project_id,items):
    #     current = self.__list_quota(project_id)
    #     new = {}
    #     for key,value in items.iteritems():
    #         try:
    #             if value != getattr(current,key):
    #                 new.update({key: value})
    #         except Exception as e:
    #             log.logger.warning("Could not parse quota of project %s with quota setting %s" % (project_id,key))
    #     return new
    #
    # def __list_quota(self,project_id):
    #     return self.nova.quotas.get(project_id)
    #
    # def revoke_to_flavor(self,flavorname,projectid):
    #     try:
    #         flid = self.__get_flavor_id(flavorname)
    #         self.nova.flavor_access.remove_tenant_access(flid,projectid)
    #         return True
    #     except Exception as e:
    #         log.logger.debug(e)
    #         return False
    #
    # def __get_flavor_access_list(self,flavor):
    #     flid = self.__get_flavor_id(flavor)
    #     if not flid:
    #         raise NameError("Flavor %s does not exist" % flavor)
    #     else:
    #         return self.nova.flavor_access._list_by_flavor(flid)
    #
    # def __get_flavor_id(self,flavor):
    #     all_flavors = self.nova.flavors.list()
    #     exists = False
    #     for f in all_flavors:
    #         if f.name == flavor:
    #             exists = f.id
    #             break
    #     return exists
    #
    #






#sess = session.Session(auth=auth,verify='cert/stack_naturalis_nl.ca-bundle')
