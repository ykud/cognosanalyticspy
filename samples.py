import sys
import os.path 
import configparser
import logging
import getopt
import time
from os import path
import getpass
import keyring
from services.cognos_analytics import CognosAnalyticsService

def get_password(config,
                 environment:str,
                 namespace_prefix :str =""):
    """	Check if there's a username defined for this CA environment namespace + user id combination 
        use keyring instead of password value in the config file       
    """
    if config.has_option(environment, f'{namespace_prefix}user'):
        user = config.get(environment, f'{namespace_prefix}user')
        namespace = config.get(environment, f'{namespace_prefix}namespace')
        password = keyring.get_password(f'CA_{environment}_{namespace}',user)
        if password is None:
            keyring.set_password(
                f'CA_{environment}_{namespace}',user, 
                getpass.getpass(
                    prompt=f'Please input password for user {user} for namespace {namespace} in {environment} environment : ')
            )
            password = keyring.get_password(f'CA_{environment}_{namespace}',user)
        config.set(environment,f'{namespace_prefix}password', password)

def main (argv):
    log_file = path.join("log",
                         f'{os.path.basename(__file__)}{time.strftime("%Y%m%d-%H%M%S")}.log')
    environment = ""
    remove_source_members = False
    # getting command line arguments
    try:
        opts,__ = getopt.getopt(argv, "h:e:l:", ["help","environment=","log="])
    except getopt.GetoptError:
        print (main.__doc__)
        sys.exit(2)
    if len(argv) <= 1:
        print (main.__doc__)
        sys.exit(2)
    for opt,arg in opts:
        if opt in ("-h","--help"):
            print (main.__doc__)
            sys.exit(2)
        elif opt in ("-e","--environment"):
            environment = arg   
        elif opt in ("-l","--log"):
            log_file = arg
    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini')
    log_level = config.get('global','loglevel') \
        if config.has_option('global','loglevel') else 'INFO'
    logging.basicConfig(filename=log_file,
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=log_level)
    # adding the console logger as well
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s,%(msecs)d %(levelname)s %(message)s'
                                                  ,'%H:%M:%S'))
    logging.getLogger().addHandler(console_handler)
    logging.info("Trying to login to Cognos Analytics for  %s environment, output log to %s"
                 ,environment, log_file)
    ca_service = CognosAnalyticsService(ca_url=config.get(environment, 'gateway'))
    namespace = config.get(environment, 'namespace')
    get_password(config, environment, namespace_prefix='')
    
    # Login
    ca_service.login(
        namespace=namespace,user=config.get(environment, 'user'),
        password=config.get(environment, 'password'))
    
    # Content methods
    # get list of content items from team folders
    team_folders_items = ca_service.content.get_content_items(content_id='team_folders')
    # pretty print
    logging.info(team_folders_items)
    # show permissions for the first item
    logging.info(ca_service.content.get_content(content_id = team_folders_items[0].id,content_fields_list=['policies']))

    #user methods
    # return all users of the namespace
    user_list = ca_service.users.get_users(identifier=namespace)
    logging.info([usr.defaultName for usr in user_list])

    #group methods
    # all groups under Cognos namespace (without folders)
    cognos_group_list = ca_service.groups.get_child_groups(parent_id='xOg__')
    logging.info([grp.defaultName for grp in cognos_group_list])
    #show members of a group
    group_members = ca_service.groups.get_group_members(group=cognos_group_list[3])
    logging.info([usr.defaultName for usr in group_members.users])
    
    

if __name__ == "__main__":
    main(sys.argv[1:])