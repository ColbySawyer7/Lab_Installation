import argparse, subprocess, os, sys
import PySimpleGUI as sg

from .constants import GVS_SOURCE_URL, OPENNSA_SOURCE_URL, SETTINGS_FILE_LOCATION, BR_MAIN_LOCATION

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateObject, DuplicateDatabase

from git import Repo

verbose = True
#//=========================================
def reload_settings():
    """Helper function that will load the settings from the config.ini file at time of calling

    Returns:
        [multiple]: [Returns entire settings parameters in following order: db_user, db_name, db_password, default_path, apps_dir, gvs_token]
    """
    #Load settings from file
    settings = sg.UserSettings(SETTINGS_FILE_LOCATION, use_config_file=True, convert_bools_and_none=True)

    #Takes parameters from configuration file. This assumes this file is intact.
    db_user = settings['Main']['db_user']
    db_name = settings['Main']['db_name']
    db_password = settings['Main']['db_password']
    default_path = settings['Main']['default_path']
    apps_dir = settings['Main']['apps_dir']
    gvs_token = settings['Main']['gvs_token']
    postgres_pwd = settings['Main']['postgres_pwd']

    return db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd
#//=========================================

#//=========================================
def validate_gvs_key(gvs_token=None):
    """ Validates the gvs_token provided in the config.ini file.
        Used primarily to alert the user of an error.

    Args:
        gvs_token ([String], optional): [String that represents a GVS token. Redirects validation from saved value to provided value]. Defaults to None.

    Returns:
        [bool]: [False if non compliant. True is compliant]
    """
    if gvs_token is None:
        db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()

    try:
        if gvs_token is not None:
            if len(gvs_token) < 40:
                print('ERROR: provided key is too short')
                return False
            else:
                return True
        else:
            print('ERROR: key file is empty. You MUST fill this out')
            return False
    except Exception as e:
        print('ERROR: ' + str(e))
        return False
#//=========================================

#//=========================================
def validate_postgres():
    """Validates the usability and versioning of postgres

    Returns:
        [bool]: [False if not a compliant or reachable instance of postgres. True if compliant version and reachable by tool]
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()
    #Connect to DB
    try:
        conn = psycopg2.connect(host='localhost', user='postgres', password=str(postgres_pwd))
        version = conn.server_version
        conn.close()
        if version < 120000 and version >= 130000:
            return False
        else:
            return True
    except Exception as e:
        sg.popup_timed('ERROR: Unable to establish connection with postgres locally. Check the given postgres password')
        return False   
#//=========================================

#//=========================================
def update():
    """Performs 'Update' of Script source. Pulls down the latest from git
    """
    #TODO: Sync with GUI to dispay a loading bar
    try:
        Repo(BR_MAIN_LOCATION).remotes.origin.pull()
    except Exception as e:
        print('ERROR: ' + str(e))
        return
    print("Update Complete!")
#//=========================================

#//=========================================
def verify_pip():
    """Verifies the installatin of Python3 package manager
    """
    # Verify Pip is installed
    if verbose:
        pip_cmd = "sudo apt install python3-pip"
    else:
        pip_cmd = "sudo apt -q install python3-pip"
    os.system(pip_cmd)
#//=========================================

#//=========================================
def verify_python3():
    """Verify that the proper Python version is installed and used.
        
        **Depreciated: Newer methodology used to verify proper python versioning
    """
    python3_command = ['sudo', 'apt', 'install', 'python3']
    python_remove_command = ['sudo', 'apt', 'purge', 'python']
    python_redirect_command = ['sudo' ,'ln' ,'-s' ,'/usr/bin/python3' ,'/usr/bin/python']
    stanout = subprocess.run(python_remove_command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)

    stanout = subprocess.run(python3_command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)

    stanout = subprocess.run(python_redirect_command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
  
    print("Python Version Verified")
#//=========================================

#//=========================================
def pip_install():
    """Helper function that stores the default install command for using pip

        Requirements:
            Updated requirements.txt file. Packages not listed will not be included
    """
    requirements_loc = BR_MAIN_LOCATION + '/requirements.txt'
    if verbose:
        command = ["sudo", "python3", "-m", "pip", "install","-r", requirements_loc]
    else:
        command = ["sudo", "python3", "-m", "pip", "install", "-q", "-r" , requirements_loc]

    stanout = subprocess.run(command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
#//=========================================
  
#//=========================================
def install(package):
    """Helper Function that stores the default install command for using the linux package manager

    Args:
        package (String): [package manager recognized name for the package intended to be installed]
    """
    if verbose:
        command = ['sudo', 'apt', 'install'] + [package]
    else:
        command = ['sudo', 'apt', '-q', 'install'] + [package]
    stanout = subprocess.run(command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
#//=========================================

#//=========================================
def setup_opennsa(setup_db=False):
    """OpenNSA Setup procedure. Manages the database setup (optional) and the generation of an SSL certificate

    Args:
        setup_db (bool, optional): [Specifies if the database configuration is to be included in the procedure]. Defaults to False (database untouched).
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()

    source_loc= str(apps_dir) + '/opennsa3'

    if setup_db:
        print("Database configuration starting")

        #Connect to DB
        conn = psycopg2.connect(host='localhost', user='postgres', password=str(postgres_pwd))
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            commands =[
                    'create user '+db_user+';',
                    'create database '+db_name+';',
                    'alter user '+db_user+' password \''+db_password+'\';'
            ]
            for command in commands:
                try:
                    cursor.execute(command)
                except DuplicateObject as e:
                    conn.rollback()
                    print(str(e))
                except DuplicateDatabase as e:
                    conn.rollback()
                    print(str(e))
                else:
                    conn.commit()
        cursor.close()
        conn.close()
        print('Database created')

        path = default_path
        #Connect to new OpenNSA DB and fill from SQL file
        conn = psycopg2.connect(host='localhost', user=db_name, password=db_password)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Verify PostGreSQL is 12.0.0+
        if conn.server_version < 120000:
            print("ERROR: You are using an outdated version of Postgres (Postgres 12+ is required)")

        print("Filling Databse from file: " + path)
        with conn.cursor() as cursor:
            cursor.execute(open(path, "r").read())
            conn.commit()
            cursor.close()
            conn.close()
            print('Database filled from file' + path)

    setup_file_loc = source_loc + '/setup.py'
    stanout = subprocess.run(['sudo', 'python3', setup_file_loc , 'build'])
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)

    stanout = subprocess.run(['sudo', 'python3', setup_file_loc , 'install'])
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)

    #print("OpenNSA Instance Setup complete")
#//=========================================

#TODO: See if parameterized calling of script is available (could incorporate into GUI)
#//=========================================
def generate_ssl_cert():
    """Generates a basic SSL certificate. 

        Requirements:
            OpenSSL must be installed prior (This should be standard to intended Ubuntu environments)
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()
    source_loc= str(apps_dir) + '/opennsa3'

    sg.popup_timed('NOTICE: This installer utilizes an external tool. Please return to the terminal interface to complete its steps', auto_close_duration=60, keep_on_top=True)
    command = ['sudo', 'openssl', 'req', '-x509' ,'-nodes', '-days' ,'365', '-newkey','rsa:2048', '-keyout', 'opennsa-selfsigned.key', '-out', 'opennsa-selfsigned.crt']
    stanout = subprocess.run(command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
    
    key_dir_dest = source_loc + '/keys'
    crt_dir_dest = source_loc + '/certs'
    
    if not os.path.exists(key_dir_dest):
        os.makedirs(key_dir_dest)
    if not os.path.exists(crt_dir_dest):
        os.makedirs(crt_dir_dest)

    keys_file_loc = BR_MAIN_LOCATION + '/opennsa-selfsigned.key'
    crt_file_loc = BR_MAIN_LOCATION + '/opennsa-selfsigned.crt'

    keys_file_dest = str(source_loc) + 'keys/opennsa-selfsigned.key'
    crt_file_dest = str(source_loc) + 'certs/opennsa-selfsigned.crt'

    commands = [
        ['sudo','cp', keys_file_loc, keys_file_dest],
        ['sudo','cp', crt_file_loc, crt_file_dest],
        ['sudo','rm','-r', keys_file_loc],
        ['sudo','rm','-r', crt_file_loc],
    ]
    for command in commands:
        stanout = subprocess.run(command)
        if stanout.stdout is not None and verbose:
            print(stanout.stdout)
#//=========================================

#TODO: See if parameterized calling of script is available (could incorporate into GUI)
#//=========================================
def configure_openvpn(gui_enabled=False):
    """Uses the OpenVPN Road Warrior Install (external open source project) to install and setup OpenVPN
    Args:
        gui_enabled (bool, optional): [Set true is GUI is being used]. Defaults to False.
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()

    #Hard Code Install
    #print('Installing OpenVPN...\n\nThis may take a minute, Please wait for entire process to complete\n')
    #install(['openvpn', 'easy-rsa'])

    #OpenVPN Road Warrior Install
    #This approach utlizes an opensource OpenVPN install and config shell script from Github
    # repo = 'https://github.com/Nyr/openvpn-install.git'\
    if gui_enabled:
        sg.popup_timed('NOTICE: This installer utilizes an external tool. Please return to the terminal interface to complete its steps', auto_close_duration=60, keep_on_top=True)
        try: 
            stanout = subprocess.run(['sudo', 'bash', 'utils/openvpn-install.sh'])
            if stanout.stdout is not None and verbose:
                print(stanout.stdout) 
            sg.popup("To access your OpenVPN server with an OpenVPN client you will now need to sftp to the server and retrieve the .ovpn file (stores vpn connection settings)", title='OVPN Successful', keep_on_top=True)
        except Exception as e:
            sg.popup('ERROR:\t' + str(e))
    else:
        try: 
            stanout = subprocess.run(['sudo', 'bash', '/utils/openvpn-install.sh'])
            if stanout.stdout is not None and verbose:
                print(stanout.stdout)
            print("Installation Complete!")
            print("\nTo access your OpenVPN server with an OpenVPN client you will now need to sftp to the server and retrieve the .ovpn file (stores vpn connection settings)\n\n")
        except Exception as e:
            print('ERROR:\t' + str(e))
#//=========================================

#//=========================================
def install_opennsa(gui_enabled=False):
    """OpenNSA installation procedure. Verification of the correct dependencies followed by installation of the source. Calls the setup_opennsa on the users request
    Args:
        gui_enabled (bool, optional): [Set true is GUI is being used]. Defaults to False.
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()
    repoURL = OPENNSA_SOURCE_URL
    source_loc= str(apps_dir) + '/opennsa3'
        
    if gui_enabled:
        # This is the normal print that comes with simple GUI
        sg.Print('Re-routing the stdout', do_not_reroute_stdout=False, )

        sg.Print('****************************************************************************')
        sg.Print('WARNING: It is up to the user to secure the database. Best way to do this is to change the default password stored in the settings.')
        sg.Print('****************************************************************************\n\n')

        #Clone OpenNSA (From Geant Gitlab)
        sg.Print('\n\n***************************************************************************')
        sg.Print('Installing OpenNSA...')
        sg.Print('This may take a minute, Please wait for entire process to complete')
        sg.Print('****************************************************************************\n\n')



        try:
            if not os.path.isdir(source_loc):
                Repo.clone_from(repoURL,apps_dir)

            # Install Dependencies
            #verify_python3()
            verify_pip()

            sg.Print('****************************************************************************')
            sg.Print('Installing OpenNSA Dependencies...')
            sg.Print('****************************************************************************\n\n')

            install('python3-dev')
            install('libpq-dev')

            #Pip dependencies Install
            pip_install()
            install('python3-bcrypt')

            # OpenNSA Configuration
            sg.Print('****************************************************************************')
            sg.Print("OpenNSA Configuration Starting ...")
            sg.Print('****************************************************************************\n\n')


            reply = sg.popup_yes_no('Would you like for the database to be configured at this time? (y/n): ')
            if reply[0] == 'Y':
                setup_opennsa(setup_db=True)
            else:
                setup_opennsa()
            mess = "Would you like for the database to be configured at this time? (y/n): " + str(reply)
            sg.Print('****************************************************************************')
            sg.Print(mess)

            # Certification Creation 
            reply = sg.popup_yes_no("Would you like to generate a self-signed certification? (y/n): ")
            if reply[0] == 'Y':
                generate_ssl_cert()
            mess = "Would you like to generate a self-signed certification? (y/n): " + str(reply)
            sg.Print(mess)
            sg.Print('****************************************************************************\n\n')

            sg.Print('****************************************************************************')
            sg.Print('**Warning: The .cert and .key files are not R/W protected by one user. It is your responsilbity to secure these files')
            sg.Print('****************************************************************************\n\n')

            sg.popup_timed("OpenNSA Installation Complete!", auto_close_duration=60)
            sg.Print('****************************************************************************')
            sg.Print('Source Code Location:' + source_loc, font='bold')
            sg.Print('****************************************************************************\n\n')

        except Exception as e:
            sg.Print('****************************************************************************')
            sg.Print('ERROR:\t' + str(e))
            sg.Print('****************************************************************************\n\n')
    else:
        print('****************************************************************************')
        print('\nWARNING: It is up to the user to secure the database. Best way to do this is to change the default password stored in the config.ini.')
        print('****************************************************************************\n\n')

        #Clone OpenNSA (From Geant Gitlab)
        print('\n\n***************************************************************************')
        print('Installing OpenNSA... This may take a minute, Please wait for entire process to complete')
        print('****************************************************************************\n\n')

        try:
            if not os.path.isdir(source_loc):
                Repo.clone_from(repoURL,apps_dir)

            # Install Dependencies
            #verify_python3()
            verify_pip()

            print('****************************************************************************')
            print('Installing OpenNSA Dependencies...')
            print('****************************************************************************\n\n')

            install('python3-dev')
            install('libpq-dev')

            #Pip dependencies Install
            pip_install()
            install('python3-bcrypt')

            # OpenNSA Configuration
            print('****************************************************************************')
            print("OpenNSA Configuration Starting ...")
            print('****************************************************************************\n\n')

            reply = str(input('\nWould you like for the database to be configured at this time?' +' (y/n): ')).lower().strip()
            if reply[0] == 'y':
                setup_opennsa(setup_db=True)
            else:
                setup_opennsa()

            # Certification Creation 
            reply = str(input("\nWould you like to generate a self-signed certification? (y/n): ")).lower().strip()
            if reply[0] == 'y':
                generate_ssl_cert()
                
            print('****************************************************************************')
            print('**Warning: The .cert and .key files are not R/W protected by one user. It is your responsilbity to secure these files')
            print('****************************************************************************\n\n')
            
            reply = str(input('\nWould you like to run an instance of OpenNSA now?' +' (y/n): ')).lower().strip()
            tac_loc = source_loc + '/datafiles/opennsa.tac'
            if reply[0] == 'y':
                stanout = subprocess.run(['twistd', '-yn', tac_loc])
                if stanout.stdout is not None and verbose:
                    print(stanout.stdout)
            print('****************************************************************************')
            print("Installation Complete!")
            print('Source Code Location:' + source_loc)
            print('****************************************************************************\n\n')
        except Exception as e:
            print('****************************************************************************')
            print('ERROR:\t' + str(e))
            print('****************************************************************************\n\n')
#//=========================================
 
#//=========================================
def install_gvs(gui_enabled=False):
    """GVS Installation. 

        Assumptions:
            Proper token is specified in teh key.py file
    Args:
        gui_enabled (bool, optional): [Set true is GUI is being used]. Defaults to False.
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token, postgres_pwd = reload_settings()

    source_loc = str(apps_dir) + '/GVS'
    username = 'ColbySawyer7'
    remote = f"https://{username}:{str(gvs_token)}" + GVS_SOURCE_URL

    if gui_enabled:
        # This is the normal print that comes with simple GUI
        sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)

        try:
            if not validate_gvs_key():
                sg.Print('ERROR: Unable to validate key.py file')
                return
                #Exception('ERROR: GVS Key file requires attention')

            isString = isinstance(gvs_token,str)
            if gvs_token is not None and isString:
                sg.Print('Installing GVS...\n\nThis may take a minute, Please wait for entire process to complete\n')
                try:
                    if not os.path.isdir(str(apps_dir) + '/GVS'):
                        Repo.clone_from(remote,to_path=apps_dir)
                except Exception as e:
                    sg.popup_timed('ERROR: GVS source could not be pulled', auto_close_duration=60)
                    print('ERROR: GVS source could not be pulled')
                    return
                sg.popup_timed("Installation Complete!", auto_close_duration=60)
                sg.Print('Source Code Location:' + source_loc)                    
            elif not isString:
                sg.Print('ERROR (Improper Key): Please verify you have the proper key/token in the keys.py file AND is a String')
                print('ERROR (Improper Key): Please verify you have the proper key/token in the keys.py file AND is a String')
            else:
                sg.Print('ERROR (Private Repo Access Denied): You have not added the proper key/token in the settings')
                print('ERROR (Private Repo Access Denied): You have not added the proper key/token in the settings')
        except Exception as e:
            sg.Print('ERROR:\t' + str(e))
    else:
        try:
            if not validate_gvs_key():
                print('ERROR: Unable to validate key.py file')
                return

            isString = isinstance(gvs_token,str)
            if gvs_token is not None and isString:
                print('Installing GVS...\n\nThis may take a minute, Please wait for entire process to complete\n')
                if os.path.isdir(source_loc):
                    Repo(source_loc).remotes.origin.pull()
                else:
                    if not os.path.isdir(str(apps_dir) + '/GVS'):
                        Repo.clone_from(remote,apps_dir)
                
                print("\n\nInstallation Complete!")
                print('Source Code Location:' + source_loc)
            elif not isString:
                print('ERROR (Improper Key): Please verify you have the proper key/token in the keys.py file AND is a String')
            else:
                print('ERROR (Private Repo Access Denied): You have not added the proper key/token to the config.ini file')
        except Exception as e:
            print('ERROR:\t' + str(e))
#//=========================================
