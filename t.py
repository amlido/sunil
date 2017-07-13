import unittest

def fun(x):
    return x + 1

class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)
if __name__ == '__main__':
    import doctest
    doctest.testmod()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    import os
import sys

from getpass import getpass

from cliff.command import Command
from blended_hostlib.initializer import Route
from blended_hostlib.backend import FileSystemBackend
from blended_hostlib.network import Network
from blended_hostlib.controller import Controller
from blended_hostlib.exceptions import BlendedException, PackageNameExistsException

from blendedcli.spinner import Spinner
from blendedcli.args_setter import PackageInfo,AccountInfo
from blendedcli.theme_preview import theme_app, extra_files
from blendedcli.helpers import *


CACHE_DIR = IMAGE_CACHE_DIR
blended_dir = BLENDED_DIR
domain_address = DOMAIN


class StreamType(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            description = ''
            for information in values.readlines():
                description = description + information
            #print(values.readlines())
            setattr(namespace, self.dest, description)
        except AttributeError:
            setattr(namespace, self.dest, values)


class PackageCreate(Command):
    """
    Cammand to Create Package.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageCreate, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name that need to be created")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--type', nargs='?', default=None)
        parser.add_argument('--description', nargs='?', const=sys.stdin, action=StreamType, default=None)
        return parser

    def take_action(self, parsed_args):
        package_name = parsed_args.package_name
        package_type = parsed_args.type
        error_message_1 = "Entered Wrong Choice for Package Type. Command's operations are cancelled"
        error_message_2 = "Enter invalid data for Package Type. Command's operations are cancelled"
        
        if not package_name:
            package_name = input("Please Enter Package Name: ")
        if not package_type:
            print("Package Type:")
            for index, items in enumerate(PACKAGES_TYPE):
                print('{2:>5}{0:{width}1}{1}'.format(str(index + 1), items, '', width=1))
            try:
                package_type = int(input("Please Enter Number of Package Type: "))
            except ValueError:
                return error_message_2
        else:
            try:
                package_type = int(package_type)
            except ValueError:
                return error_message_2

        if package_type == 0:
            return error_message_1
        try:
            package_type_name = PACKAGES_TYPE[package_type - 1]
        except IndexError:
            return error_message_1

        try:
            package = PackageInfo(package_name=package_name, 
                                  package_type=parsed_args.type, 
                                  package_description = parsed_args.description,
                                  package_type_name=package_type_name
                                  )
            account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login)
            response = Route.create_package(account, package)
        except BlendedException as exc:
            raise BlendedException(exc)
        if response:        
            print(response)


class PackageList(Command):
    """
    Cammand to get list of Package.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageList, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--account', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        package_name = parsed_args.package_name
        package_id = parsed_args.package_id
        if package_name:
            try:
                #response = controller.package_accounts_list(account_name, package_name=package_name)
                response = "TODO"
            except BlendedException as exc:
                raise BlendedException(exc)
        else:
            try:
                package = PackageInfo(package_name=package_name, 
                                     package_id = parsed_args.package_id
                                     )
                account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login,
                                  account_name=parsed_args.account)
                response = Route.packages_list(account, package)
               
            except BlendedException as exc:
                raise BlendedException(exc)

        if response:        
            print(response)


class GetPackage(Command):
    """
    Adds a package in library of current account.
    Also pass new name for the package by --new_name 
    if the package name already exist in library.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(GetPackage, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--license', nargs='?', default=None)
        parser.add_argument('--new-name', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        package_name = parsed_args.package_name
        package_id = parsed_args.package_id
       
        if not package_name:
            package_name = input("Please Enter Package Name: ")
        if (package_name) and (not package_id):

            try:
                package = PackageInfo(package_name=package_name, 
                                     package_id = parsed_args.package_id,
                                     license_name = parsed_args.license,
                                      new_name = parsed_args.new_name
                                
                                     )
                account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login,
                                  )
                response = Route.get_package_acquisition(account, package)
            except PackageNameExistsException:
                print('Given Package Name Already Exist in Account\n')
                new_name = input('Please Enter a new-name for package:')
                package_name = new_name 
                try:
                    package = PackageInfo(package_name=package_name, 
                                          package_id = parsed_args.package_id,
                                          license_name = parsed_args.license,
                                          new_name = parsed_args.new_name
                                           )
                    account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login,
                                 )
                    response = Route.get_package_acquisition(account, package)
                except BlendedException as ex:
                    raise BlendedException(exc)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"

        if response:
            if(response.package_status!=None) and (response.package_status.lower()=='paid'):
                print('http://cognam.com')       
            print(response)


class ClonePackage(Command):
    """
    Clone a package to the filesystem.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(ClonePackage, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--new-name', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        parser.add_argument('--description', nargs='?', default=None)
        parser.add_argument('--draft', nargs='?', default=False, const=True)
        parser.add_argument('--no-download', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
      
        package_name = parsed_args.package_name
        
        package_id = parsed_args.package_id
        
        label = parsed_args.label
        package_description = parsed_args.description
        draft = parsed_args.draft

        if not package_name:
            package_name = input("Please Enter Package Name: ")

       
        spinner = Spinner()
        if (package_name) and (not package_id):
            spinner.start()
            try:
                package = PackageInfo(package_name=package_name, 
                                      package_id=package_id,
                                      new_name=parsed_args.new_name,
                                      no_download=parsed_args.no_download,
                                      label=parsed_args.label,
                                      package_description=parsed_args.description,
                                      draft=parsed_args.draft
                                      )
                account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login,
                                  )
                response = Route.package_clone(account, package)
            except PackageNameExistsException:
                spinner.stop()
                print('Given Package Name Already Exist in Account\n')
                new_name = input('Please Enter a new-name for package: ')
                package_name = new_name 
                try:
                    spinner.start()
                    package = PackageInfo(package_name=package_name, 
                                      package_id=package_id,
                                      new_name=parsed_args.new_name,
                                      no_download=parsed_args.no_download,
                                      label=parsed_args.label,
                                      package_description=parsed_args.description,
                                      draft=parsed_args.draft
                                      )
                    account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login,
                                  )
                    response = Route.package_clone(account, package)
                except BlendedException as e:
                    spinner.stop()
                    raise BlendedException(e)
            except BlendedException as exc:
                spinner.stop()
                raise BlendedException(exc)
            spinner.stop()
        elif package_id:
            response = "TODO"
        cloned_package_name = response.slug
        message = "Package %s is Cloned as %s Successfully" % (package_name, cloned_package_name)
        if not no_download:
            print("Downloading the cloned package...")
            spinner.start()
            if draft:
                try:
                    controller.pull_package(cloned_package_name, draft=draft,
                                            label=label, force=True,
                                            current_account=current_account)
                except BlendedException as exc:
                    spinner.stop()
                    raise BlendedException(exc)
            else:
                try:
                    controller.pull_package(cloned_package_name, draft=draft,
                                            label=label, force=True,
                                            current_account=current_account)
                except BlendedException as exc:
                    spinner.stop()
                    raise BlendedException(exc)
            spinner.stop()
            backend.set_src
            message = "Package %s is Cloned as %s and downloaded successfully" % (package_name, cloned_package_name)

        print(message)


class PackageExtend(Command):
    """
    Save a package to the Hub.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageExtend, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--new-name', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        parser.add_argument('--description', nargs='?', default=None)
        parser.add_argument('--draft', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
        #import pdb ;pdb.set_trace()
        package_name = parsed_args.package_name
        new_name=parsed_args.new_name
        package_id = parsed_args.package_id
        if not package_name:
            package_name = input("Please Enter Package Name: ")
        if not new_name:
            new_name = input("Please Enter New Package Name for the extended package: ")
  
        if (package_name) and (not package_id):
            try:
                package = PackageInfo(package_name=package_name, 
                                      package_id=package_id,
                                      new_name=new_name,
                                      label=parsed_args.label,
                                      package_description=parsed_args.description,
                                      draft=parsed_args.draft
                                      )
                account = AccountInfo(blended_dir=get_blended_directory_path(),  
                                  password=parsed_args.password, 
                                  username=parsed_args.login,
                                  )
                response = Route.package_extend(account, package)
                
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"

        if response:
            print("Package %s is Extended Successfully as %s" % (package_name, new_name))


class PackageSave(Command):
    """
    Save a package to the Hub.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageSave, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--force', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        force = parsed_args.force
        network = Network()
        network, user_slug = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_slug)
        current_dir = os.path.join(blended_dir, current_account)
        if not package_name:
            try:
                relative_package_path = read_package_name_from_directory(current_account=current_account,
                                                                         current_dir=current_dir,
                                                                         blended_dir=blended_dir)
                package_name = relative_package_path[1].replace(os.sep, "/")
            except AssertionError:
                package_name = input("Please Enter Package Name: ")

        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)
        if (package_name) and (not package_id):
            try:
                print("Uploading Package...")
                
                response = controller.push_package(package_name, force=force, user_slug=user_slug)
                import pdb;pdb.set_trace()
                if len(response)==3:
                     key = list(response[2].copy().keys())[0]
                     value = list(response[0].copy().values())[0]
                     if key == 'force':
                         controller.save_hub(current_account, package_slug, package, force=force)
                         print("force push")
                     elif key == 'flag':
                         print("flag")                   
                else:
                    pass
                      
                
                print("Upload Complete!!")
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"

        if response:
            print("Package %s is successfully uploaded" % (package_name))


class DownloadPackage(Command):
    """
    Download a package to the filesystem.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(DownloadPackage, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        #parser.add_argument('--label', nargs='?', default=None)
        parser.add_argument('--draft', nargs='?', default=False, const=True)
        parser.add_argument('--update', nargs='?', default=None)
        parser.add_argument('--force', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
        package_name = parsed_args.package_name
        package_id = parsed_args.package_id
        update = parsed_args.update    
        if update:
            print("TODO")
            sys.exit(0)
        if (package_name) and (not package_id):
            print("Downloading Package...")
            spinner = Spinner()
            spinner.start()
            try:
                package = PackageInfo(
                    package_name=package_name,
                    package_id=package_id,
                    label=None,
                    draft=parsed_args.draft,
                    update=parsed_args.update,
                    force=parsed_args.force
                    )
                account = AccountInfo(blended_dir=get_blended_directory_path(),  password=parsed_args.password, username=parsed_args.login)
                response = Route.pull_package(account, package)
            except BlendedException as exc:
                spinner.stop()
                raise BlendedException(exc)
            spinner.stop()
            print("%s is Downloaded!!" % (package_name))
        elif package_id:
            response = "TODO"
        if response:        
            print(response)


class InstallPackage(Command):
    """
    Install Package in lib Directory
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(InstallPackage, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        package_name = parsed_args.package_name
        package_id = parsed_args.package_id
        if not package_name:
            package_name = input("Please Enter Package Name: ")
        if package_name:
            length = len(package_name.rsplit("/"))
            if length != 2:
                return "Please enter fully qualified name of the package"
        if (package_name) and (not package_id):
            print("Installing Package...")
            spinner = Spinner()
            spinner.start()
            try:
                package = PackageInfo(package_name=package_name, package_id=package_id, label=parsed_args.label)
                account = AccountInfo(blended_dir=get_blended_directory_path(),  password=parsed_args.password, username=parsed_args.login)
                response = Route.install_package(account, package)
            except BlendedException as exc:
                raise BlendedException(exc)
            spinner.stop()
            print("%s is Installed!!" % (package_name))
        elif package_id:
            response = "TODO"

        if response:
            print(response)


class PackageUpdate(Command):
    """
    Update a package to the Hub.
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageUpdate, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--force', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        force = parsed_args.force
        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        
        package_name, package_id = check_package_credentials(package_name, package_id)

        if package_name:
            #try:
             #   package_id = controller.read_package_pk(package_name)
            #except BlendedException:
             #   response = controller.packages_list()
             #   package_id = controller.read_package_pk(package_name)
            #try:
             #   response = controller.update_package(package_name, package_id=package_id, draft=draft)
            #except BlendedException as exc:
             #   raise BlendedException(exc)
            pass
        else:
            #try:
             #   response = controller.update_package(package_name, package_id=package_id, draft=draft)
            #except BlendedException as exc:
             #   raise BlendedException(exc)
            pass
        response = None
        if response:        
            print(response)


class PackageCompare(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageCompare, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        parser.add_argument('--files', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        label = parsed_args.label
        files = parsed_args.files

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        #package_name, package_id = check_package_credentials(package_name, package_id)
        '''
        if (package_name) and (not package_id):
            try:
                hub_package = network.download_draft(package_name)
            except BlendedException as exc:
                raise BlendedException(exc)

            local_package, package_hash_current = controller.get_package(package_name, 'as_hash', version=label)
            last_hash = backend.get_hash(package_name)
            try:
                response = controller.compare_package(hub_package, local_package,
                                                      'push',
                                                      package_last_hash=last_hash,
                                                      package_current_hash=package_hash_current)
            except BlendedException as exc:
                raise BlendedException(exc)
        else:
            response = "TO DO"
        '''
        if local_package_hash == package_hash:
            print("Package Hash Matched")


class PackageValidate(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageValidate, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        label = parsed_args.label
        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        #if os.path.isfile(os.path.join(current_dir, blended_rc_file)):
        #    backend, package_name = backend_initializer(current_dir)
        #else:
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if package_name:
            """
            try:
                package_id = controller.read_package_pk(package_name)
            except BlendedException:
                response = controller.packages_list()
                package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_validate(package_id, label=label)
            except BlendedException as exc:
                raise BlendedException(exc)
            """
            pass
        else:
            """
            try:
                response = controller.package_validate(int(package_id), label=label)
            except BlendedException as exc:
                raise BlendedException(exc)
            """
            pass
        #if response:        
         #   print(response)


class PackageSnapshot(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageSnapshot, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        label = parsed_args.label

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        if not label:
            label = input("Please Enter the version label of the package: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if (package_name) and (not package_id):
            #try:
             #   package_id = controller.read_package_pk(package_name)
            #except BlendedException:
             #   response = controller.packages_list()
             #   package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_snapshot(current_account, package_name, label=label)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"
        #else:
         #   try:
         #       response = controller.package_snapshot(package_id, label=label)
         #   except BlendedException as exc:
         #       raise BlendedException(exc)
            
        if response:        
            print(response)


class PackageCanonical(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageCanonical, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        label = parsed_args.label

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        #if os.path.isfile(os.path.join(current_dir, blended_rc_file)):
        #    backend, package_name = backend_initializer(current_dir)
        #else:
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if (package_name) and (not package_id):
            #try:
            #    package_id = controller.read_package_pk(package_name)
            #except BlendedException:
            #    response = controller.packages_list()
            #    package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_canonical(current_account, package_name, label=label)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"
        #else:
         #   try:
         #       response = controller.package_canonical(package_id, label=label)
         #   except BlendedException as exc:
         #       raise BlendedException(exc)
            
        if response:        
            print(response)


def all_license(licenses):
    """
    """
    show_licenses(licenses)
                
    license_name = input("Please Enter A License name from the above: ")
    try:
        license_price = licenses[license_name]
    except KeyError:
        license_name, license_price = all_license(licenses)
    
    return license_name, license_price
    

class PackagePublish(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackagePublish, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        parser.add_argument('--license', nargs='?', default=None)
        parser.add_argument('--price', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        label = parsed_args.label
        license_name = parsed_args.license
        license_price = parsed_args.price

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        #if os.path.isfile(os.path.join(current_dir, blended_rc_file)):
        #    backend, package_name = backend_initializer(current_dir)
        #else:
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)
        
        if not license_name:
            if license_price:
                #try:
                 #   response = controller.get_all_licenses()
                #except BlendedException as exc:
                 #   raise BlendedException(exc)
                response = {
                            "href": "http://54.236.218.137:8000/v0/licenses/",
                            "items": [
                                        {
                                        "href": "http://54.236.218.137:8000/v0/licenses/MIT/",
                                        "name": "MIT",
                                        "price": "0.00"
                                        },
                                        {
                                        "href": "http://54.236.218.137:8000/v0/licenses/CGM/",
                                        "name": "CGM",
                                        "price": "1000.00"
                                        },
                                        {
                                        "href": "http://54.236.218.137:8000/v0/licenses/GPL/",
                                        "name": "GPL",
                                        "price": "10.00"
                                        },
                                        {
                                        "href": "http://54.236.218.137:8000/v0/licenses/BSD/",
                                        "name": "BSD",
                                        "price": "100.00"
                                        }
                                    ]   
                            }
                licenses = {}
                all_licenses = response.get('items')
                for license in all_licenses:
                    licenses.update({license.get('name'): license.get('price')})
                
                
                license_detail = all_license(licenses)
                license_name = license_detail[0]
            else:
                license_name = 'MIT'
                license_price = 0

        if (package_name) and (not package_id):
            #try:
            #    package_id = controller.read_package_pk(package_name)
            #except BlendedException:
            #    response = controller.packages_list()
            #    package_id = controller.read_package_pk(package_name)
            try:
                controller.package_addlicense(current_account, package_name, license_name, license_price, label)
                response = controller.package_publish(current_account, package_name, label=label)
            except BlendedException as exc:
                raise BlendedException(exc)

        elif package_id:
            response = "TODO"
        #else:
        #    try:
        #        package_id = int(package_id)
        #        controller.package_addlicense(package_id, license_name, license_price)
        #        response = controller.package_publish(package_id, label=label)
        #    except BlendedException as exc:
        #        raise BlendedException(exc)
        if response:        
            print(response)


class PackageRetract(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageRetract, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--label', nargs='?', default=None)
        parser.add_argument('--license', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        label = parsed_args.label
        license_name = parsed_args.license

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        #if os.path.isfile(os.path.join(current_dir, blended_rc_file)):
        #    backend, package_name = backend_initializer(current_dir)
        #else:
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if (package_name) and (not package_id):
            try:
                package_id = controller.read_package_pk(package_name)
            except BlendedException:
                response = controller.packages_list()
                package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_deletelicense(package_id, license_name)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"
        if response:        
            print(response)


class PackageShare(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageShare, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--with', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        #import pdb;pdb.set_trace()
        account_name = getattr(parsed_args, 'with', None)

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        if not account_name:
            account_name = input("Please enter name of the account you want to share this package with: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)


        if (package_name) and (not package_id):
            #try:
            #    package_id = controller.read_package_pk(package_name)
            #except BlendedException:
            #    response = controller.packages_list()
            #    package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_share(current_account, package_name, account_name=account_name)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"
        #else:
        #    try:
        #        response = controller.package_share(package_id, account_name=account_name)
        #    except BlendedException as exc:
        #        raise BlendedException(exc)
        if response:        
            print("Package %s is shared with %s" % (package_name, account_name))


class PackageTransfer(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageTransfer, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--to', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        account_name = parsed_args.to

        if not package_name:
            package_name = input("Please Enter Package Name: ")

        if not account_name:
            account_name = input("Please enter name of the account you want to transfer this package to: ")

        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if (package_name) and (not package_id):
            #try:
            #    package_id = controller.read_package_pk(package_name)
            #except BlendedException:
            #    response = controller.packages_list()
            #    package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_transfer(current_account, package_name, account_name=account_name)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"
        #else:
        #    try:
        #        response = controller.package_transfer(package_id, account_name=account_name)
        #    except BlendedException as exc:
        #        raise BlendedException(exc)
        if response:
            print("Package %s is transferred to %s" % (package_name, account_name))


class PackageRevoke(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageRevoke, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--account', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        account_name = parsed_args.account
        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if package_name:
            #try:
             #   package_id = controller.read_package_pk(package_name)
            #except BlendedException:
             #   response = controller.packages_list()
             #   package_id = controller.read_package_pk(package_name)
            #try:
             #   response = controller.package_revoke(package_name, package_id=package_id, draft=draft)
            #except BlendedException as exc:
             #   raise BlendedException(exc)
            pass
        else:
            #try:
             #   response = controller.package_revoke(package_name, package_id=package_id, draft=draft)
            #except BlendedException as exc:
             #   raise BlendedException(exc)
            pass
        #if response:        
         #   print(response)


class PackagePreview(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackagePreview, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--host', nargs='?', default=None)
        parser.add_argument('--port', nargs='?', type=int, default=None)
        parser.add_argument('--tweak', nargs='?', default=None)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        host = parsed_args.host
        port = parsed_args.port
        tweak_json = parsed_args.tweak
        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        relative_package_path = []
        if not package_name:
            try:
                relative_package_path = read_package_name_from_directory(current_account=current_account,
                                                                         current_dir=current_dir,
                                                                         blended_dir=blended_dir)
            except AssertionError:
                package_name = input("Please Enter Package Name: ")

        get_host, get_port = get_ip_address()

        if not host:
            host = get_host()

        if not port:
            port = get_port()

        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        if relative_package_path:
            lib_or_src, package_name = relative_package_path[0], relative_package_path[1].replace(os.sep, "/")
            path = "/%s" % (lib_or_src)
        else:
            backend.check_lib_or_src(package_name)
            path = backend.directory_path.split(current_dir)[1].replace(os.sep, "/")
        #package_name, package_id = check_package_credentials(package_name, package_id)
        identifiers = package_name.split("/")

        if len(identifiers) > 1:
            account = identifiers[0]
            package_slug = identifiers[1]
        else:
            try:
                account = backend.get_current_account()
            except BlendedException as exc:
                raise BlendedException(exc)
            package_slug = identifiers[0]

        if path.endswith('lib'):
            package_slug = '%s/%s' % (account, package_slug)

        print('''\ncopy and open this URL '%s:%s/preview%s/%s/templates/' in Your browser\n''' %
              (host, port, path, package_slug))
        theme_app.run(host=host, port=port, debug=False, use_reloader=False, extra_files=extra_files)


class PackageAsJson(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageAsJson, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--jptf', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        tweak_json = parsed_args.jptf
        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        #if os.path.isfile(os.path.join(current_dir, blended_rc_file)):
        #    backend, package_name = backend_initializer(current_dir)
        #else:
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if package_name:
            #try:
             #   package_id = controller.read_package_pk(package_name)
            #except BlendedException:
             #   response = controller.packages_list()
             #   package_id = controller.read_package_pk(package_name)
            #try:
             #   response = controller.as_jptf(package_name, package_id=package_id, draft=draft)
            #except BlendedException as exc:
             #   raise BlendedException(exc)
            pass
        else:
            #try:
             #   response = controller.as_jptf(package_name, package_id=package_id, draft=draft)
            #except BlendedException as exc:
             #   raise BlendedException(exc)
            pass
        if response:        
            print(response)


class PackageDetail(Command):
    """
    """
    def get_parser(self, prog_name, **kwargs):
        parser = super(PackageDetail, self).get_parser(prog_name)
        parser.add_argument('package_name', nargs='?', default=None, help="Needed package name")
        parser.add_argument('--login', nargs='?', default=None)
        parser.add_argument('--password', nargs='?', default=None)
        parser.add_argument('--package-id', nargs='?', default=None)
        parser.add_argument('--description', nargs='?', default=False, const=True)
        parser.add_argument('--licenses', nargs='?', default=False, const=True)
        return parser

    def take_action(self, parsed_args):
        blended_dir = get_blended_directory_path()
        package_name = parsed_args.package_name
        password = parsed_args.password
        username = parsed_args.login
        package_id = parsed_args.package_id
        is_description = parsed_args.description
        is_licenses = parsed_args.licenses
        network = Network()
        network, user_pk = manage_session_key(username, password, network)
        current_account = get_current_account(network, user_pk)
        current_dir = os.path.join(blended_dir, current_account)
        backend = FileSystemBackend(
            current_dir, blended_dir=blended_dir,
            current_account=current_account, blended_directory_path=blended_dir)
        controller = Controller(network, backend)
        package_name, package_id = check_package_credentials(package_name, package_id)

        if (package_name) and (not package_id):
            #try:
             #   package_id = controller.read_package_pk(package_name)
            #except BlendedException:
             #   response = controller.packages_list()
             #   package_id = controller.read_package_pk(package_name)
            try:
                response = controller.package_detail(package_name)
            except BlendedException as exc:
                raise BlendedException(exc)
        elif package_id:
            response = "TODO"

        if response:
            try:
                package_description = response.description
                package_licenses = response.licensedetails.get('items')
                licenses = {}
                if package_licenses:
                    for license in package_licenses:
                        licenses.update({license.get('name'): license.get('price')})
                else:
                    licenses = {}
                if not package_description:
                    package_description = ''
                if is_licenses and is_description:
                    print("licenses:\n")
                    show_licenses(licenses)
                    print("\ndescription:\n")
                    print(package_description)
                elif is_licenses and not is_description:
                    print("licenses:\n")
                    show_licenses(licenses)
                elif is_description and not is_licenses:
                    print("description:\n")
                    print(package_description)
                else:
                    print(response)
            except BlendedException as exc:
                print(response)


def show_licenses(licenses):
    """
    """
    for name, price in licenses.items():
        print("     %s  %s" %(name, price))
