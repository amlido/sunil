#self.backend.get_class("Directory")
import os
import re
import sys
import requests

import json
import base64
import zlib
import hashlib
from collections import OrderedDict
from copy import copy
from copy import deepcopy

from sys import platform
os_name = platform.lower()
if os_name == 'linux':
    import readline
elif os_name == 'darwin':
    import readline

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs

from blended.jinjaenv import BlendedEnvironment

from blended_hostlib.exceptions import BlendedException, \
    PackageNameExistsException

ALLOWED_IMAGE_TYPES = ['.jpg', '.jpeg', '.bmp',
                       '.gif', '.tif', '.png',
                       '.ico', '.webp', '.otf', 
                       '.eot', '.svg', '.ttf', 
                       '.woff', '.woff2']

SAVE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "save_files/")
LOAD_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "Load_files/")

DEFAULT_CHUNK_SIZE = 64 * 2 ** 10


class Controller(object):
    """
    Controller class
    """
    def __init__(self, network, backend):
        """
        Initialization method of controller class.
        """
        self.network = network
        self.backend = backend
        self.root_directory = backend.directory_path
        self.src_or_lib = None
        
    def account_login(self, username, password):
        """
        account login call and stores sessionkey in filesystem.
        """
        pass

    def create_account(self, **kwargs):
        """
        """
        try:
            response = self.network.create_account(kwargs)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def activation_solution(self, challenge):
        """
        :param challenge:
        :return: solution
        """
        operands = challenge['operands']
        operator = challenge['operator']
        if operator == 'SQUARE':
            num = operands[0]
            return num ** 2

        num1, num2 = operands

        if operator == 'DIVIDE':
            solution = int(num1 / num2)
        elif operator == 'MULTIPLY':
            solution = num1 * num2
        elif operator == 'SUM':
            solution = num1 + num2
        elif operator == 'SUBTRACT':
            solution = num1 - num2
        elif operator == 'MODULO':
            solution = int(num1 % num2)

        return solution


    def update_account(self, user_pk, **kwargs):
        """
        """
        try:
            response = self.network.update_account(user_pk, kwargs)
        except BlendedException as exc:
            raise BlendedException(exc)

    def get_current_account(self, user_pk):
        """
        """
        try:
            response = self.network.get_current_account(user_pk)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def get_account_list(self, user_pk):
        """
        """
        try:
            response = self.network.get_account_list(user_pk)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def invite_user(self, user_slug, **kwargs):
        """
        :param user_slug:
        :param kwargs:
        :return:
        """
        try:
            response = self.network.invite_user(user_slug, kwargs)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def accept_invite(self, user_slug, **kwargs):
        """
        :param user_slug:
        :param kwargs:
        :return:
        """
        try:
            response = self.network.add_account_user(user_slug, kwargs)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def get_account_users(self, slug):
        """
        """
        try:
            response = self.network.get_account_users(slug)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def revoke_account(self, slug, account_slug):
        """
        """
        try:
            response = self.network.remove_account(slug, account_slug)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def set_current_account(self, account_name):
        """
        :param account_name:
        :return:
        """
        body = {'slug': account_name}
        try:
            response = self.network.set_current_account(body)
        except BlendedException as exc:
            raise BlendedException(exc)

        return response

    def create_package(self, account_name, package_name, package_type, description):
        """
        """
        self.backend.set_src
        try:
            self.backend.create_package(account_name, package_name, package_type, description)
        except BlendedException as exc:
            raise BlendedException(exc)
        else:
            if description:
                body = {'slug': package_name, 'type': package_type, 'description': description}
            else:
                body = {'slug': package_name, 'type': package_type}
            try:
                response = self.network.create_package(account_name, body)
            except BlendedException as exc:
                raise BlendedException(exc)

        package_obj = self.backend.get_package(package_name, entry=False)
        package = self.as_jptf(package_obj)
        draft_body = {'name': package_name, 'documents': package}
        try:
            draft_response = self.network.create_draft(account_name, package_name, draft_body)
        except BlendedException as ex:
            raise BlendedException(ex)
        else:
            tokens = draft_response.to_dict().get('tokens', None)
            self.upload_media(account_name, tokens, package_name)

        return "Package %s is Created Successfully" % (package_name)

    
    def get_package_acquisition(self, package_name, **kwargs):
        """
        method to get package from hub.
        """
        body = {}
        license_name = kwargs.get('license_name') 
        new_name = kwargs.get('new_name')
        identifiers = package_name.split("/")

        if len(identifiers) > 1:
            account = identifiers[0]
            package_slug = identifiers[1]
        else:
            account = kwargs.get('current_account')
            package_slug = identifiers[0]

        if new_name:
            body.update({'new_package_slug': new_name})

        if license_name:
            body.update({'type': 'get', 'license_name': license_name})
        else:
            body.update({'type': 'get'})

        try:
            response = self.network.acquire_package(account, package_slug, body)
        except PackageNameExistsException as ex:
            raise PackageNameExistsException(ex)
        except BlendedException as exc:
            raise BlendedException(exc)

        return response

    def package_detail(self, package_id):
        """
        """
        try:
            response = self.network.get_package_details(package_id)
        except BlendedException as exc:
            raise BlendedException(exc)
        return response

    def package_share(self, account_slug, package_id, **kwargs):
        """
        """
        account_name = kwargs.get('account_name') 
        body = {'type': 'share', 'account_slug': account_name}
        try:
            response = self.network.acquire_package(account_slug, package_id, body)
        except BlendedException as exc:
            raise BlendedException(exc)
        return True

    def package_transfer(self, account_slug, package_id, **kwargs):
        """
        """
        account_name = kwargs.get('account_name') 
        body = {'type': 'transfer', 'account_slug': account_name}
        try:
            response = self.network.acquire_package(account_slug, package_id, body)
        except BlendedException as exc:
            raise BlendedException(exc)
        return True

    def package_clone(self, package_name, **kwargs):
        """
        """
        body = {}
        new_name = kwargs.get('new_name')
        draft = kwargs.get('draft')
        label = kwargs.get('label')
        description = kwargs.get('description')
        current_account = kwargs.get('current_account')
        identifiers = package_name.split("/")
        if len(identifiers) > 1:
            account = identifiers[0]
            package_slug = identifiers[1]
        else:
            account = current_account
            package_slug = identifiers[0]

        if new_name:
            body.update({'new_package_slug': new_name})

        if draft:
            body.update({'type': 'clone', 'label': 'draft'})
        elif label:
            body.update({'type': 'clone', 'label': label})
        else:
            body.update({'type': 'clone', 'label': 'canonical'})

        try:
            response = self.network.acquire_package(account, package_slug, body)
        except PackageNameExistsException as ex:
            raise PackageNameExistsException(ex)
        except BlendedException as exc:
            raise BlendedException(exc)

        return response

    def install_package(self, package_name, **kwargs):
        """
        :param package_name:
        :param kwargs:
        :return:
        """
        package = []
        hub_package = []
        label = kwargs.get('label')
        current_account = kwargs.get('current_account')
        identifiers = package_name.rsplit("/")
        if len(identifiers) > 1:
            account = identifiers[0]
            package_slug = identifiers[1]
        else:
            account = current_account
            package_slug = identifiers[0]

        if (label) and (not ((label == 'draft') or (label == 'canonical'))):
            try:
                hub_package = self.network.download(account, package_slug, label)
            except BlendedException as exc:
                raise BlendedException(exc)
        else:
            try:
                hub_package = self.network.download_canonical(account, package_slug)
            except BlendedException as exc:
                raise BlendedException(exc)
        hub_package, package_hash = self._remove_root_from_jptf(hub_package)
        package = self.de_jptf(hub_package)
        self.save_local(package_slug, intermediary_object=package, dependency=True, account=account)
        self.download_dependencies(package)


    def download_dependencies(self, intermediary_object):
        dependencies = []
        project_dot_json = {}
        current_account = self.backend.get_current_account()
        if not intermediary_object:
            return None
        project_dot_json = json.loads([list(item.values())[0] for item in intermediary_object if (list(item.keys())[0] == '_project.json')][0])
        dependencies = project_dot_json.get('dependencies')
        if dependencies:
            for dependent_packages in dependencies:
                package_name = dependent_packages.get('name')
                version = dependent_packages.get('version')
                try:
                    self.install_package(package_name,
                                         label=version,
                                         current_account=current_account)
                except BlendedException as exc:
                    #import pdb;pdb.set_trace()
                    print("\n%s while installing dependency package %s\n" % (exc.args[0].args[0].get('message'), package_name))
                    continue

    def pull_package(self, package_name, force=False, **kwargs):
        """
        """
        version = kwargs.get('version')
        replace_from_local_list = kwargs.get('replace_from_local_list')
        #package_id = kwargs.get('package_id')
        is_draft = kwargs.get('draft')
        user_slug = kwargs.get('user_slug')
        label = kwargs.get('label')
        current_account = kwargs.get('current_account')
        if package_name:
            identifiers = package_name.rsplit("/")
            if len(identifiers) > 1:
                account = identifiers[0]
                package_slug = identifiers[1]
            else:
                account = current_account
                package_slug = identifiers[0]
        #import pdb;pdb.set_trace()
        if is_draft:
            try:
                #import pdb;pdb.set_trace()
                hub_package = self.network.download_draft(account, package_slug)  # account , as_hash must be here
            except BlendedException as exc:
                raise BlendedException(exc)
        elif label:
            try:
                hub_package = self.network.download(account, package_slug, label)
                #hub_package = self.network.download(account, package_slug)# account ,version , as_hash must be here
            except BlendedException as exc:
                raise BlendedException(exc)
        else:
            try:
                #hub_package = self.network.download(account, package_slug, label)
                hub_package = self.network.download_canonical(account, package_slug)# account ,version , as_hash must be here
            except BlendedException as exc:
                raise BlendedException(exc)

        try:
            hub_package, package_hash = self._remove_root_from_jptf(hub_package)
            hub_package = self.de_jptf(hub_package)
            hub_package = self.backend.get_class('intermediary')(
                                       package_slug, content=hub_package, 
                                       name=package_slug, hash=package_hash)
           
        except BlendedException as exc:
            raise BlendedException(exc)
        #account_package_name = os.path.join(account, package_slug)
        if force:
            try:
                if is_draft:
                    self.save_local(package_slug, intermediary_object=hub_package, draft=True)
                else:
                    self.save_local(package_slug, intermediary_object=hub_package, current_account=current_account, account=account)
            except BlendedException as exc:
                raise BlendedException(exc)
            else:
                return []
        if is_draft:
            package = self.get_package(package_name, "as_hash", version='draft')
        else:
            package = self.get_package(package_name, "as_hash", version=label)

        if replace_from_local_list:
            if is_draft:
                self.save_local(package_slug,
                                intermediary_object=self.merge_package(hub_package,
                                                                       package,
                                                                       replace_from_local_list),
                                draft=True)
            else:
                self.save_local(package_slug,
                                intermediary_object=self.merge_package(hub_package,
                                                                       package,
                                                                       replace_from_local_list),
                                current_account=current_account, account=account)
            return []
        differences = self.compare_package(hub_package, package, "pull")
        if differences:
            return differences
        if is_draft:
            saved_package = self.save_local(package_slug, intermediary_object=hub_package, draft=True)
        else:
            saved_package = self.save_local(package_slug, intermediary_object=hub_package, current_account=current_account, account=account)
        return saved_package
        pass

    def push_package(self, package_name, force=False, **kwargs):
        """
        """
        version = kwargs.get('version')
        replace_from_hub_list = kwargs.get('replace_from_hub_list')
        package_id = kwargs.get('package_id')
        user_slug = kwargs.get('user_slug')
        if package_name:
            identifiers = package_name.split("/")
            if len(identifiers) > 1:
                account = identifiers[0]
                package_slug = identifiers[1]
            else:
                try:
                    account = self.backend.get_current_account()
                except BlendedException as exc:
                    raise BlendedException(exc)
                package_slug = identifiers[0]

        try:
            package = self.backend.get_package(package_slug)
        except BlendedException as exc:
            raise BlendedException(exc)
        if force:
            try:
                return self.save_hub(account, package_slug, package)
            except BlendedException as exc:
                raise BlendedException(exc)
        try:
            #hub_package = self.network.download(package_slug, account, version, as_hash=True)
            hub_package = self.network.download_draft(account, package_slug)
        except BlendedException as exc:
            raise BlendedException(exc)
        try:
            package, package_hash = self.as_hash(package)
        except BlendedException as exc:
            raise BlendedException(exc)

        if replace_from_hub_list:
            self.save_hub(account, package_slug, self.merge_package(package, hub_package, replace_from_hub_list))
        local_last_hash = self.backend.get_hash(package_slug)
        differences = self.compare_package(hub_package, package,
                                           "push", package_current_hash=package_hash,
                                           package_last_hash=local_last_hash)
        if differences:
            return differences
        return self.save_hub(account, package_slug, package, force=force)


    def file_hash(self, project_object, path='', hashed_package=[]):
        """
        :param project_object:
        :param path:
        :param package:
        :return:
        """
        try:
            assert type(project_object) == list
            for index, item in enumerate(project_object):
                assert type(item) == dict
                key = list(item.copy().keys())[0]
                value = list(item.copy().values())[0]
                keys = key.rsplit('.', 1)

                if (len(keys) > 1):
                    with_extension = True
                    extension = ('.%s' % (keys[1]))
                else:
                    with_extension = False
                if (type(value) is list):
                    new_path = path + '/' + key
                    hashed_package = self.file_hash(value, path=new_path, hashed_package=hashed_package)
                elif (with_extension and extension.lower() in ALLOWED_IMAGE_TYPES):
                    # import pdb; pdb.set_trace()
                    new_path = path + '/' + key
                    image = self.backend.get_media(value)
                    hash_value = self.compute_hash(image)
                    hashed_package.append({'path': new_path, 'hash': hash_value})

                elif (type(value) is dict):
                    new_path = path + '/' + key
                    value = hashlib.md5(json.dumps(value, sort_keys=True).encode('utf-8')).hexdigest()
                    hashed_package.append({'path': new_path, 'hash': value})
                else:
                    new_path = path + '/' + key
                    if (not type(value) is bytes):
                        value = value.encode('utf-8')
                    value = hashlib.md5(value).hexdigest()
                    hashed_package.append({'path': new_path, 'hash': value})

            return hashed_package
        except AssertionError as exc:
            return None


    def as_hash(self, package):
        """
        :param package:
        :return:
        """
        hashes = []
        hashed_package = self.file_hash(package)
        for item in hashed_package:
              hashes.append(item['hash'])

        package_hash = hashlib.md5((':'.join(hashes)).encode('utf-8')).hexdigest()
        #package.append({'current_hash': package_hash})
        return hashed_package, package_hash

    def compare_package(self, hub_package, local_package, action, **kwargs):
        """
        """
        local_last = kwargs.get('package_last_hash')
        hub_current = hub_package.get('package_draft_hash')
        local_current = kwargs.get('package_current_hash')

        if action == "push":
            if hub_current == local_last:
                return []
            else:
                remote_package = hub_package.get('hashes')
                return self.differences(remote_package, local_package)

        elif action == "pull":
            if local_last == local_current:
                return []
            else:
                remote_package = hub_package.get('hashes')
                return self.differences(remote_package, local_package)

    def merge_package(self, final_package, replace_package, replace_list):
        """
        """
        for file_to_replace in replace_list:
            for file_in_replace_package in replace_package:
                if file_to_replace == file_in_replace_package:
                    
            #file = find file_to_replace in replace_package
            #final_package[file_to_replace location] = file
                    pass
        return final_package

    def differences(self, remote_package, local_package):
        """
        """
        diffs = []
        for items in local_package:
            hash_at_path = items.get('hash')
            path = items.get('path')
            path_list = path.split('/')
            path_list.pop(0)
            hash_bool = self.file_difference(remote_package, path_list, hash_at_path)
            if hash_bool:
                diffs.append(path)
        #for package_file in remote_package:
        #    if isinstance(package_file, list):
        #        diffs.append(self.differences(package_file, local_package[package_file]))
        #    if isinstance(package_file, dict):
        #        if package_file['hash'] != local_package[package_file]['hash']:
        #            diffs.append(package_file)
        return diffs

    def file_difference(self, remote_package, path_list, hash_at_path):
        #import pdb;pdb.set_trace()
        index = path_list.pop(0)
        for files in remote_package:
            if isinstance(files, dict):
                key = list(files.copy().keys())
                length = len(path_list)
                if (index in key) and (length>0):
                    #import pdb;pdb.set_trace()
                    hash = self.file_difference(files[index]['Document'], path_list, hash_at_path)
                elif (index in key) and (length==0):
                    file_hash = files[index]['hash']
                    if file_hash != hash_at_path:
                        hash = True
                    else:
                        hash = False
        return hash

    def preview(self, url, **kwargs):
        """
        :param url:
        :return:
        """
        url_split = url.split(os.sep)
        account = kwargs.get('account')
        length_of_url = len(url_split)
        theme = url_split[0]
        version = url_split[1]
        template = url_split[2]
        if length_of_url == 4:
            q_string = url_split[3]
        else:
            q_string = ''
        query_dict = parse_qs(q_string)
        query_string = {}
        if query_dict:
            list_of_query_string = [{key: value[0]} for key, value in query_dict.items()]
            for query in list_of_query_string:
                query_string.update(query)

        if account:
            theme = '%s/%s' % (account, theme)
        context = dict(self.get_package(theme, "context", version))
        if query_string:
            for key, value in query_string.items():
                location = key.split(".")
                location.pop(0)
                context = self.context_change(context, location, value)

        preview_template = context.get('preview').get(template)
        context = {'theme': context}
        #return render_code(preview_template, context)
        return preview_template, context

    def context_change(self, theme_object, location_array, new_value):
        """
        :param theme_object:
        :param location_array:
        :param new_value:
        :return:
        """
        while(location_array):
            index_value = location_array.pop(0)
            if len(location_array) > 0:
                self.context_change(theme_object[index_value], location_array, new_value)
            else:
                theme_object[index_value] = new_value

        return theme_object

    #def render_code(self, file_content, context):
     #   """
     #   :param file_content: compiled template content
     #   :param context: theme_object or context
     #   :return: rendered content of template.
     #   """
     #   template = env.from_string(file_content, context)
     #   return template.render(context)

    @property
    def set_backend_root(self):
        self.backend.directory_path = self.root_directory

    def download_package(self, package_id, package_name):
        """
        """
        try:
            response = self.network.download(package_id)
        except BlendedException as exc:
            raise BlendedException(exc)
        try:
            intermediary_object = self.de_jptf(response)        
            self.backend.save_local(package_name, intermediary_object)
        except BlendedException as exc:
            raise BlendedException(exc)

    def download_package_draft(self, package_id, package_name):
        """
        """
        try:
            response = self.network.download_draft(package_id)
        except BlendedException as exc:
            raise BlendedException(exc)
        try:
            intermediary_object = self.de_jptf(response)        
            self.backend.save_local(package_name, intermediary_object)
        except BlendedException as exc:
            raise BlendedException(exc)

    def package_accounts_list(self, slug=None, package_name=None):
        """
        :param slug: Account Name or Account Slug
        :param package_name: Package Name or Package Slug
        :return:
        """
        package_account_list = []
        try:
            response = self.network.package_accounts_list(slug, package_name)
        except BlendedException as exc:
            raise BlendedException(exc)
        else:
            package_items = response.items
            for item in package_items:
                package_account_list.append({'name': item.name, 'pk': item.pk})
        return package_account_list

    def packages_list(self, slug=None):
        """
        """
        package_list = []
        package_dict = {}
        try:
            if slug:
                response = self.network.package_list(slug)
            else:
                response = self.network.package_list()
        except BlendedException as exc:
            raise BlendedException(exc)
        else:
            package_items = response.items
            for item in package_items:
                package_list.append({'name': item.slug, 'pk': item.pk})
                package_dict.update({item.slug: item.pk})
        try:
            filesystem = self.backend.package_list(package_dict)
        except BlendedException as exc:
            raise BlendedException(exc)
        return package_list
    
    def read_package_pk(self, package_name):
        """
        """
        try:
            package_pk = self.backend.read_package_pk(package_name)
        except BlendedException:
            raise BlendedException()
        return package_pk

    def package_extend(self, package_name, **kwargs):
        """
        :param package_name:
        :param kwargs:
        :return:
        """
        new_name = kwargs.get('new_name')
        is_draft = kwargs.get('draft')
        label = kwargs.get('label')
        description = kwargs.get('description')
        current_account = kwargs.get('current_account')
        hub_package = None

        if package_name:
            identifiers = package_name.rsplit("/")
            if len(identifiers) > 1:
                account = identifiers[0]
                package_slug = identifiers[1]
            else:
                try:
                    account = current_account
                except BlendedException as exc:
                    raise BlendedException(exc)
                package_slug = identifiers[0]

        packages = self.backend.packages_in_src()
        lib_packages = self.backend.packages_in_lib(account)

        if package_slug in packages:
            self.backend.set_src
            package = self.backend.get_package(package_slug, entry=False)
            self.set_backend_root
        #elif package_slug in lib_packages:
        #    self.backend.set_lib(account)
            #package = self.backend.get_package(package_slug, entry=False)
            #self.set_backend_root
        else:
            if is_draft:
                try:
                    #import pdb;pdb.set_trace()
                    label = 'draft'
                    hub_package = self.network.download_draft(account, package_slug)  # account must be here
                except BlendedException as exc:
                    raise BlendedException(exc)
            else:
                try:
                    hub_package = self.network.download(account, package_slug, label)# account, version_label  must be here
                except BlendedException as exc:
                    raise BlendedException(exc)
            try:
                hub_package, package_hash = self._remove_root_from_jptf(hub_package)
                package = self.de_jptf(hub_package)
                package = self.backend.get_class('intermediary')(
                                       package_slug, content=package, 
                                       name=package_slug, hash=package_hash)
            except BlendedException as exc:
                raise BlendedException(exc)
            try:
                if is_draft:
                    self.save_local(package_slug, intermediary_object=package, draft=True)
                else:
                    self.save_local(package_slug, intermediary_object=package,
                                    current_account=current_account, account=account)
            except BlendedException as exc:
                raise BlendedException(exc)

        self.backend.set_src
        self.backend.create_extended_package(package_slug, package, new_name, account=account,
                                             description=description, label=label)
        self.set_backend_root
        #dependency_packages = self.network.get_dependencies(package_name)
        return True

    def package_snapshot(self, account_slug, slug, **kwargs):
        """
        """
        #here package_id is Package_slug/package_name
        label = kwargs.get('label')
        body = {'label': label}
        self.backend.set_src
        try:
            response = self.network.snapshot(account_slug, slug, body)
        except BlendedException as exc:
            raise BlendedException(exc)
        try:
            #package_name = self.read_package_name(package_id)
            self.backend.update_blendedrc(slug, label=label, version_pk=response.pk)
            #package_path = os.path.join(self.backend.directory_path, slug, '_project.json')
            #self.backend.update_project_dot_json(package_path, {'version': label})
        except BlendedException:
            raise BlendedException("Version pk not updated")
        return "Package is Snapshot with version label %s" % (label)

    def read_package_name(self, package_id):
        """
        """
        try:
            package_name = self.backend.read_package_name(package_id)
        except BlendedException:
            raise BlendedException()
        return package_name

    def package_canonical(self, account_slug, slug, **kwargs):
        """
        """
        label = kwargs.get('label')
        body = {'is_canonical': True}
        #package_name = self.read_package_name(package_id)
        #version_id = int(self.backend.get_version_id(package_name, label))
        #self.backend.check_lib_or_src(slug)
        try:
            response = self.network.set_canonical(account_slug, slug, label, body)
        except BlendedException as exc:
            raise BlendedException(exc)
            
        return "Canonical Version of Package is created"

    def package_publish(self, account_slug, slug, **kwargs):
        """
        """
        label = kwargs.get('label')
        #package_name = self.read_package_name(package_id)
        #version_id = int(self.backend.get_version_id(package_name, label))
        body = {'publish': True}
        try:
            response = self.network.set_canonical(account_slug, slug, label, body)
        except BlendedException as exc:
            raise BlendedException(exc)
        return "Package is published with version label %s" % (label)

    def package_addlicense(self, account_slug, slug, license_name, license_price, label):
        """
        """
        body = {'name': license_name, 'price': license_price}
        try:
            response = self.network.add_license(account_slug, slug, label, body)
        except BlendedException as exc:
            raise BlendedException(exc)

    def package_deletelicense(self, package_id, license_name):
        """
        """
        try:
            response = self.network.remove_license(package_id, license_name)
        except BlendedException as exc:
            raise BlendedException(exc)

    def get_package(self, package_name=None, format=None, version=None, trim=True, dependency=False):
        """
        it will load the intermediary project object in the jptf structure or in the proper context structure of the json format
        it will call the backend based on the backend name passed to it.for default it will use memory ...#todo
        """
        package = {}
        current_account = self.backend.get_current_account()
        if package_name:
            identifiers = package_name.rsplit("/")
            if len(identifiers) > 1:
                account = identifiers[0]
                package_slug = identifiers[1]
            else:
                account = current_account
                package_slug = identifiers[0]

        try:
            package = self.backend.get_package(package_name, dependency=dependency)
        except FileNotFoundError:
            if version == 'draft':
                hub_jptf = self.network.download_draft(account, package_slug)
                hub_jptf, package_hash = self._remove_root_from_jptf(hub_jptf)
                hub_package = self.de_jptf(hub_jptf)
                hub_package = self.backend.get_class('intermediary')(
                                       package_slug, content=hub_package, 
                                       name=package_slug, hash=package_hash)
                self.save_local(package_slug,
                                intermediary_object=hub_package,
                                account=account, current_account=current_account,
                                draft=True)

            else:
                hub_jptf = self.network.download(account, package_slug, version)# account, version will also be here
                hub_jptf, package_hash = self._remove_root_from_jptf(hub_jptf)
                hub_package = self.de_jptf(hub_jptf)
                hub_package = self.backend.get_class('intermediary')(
                                       package_slug, content=hub_package, 
                                       name=package_slug, hash=package_hash)

                self.save_local(package_slug,
                                intermediary_object=hub_package,
                                account=account, current_account=current_account,
                                version=version, dependency=dependency)

            package = self.backend.get_package(package_name, dependency=dependency)
                        
        if format == "jptf":            
            return self.as_jptf(package)
        elif format == "context":            
            package = self.as_context(package, trim=trim, dependency=dependency)
            src_or_lib = self.src_or_lib
            if (src_or_lib) and (src_or_lib.endswith('lib') or src_or_lib.endswith('src')):
                backend_directory_path = src_or_lib
            else:
                backend_directory_path = self.backend.directory_path
            package.update({'theme_name': package_slug,
                            'account': account, 'current_account': current_account,
                            'theme_path': backend_directory_path,
                            'root_path': self.root_directory})
            return package
        elif format == "as_hash":
            return self.as_hash(package)
        else:            
            return package

    def save_local(self, package_slug, **kwargs):
        """
        save the project in intermediary structure in the local backend based on the backedn used.call the backend and use 
        use it to save the file in backend (fileystem)
        """
        #package_id = kwargs.get('package_id')
        #draft = kwargs.get('draft')
        #label = kwargs.get('label')
        #import pdb; pdb.set_trace()
        intermediary_object = kwargs.get('intermediary_object')
        is_draft = kwargs.get('draft')
        version = kwargs.get('version')
        current_account = kwargs.get('current_account')
        dependency = kwargs.get('dependency')
        account_name = kwargs.get('account')
        try:
            if is_draft:
                self.backend.save_local(package_slug, intermediary_object, draft=is_draft)
            elif dependency:
                package_name = os.path.join(account_name, package_slug)
                self.backend.save_local(package_name, intermediary_object, dependency=dependency)
            elif account_name != current_account:
                package_name = os.path.join(account_name, package_slug)
                self.backend.save_local(package_name, intermediary_object, owner=False)
            else:
                self.backend.save_local(package_slug, intermediary_object)

        except BlendedException as exc:
            raise BlendedException(exc)



    def save_hub(self, account_name, package_name, blended_package, **kwargs):
        """
        convert intermediary package object into jptf and send it to Hub.
        """
        package = self.as_jptf(blended_package)
        body = {'name': package_name, 'documents': package}
        try:
            response = self.network.update_draft(account_name, package_name, body)
        except BlendedException as exc:
            raise BlendedException(exc)

        tokens = response.to_dict().get('tokens', None)
        self.upload_media(account_name, tokens, package_name)

        return response
            
    def upload_media(self, account_name, tokens, package_name):
        """
        """
        for token in tokens.items():            
            media_path = os.path.join(package_name, token[0])
            image = self.backend.get_media(media_path)
            hash_value = self.compute_hash(image)
            try:
                self.network.upload_media(account_name, str(package_name),
                                          hash_value, name=token[0],
                                          image=image.name, token=token[1])
            except BlendedException:
                print("\nsome error in uploading image %s" % (image.name))
                continue
                                
    def validate_local(self, project_object):
        """
        """
        #todo in near future
        backend = BackendLoader.get_backend("filebase")
        project = self.as_jptf(project_object)
        backend.validate(project)

    def validate_hub(self, project_object):
        """
        """
        project = self.as_jptf(project_object)
        #client.validate(project)

    def save_js(self, name, content):
        """
        save the javascript file with name and content of the file and return the url of save location
        """
        url = self.backend.save_js(name, content)
        return url

    def save_css(self, name, content):
        """
        save the css file with name and content of the file and return the url of save location
        """
        url = self.backend.save_css(name, content)
        return url

    
    def get_image(self,image_name):
        """
        image_name is searched in the theme/media directory. 
        """
        backend = BackendLoader.get_backend("filebase")
        url = backend.get_image(image_name)
        return url

    def load_image(self, image_url):
        """
        load the image as PIL Object form from the image_url full path of the image location
        and returns the pil object used by transform
        """
        backend = BackendLoader.get_backend()
        image = backend.load_image(image_url)
        return image

    def save_image(self, image_name, image_content):
        """
        save the image_content(pil object) using the backend in a particular save directory and returns the path
        """
        backend = BackendLoader.get_backend()
        url = backend.save_image(image_name, image_content)
        return url

    def compute_hash(self, content):
        """
        """                
        hasher = hashlib.sha1()
        cursor = content.tell()
        content.seek(0)
        try:
            while True:
                data = content.read(DEFAULT_CHUNK_SIZE)
                if not data:
                    break
                hasher.update(data)
            return hasher.hexdigest()
        finally:
            content.seek(cursor)

    
    def as_jptf(self, intermediary):
        """
        """
        jptf = self.intermediary_to_jptf(intermediary )
        obj = [{"/" : {"type" : "directory", "hash" : intermediary.hash, "content" : jptf}}]
        return obj

    def intermediary_to_jptf(self, project_object):
        """
        """
        try:
            if project_object.__class__.__name__ == 'Directory':
                project_object =project_object.content
            for index, item in enumerate(project_object):
                key = item.name
                value = item.content
                keys = key.rsplit('.', 1)
                if(len(keys)>1):
                    with_extension = True
                    extension = ('.%s' % (keys[1]))
                else:
                    with_extension = False
                if(type(value) is list):
                    value = self.intermediary_to_jptf(value)            
                    project_object[index] = {key: {"type": "directory", "content": value}}
                elif(with_extension and extension.lower() in ALLOWED_IMAGE_TYPES):
                                      
                    project_object[index] = {key: {"type": "media", "hash": item.hash}}
                elif item.__class__.__name__ == 'JSONFile':
                    value = base64.b64encode(zlib.compress(value.encode('utf-8'))).decode('utf-8')
                    project_object[index] = {key: {"type": "file", "content": value, "hash": item.hash}}
                elif item.__class__.__name__ == 'TextFile':                
                    if(not type(value) is bytes):
                        value = value.encode('utf-8')
                    value = base64.b64encode(zlib.compress(value)).decode('utf-8')
                    project_object[index] = {key: {"type": "file", "content": value, "hash": item.hash}}
            return project_object
        except AssertionError as exc:
            return None

    def _remove_root_from_jptf(self, project_object):
        """
        :param project_object:
        :return:
        """
        jptf = project_object[0]['/']['content']
        package_hash = project_object[0]['/']['hash']
        return jptf, package_hash


    def de_jptf(self, project_object):
        """
        """
        
        data = []
        for i in project_object:  
            dict_copy = {}
            project_object_iter = i
            keys = list(project_object_iter.keys())

            for j_key in keys:
                key = j_key
                value = project_object_iter[key]
                if value['type'] == 'directory':
                    content = self.de_jptf(value['content'])
                    data.append(self.backend.get_class("Directory")(key, content=content, name=key, hash=value['hash']))
                elif key[-5:]=='.json':
                    content = zlib.decompress(base64.b64decode(value['content'])).decode('utf-8')
                    data.append(self.backend.get_class("JSONFile")(key, content=content, name=key, hash=value['hash']))
                elif value['type'] == 'media':
                    data.append(self.backend.get_class("BinaryFile")(key, content=value['href'], name=key, hash=value['hash']))
                elif value['type'] == 'file' and key[-5:]!='.json':
                    content = zlib.decompress(base64.b64decode(value['content'])).decode('utf-8')
                    data.append(self.backend.get_class("TextFile")(key, content=content, name=key, hash=value['hash']))
                   
              
        return data
                
    
     
    def intermediary_to_context(self, package, obj_to_return=None):
        """
        :param obj_to_return:
        :return:
        """
        image_class = self.backend.get_class('BinaryFile')
        package = package.content
        #import pdb;pdb.set_trace()
        if not obj_to_return:
            obj_to_return = {}
        for item in package:
            value=item
            key = item.name
            
            if isinstance(value.content, list):
                #import pdb;pdb.set_trace()
                obj_to_return[key] = {}
                obj_to_return.update({key: self.intermediary_to_context(value, obj_to_return[key])})
            elif isinstance(value, image_class):
                obj_to_return.update({key: value.location})
            else:
                if key.endswith('.json'):
                    value = json.loads(value.content)
                else:
                    value = value.content
                obj_to_return.update({key: value})
        return obj_to_return

    def as_context(self, project, trim=True, dependency=False):
        """
        as_context function is used to turn a project object in intermediary format into context format.  
        It also resolves all the json pointers including those pointing to dependencies before it returns it
        """
        dependency_dict = {}
        package = self.intermediary_to_context(project)

        project_json = package.get('_project.json', {})
        if project_json:
            #import pdb;pdb.set_trace() 
            dependency_list = project_json.get('dependencies', {})
            if(dependency_list):
                dependency_dict = self.load_dependency(dependency_list, dependency=dependency)
        #project.update(dependency_dict)
        package.pop('_project.json')
        package = self.order_project_dict(package)
        self.resolve(None, package, dependency_dict, None)
        if trim:
            self.trim_context(package)
        self.remove_index(package)
        return package

    def order_project_dict(self, project_object):
        """
        make the dict in ordered dict
        """
        return OrderedDict(sorted(list(project_object.items()), reverse=True))

    def remove_index(self, project_object):
        """
        remove the _index.json and _index the content to directly project object

        #not right now used was use in host doc vol 1
        """
        #project_object.update(project_object.pop('_index.json', {}))
        #project_object.update(project_object.pop('_index', {}))
        from copy import deepcopy
        unchanged_project_object = deepcopy(project_object)
        for key, value in unchanged_project_object.items():
            if (key == '_index') or (key == '_index.json'):
                project_object.update(project_object.pop(key, {}))
            elif isinstance(project_object.get(key), dict):
                self.remove_index(project_object.get(key))
        return self.order_project_dict(project_object)

    def trim_context(self, current_node):
        """
        trim context is make the _index json contents to outer loop and remove the key starting with _
        also it remove the file extension from the file name (key in dict)

        """
        from copy import copy
        current_node_iter = copy(current_node)
        if isinstance(current_node_iter, dict) and current_node_iter:
            for key, value in current_node_iter.items():
                if key == '_index':
                    for index_key, index_value in value.items():
                        current_node[index_key] = index_value
                    if key in current_node.keys():
                        current_node.update(current_node.pop(key, {}))
                        #current_node.popitem(key)
                else:
                    if key.startswith("_"):
                        if key in current_node_iter:
                            del current_node[key]
                z = key.rfind('.')
                if z >= 0:
                    new_key = key[:z]
                    current_node[new_key] = value
                    if key in current_node:
                        del current_node[key]
                self.trim_context(value)

    def dict_extension_remove(self, json_file):
        """
        do the same work as trim_context used in host doc vol-1 not now in use in host doc vol -2
        """
        new = {}
        for k, v in json_file.items():
            if k:
                z = k.rfind(".")
                if z >= 0:
                    k = k[:z]
            if isinstance(v, dict):
                var = {}
                var.update(self.dict_extension_remove(v))
                new[k] = var
            else:
                new[k] = v
        return new 

    def load_dependency(self, dependency_list, dependency=False):
        """
        load the dependency based on the alias name of the theme and the uuid 
        """
        dependency_dict = {}
        if not dependency:
            self.src_or_lib = self.backend.directory_path

        for dependency in dependency_list:
            dep_uuid = dependency.get('uuid')
            theme_slug = dependency.get('name')
            account = dependency.get('account')
            dep_alias = dependency.get('alias')
            version = dependency.get('version')

            if not version:
                version = 'draft'

            if dep_alias in dependency_dict:
                raise Exception("Alias: %s is not unique .please give unique alias " % dep_alias)
            self.set_backend_root
            dependency_dict[dep_alias] = dict(self.get_package(theme_slug, 'context', version, trim=False, dependency=True))
            self.set_backend_root

        if not dependency:
            self.backend.directory_path = self.src_or_lib

        return dependency_dict


    def resolve(self, current_node, project_object, dependency_dict, current_json_file):
        """
        The resolve function uses a few helper functions (ref_set, ref_get, resolve_pointer) in order to 
        resolve all Json Pointers used in the json files of the project_object

        pattern is {"$ref":"#/meta/config.json"}
        if ref is find then resolve
        """
        is_array = lambda var: isinstance(var, (dict))
        if(not current_node):
            current_node = project_object
        
        for key, value in current_node.items():
            if key[-5:] == '.json':
                current_json_file = current_node[key]

            current_value = current_node[key]

            if is_array(current_value):
                if '$ref' in value:
                    set_val = set()
                    current_node[key] = self.resolve_pointer(current_value,
                                             project_object, dependency_dict,
                                             set_val, current_json_file)
                else:
                    if not value:
                        continue
                    self.resolve(value, project_object, dependency_dict,
                                 current_json_file)

    def resolve_pointer(self, json_ref, project_object, dependency_dict,
                        visited_set, current_json_file):
        """
        A recursive function that resolves the ref passed in.  
        If the pointer points to another Json Pointer, the function calls itself but not before adding the first pointer to the set.
        The set is used to determine if a cycle is being entered. 
        
        logic -
        if we get a ref we store it in set to solve the case of the json cycle
        """
        is_array = lambda var: isinstance(var, (dict))        
        if(is_array(json_ref) and '$ref' in json_ref):
            pointer = json_ref['$ref']           
            if pointer in visited_set:
                raise Exception('A Json Pointer cycle has been detected')
            else:
                visited_set.add(pointer)
                json_ref = self.ref_get(pointer, project_object, current_json_file,dependency_dict,visited_set)
                if(not json_ref):
                    raise Exception('A Json Pointer cycle has been detected')

                self.resolve_pointer(json_ref, project_object, dependency_dict,
                                     visited_set, current_json_file)
        return json_ref

    def multiple_replace(self, dic, text):
        """
        it will replaec the dictionary value from a particular character
        """
        pattern = "|".join(map(re.escape, dic.keys()))
        return re.sub(pattern, lambda m: dic[m.group()], text)

    def ref_get(self, ref_value, project_object, json_file, dependency_dict, visited_set):
        """
        give the ref value where json is pointing or using teh alias name of the content
        give the content from the dependencies dict
        logic-
        if while resolving we get a another we will first resolve it and then update the dictionary and recursuilevely update 
        other dict

        we need to follow a pattern that first we will resolve the alias content and then we will reolve the ref so that in case
        we are depending on the theme both alias and ref is resolved
        """
        #if not isinstance(ref_value,dict):
        dicti_replace = {'#/': ''}
        dicti_replace1 = {'#': ''}
        dicti_replace2 = {'#/': '/'}

        if ref_value.find('@') == 0:
            ref_point = ref_value.find('/')
            if ref_point==-1:
                ref_point = len(ref_value) 
            path = ref_value[ref_point+1:]
            alias_name = ref_value[1:ref_point]
            path = self.multiple_replace(dicti_replace2, path)
            ref_value = self.get_value_at_path(path, dependency_dict[alias_name])
            return ref_value
        elif ref_value.find("#/") == 0:
            path = self.multiple_replace(dicti_replace, ref_value)
            ref_value = self.get_value_at_path(path, json_file)
            if isinstance(ref_value, dict):
                if '$ref' in ref_value:
                    if ref_value['$ref'] in visited_set:
                        raise Exception('A Json Pointer cycle has been detected')
                    visited_set.add(ref_value['$ref'])
                    ref_value = self.ref_get(ref_value['$ref'],project_object,json_file,dependency_dict,visited_set)
                    return ref_value
            return ref_value
        else:
            if ref_value.startswith('/'):
                ref_value = ref_value.split('/', 1)[1]
            path = self.multiple_replace(dicti_replace1, ref_value)
            ref_value = self.get_value_at_path(path, project_object)

        return ref_value

    def get_value_at_path(self, dir_path, project_object):
        """
        returns the value at the path by recursively searching in the current _json and the project_object
        """
        paths = dir_path.split('/')
        is_array = lambda var: isinstance(var, (dict))

        from copy import copy
        unchanged_project_object = copy(project_object)

        temp_value = project_object
        if dir_path=='':
            return temp_value
        for value in paths:
            try:
                if '$ref' in temp_value:
                    ref_value = temp_value['$ref']
                    #if ref_value in visited_set:
                    #    raise Exception('A Json Pointer cycle has been detected')
                    #visited_set.add(ref_value)
                    temp_value = self.ref_get(ref_value, 
                                              unchanged_project_object, 
                                              unchanged_project_object,
                                              {}, set())
                    #temp_value=self.ref_get(temp_value,project_object1,project_object1,{},visited_set)
                temp_value = temp_value[value]
            except KeyError:
                return '%s not found' % (value,)
        return temp_value  
     
    def get_theme_data(theme_object, template, block):
        """
        get theme data is to be moved to blendedhostfunction class
        #todo
        """
        grid = theme_object['meta']['grid']['all']
        if block in theme_object['meta']['grid']['blocks']:
            grid.update(theme_object['meta']['grid']['blocks'][block])
        if template in theme_object['meta']['grid']['templates']:
            grid.update(theme_object['meta']['grid']['templates'][template]['all'])
            if block in theme_object['meta']['grid']['templates'][template]['blocks']:
                grid.update(theme_object['meta']['grid']['templates'][template]['blocks'][block])
        theme_object['meta']['grid'].update(grid)
        return theme_object

    def get_directory(self, dep_uuid):
        """
        """
        uuid_map = self.get_uuid_map()
        if bool(uuid_map.get(dep_uuid)):
            directory = uuid_map.get(dep_uuid)
        else :
            raise Exception("Directory dependency uuid not found" + dep_uuid_)
        return directory

    def get_uuid_map(self):
        
        global BLENDED_DIR
        global ACTIVE_ORGANIZATION
        global UUID_MAP
        if UUID_MAP:
            return UUID_MAP
        layouts = BLENDED_DIR.strip('\'') + '/blended/'+ ACTIVE_ORGANIZATION.strip('\'') + '/layouts'
        themes = BLENDED_DIR.strip('\'') + '/blended/'+ ACTIVE_ORGANIZATION.strip('\'') + '/themes'
        theme_groups = BLENDED_DIR.strip('\'') + '/blended/'+ ACTIVE_ORGANIZATION.strip('\'') + '/theme_groups'
        UUID_MAP.update(self.get_uuids(layouts))
        UUID_MAP.update(self.get_uuids(themes))
        UUID_MAP.update(self.get_uuids(theme_groups))
        return UUID_MAP


    def get_uuids(self, directory_path):
        """
        """ 
        uuid_map={}
        project_json = {}
        project_json_file = '_project.json'
        projects = os.listdir(directory_path)
        try:
            projects = projects.remove('.')
            projects = projects.remove('..')
        except ValueError:
            pass
        for project in projects:
            if os.path.isfile(os.path.join(directory_path , project ,project_json_file)):
                with open(os.path.join(directory_path , project ,project_json_file), 'r') as content_file:
                    project_json = json.load(content_file)

                project_json_uuid = project_json.get('uuid', None)
                if(project_json_uuid):
                    uuid = project_json_uuid
                if(uuid):
                    uuid_map[uuid] = os.path.join(directory_path, project)
        return uuid_map
