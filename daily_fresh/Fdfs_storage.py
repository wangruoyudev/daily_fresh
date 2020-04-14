from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import *


class FdfsStorage(Storage):
    def __init__(self, option=None):
        if not option:
            print(settings.CUSTOM_STORAGE_OPTIONS)
            self.config_file_path = settings.CUSTOM_STORAGE_OPTIONS['client_config']
            self.nginx_domain = settings.CUSTOM_STORAGE_OPTIONS['nginx_domain']
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        print('=====>name:', name)
        postfix = None
        postfix_list = str.split(name, '.')
        if len(postfix_list) > 1:
            postfix = postfix_list[-1]
        print('===>self.config_file_path:', self.config_file_path)
        track_conf_map = get_tracker_conf(self.config_file_path)
        print('===>track_conf_map:', track_conf_map)
        fdfs_cli = Fdfs_client(track_conf_map)
        ret = fdfs_cli.upload_by_buffer(content.read(), file_ext_name=postfix)
        print(ret)
        if ret['Status'] == 'Upload successed.':
            return ret['Remote file_id'].decode()
        else:
            raise Exception('上传fast-dfs失败')

    def exists(self, name):
        return False

    def url(self, name):
        print('====>url-name:', name)
        return self.nginx_domain + name