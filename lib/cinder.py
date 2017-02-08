from keystoneclient.auth.identity import v3
from keystoneclient import session
from cinderclient import client
from utils import log


class Cinder():

    def __init__(self, auth_url, username, password, project_name, cacert,
                 project_id):
        auth = v3.Password(auth_url=auth_url,
                           username=username,
                           password=password,
                           project_id=project_id,
                           user_domain_name='Default',
                           project_domain_id='Default')
        sess = session.Session(auth=auth, verify=cacert)
        self.cinder = client.Client('2', session=sess)

    def update_quota(self, project_id, items):
        updates = self.__quota_compare(project_id, items)
        if updates != {}:
            updates.update({"tenant_id": project_id})
            try:
                self.cinder.quotas.update(**updates)
                log.logger.info("Trying to update project_id: %s with quota: %s"
                                % (project_id, updates))
            except Exception as e:
                log.logger.warning(e)

    def __get_quota(self, project_id):
        return self.cinder.quotas.get(project_id)

    def __quota_compare(self, project_id, items):
        current = self.__get_quota(project_id)
        new = {}
        for key, value in items.iteritems():
            try:
                if value != getattr(current, key):
                    new.update({key: value})
            except Exception as e:
                log.logger.warning("Could not parse quota of project %s with "
                                   "quota setting %s" % (project_id, key))
        return new

    def get_volume_info(self):
        """
        Get info about volumes in a project
        * Needs project_id
        Return array with objects with id, attached, attached_to, size, type
        """
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
                            'status': v.status})

        return payload
