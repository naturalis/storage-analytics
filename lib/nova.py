from keystoneclient.auth.identity import v3
from keystoneclient import session
from novaclient import client
from . import log


class Nova():

    def __init__(self,auth_url,username,password,project_id,cacert):
        auth = v3.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           project_id=project_id,
                           user_domain_name='Default',
                           project_domain_id='Default')
        sess = session.Session(auth=auth,verify=cacert)
        self.nova = client.Client("2",session=sess)


    def flavor_access(self,flavor):
        return self.__get_flavor_access_list(flavor)

    def get_server_name_from_id(self,server_id):
        return self.nova.servers.get(server_id).name

    def grant_to_flavor(self,flavorname,projectid):
        try:
            flid = self.__get_flavor_id(flavorname)
            self.nova.flavor_access.add_tenant_access(flid,projectid)
            return True
        except Exception as e:
            log.logger.debug(e)
            return False


    def update_quota(self,project_id,items):
        kwargs = self.__quota_compare(project_id,items)
        if kwargs != {}:
            kwargs.update({"tenant_id": project_id})
            try:
                self.nova.quotas.update(**kwargs)
                log.logger.info("trying to update project_id: %s with quota: %s" % (project_id,kwargs))
            except Exception as e:
                log.logger.warning(e)



    def __quota_compare(self,project_id,items):
        current = self.__list_quota(project_id)
        new = {}
        for key,value in items.iteritems():
            try:
                if value != getattr(current,key):
                    new.update({key: value})
            except Exception as e:
                log.logger.warning("Could not parse quota of project %s with quota setting %s" % (project_id,key))
        return new

    def __list_quota(self,project_id):
        return self.nova.quotas.get(project_id)

    def revoke_to_flavor(self,flavorname,projectid):
        try:
            flid = self.__get_flavor_id(flavorname)
            self.nova.flavor_access.remove_tenant_access(flid,projectid)
            return True
        except Exception as e:
            log.logger.debug(e)
            return False

    def __get_flavor_access_list(self,flavor):
        flid = self.__get_flavor_id(flavor)
        if not flid:
            raise NameError("Flavor %s does not exist" % flavor)
        else:
            return self.nova.flavor_access._list_by_flavor(flid)

    def __get_flavor_id(self,flavor):
        all_flavors = self.nova.flavors.list(is_public=False)
        #log.logger.debug(all_flavors)
        exists = False
        for f in all_flavors:
            #log.logger.debug(f.name)
            if f.name == flavor:
                exists = f.id
                break
        return exists








#sess = session.Session(auth=auth,verify='cert/stack_naturalis_nl.ca-bundle')
