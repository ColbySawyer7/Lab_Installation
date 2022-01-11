import argparse, subprocess, os, sys
import PySimpleGUI as sg

from .constants import SETTINGS_FILE_LOCATION

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateObject, DuplicateDatabase


verbose = True
#//=========================================
def reload_settings():
    """[summary]

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

    return db_user, db_name, db_password, default_path, apps_dir, gvs_token
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
        db_user, db_name, db_password, default_path, apps_dir, gvs_token = reload_settings()

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
    #TODO: COMPLETE THIS FUNC
    return None
#//=========================================

#//=========================================
def update():
    """Performs 'Update' of Script source. Pulls down the latest from git

        Assumptions:
            Working Directory is Lab_Installation
    """
    #TODO: Sync with GUI to dispay a loading bar
    stanout = subprocess.run(['git', 'pull'])
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
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
    if verbose:
        command = ["sudo", "pip", "install","-r", "requirements.txt"]
    else:
        command = ["sudo", "pip", "install", "-q", "-r", "requirements.txt"]

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
    db_user, db_name, db_password, default_path, apps_dir, gvs_token = reload_settings()

    os.chdir('../opennsa3')

    if setup_db:
        print("Database configuration starting")

        #Connect to DB
        conn = psycopg2.connect(host='localhost', user='postgres', password='postgres')
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

    stanout = subprocess.run(['python', 'setup.py', 'build'])
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)

    stanout = subprocess.run(['sudo', 'python', 'setup.py', 'install'])
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)

    print("OpenNSA Instance Setup complete")
#//=========================================

#//=========================================
def generate_ssl_cert():
    """Generates a basic SSL certificate. 

        Requirements:
            OpenSSL must be installed prior (This should be standard to intended Ubuntu environments)
    """
    command = ['sudo', 'openssl', 'req', '-x509' ,'-nodes', '-days' ,'365', '-newkey','rsa:2048', '-keyout', 'opennsa-selfsigned.key', '-out', 'opennsa-selfsigned.crt']
    stanout = subprocess.run(command)
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
    
    if not os.path.exists('keys'):
            os.makedirs('keys')
    if not os.path.exists('certs'):
        os.makedirs('certs')
    commands = [
        ['sudo','cp','opennsa-selfsigned.key', 'keys/opennsa-selfsigned.key'],
        ['sudo','cp','opennsa-selfsigned.crt', 'certs/opennsa-selfsigned.crt'],
        ['sudo','rm','-r', 'opennsa-selfsigned.key'],
        ['sudo','rm','-r', 'opennsa-selfsigned.crt'],
    ]
    for command in commands:
        stanout = subprocess.run(command)
        if stanout.stdout is not None and verbose:
            print(stanout.stdout)
#//=========================================

#//=========================================
def configure_openvpn(gui_enabled=False):
    """Uses the OpenVPN Road Warrior Install (external open source project) to install and setup OpenVPN
    Args:
        gui_enabled (bool, optional): [Set true is GUI is being used]. Defaults to False.
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token = reload_settings()

    #Hard Code Install
    #print('Installing OpenVPN...\n\nThis may take a minute, Please wait for entire process to complete\n')
    #install(['openvpn', 'easy-rsa'])

    #OpenVPN Road Warrior Install
    #This approach utlizes an opensource OpenVPN install and config shell script from Github
    # repo = 'https://github.com/Nyr/openvpn-install.git'\
    if gui_enabled:
        # This is the normal print that comes with simple GUI
        sg.Print('Re-routing the stdout', do_not_reroute_stdout=False, )
        try: 
            stanout = subprocess.run(['sudo', 'bash', 'utils/openvpn-install.sh'])
            if stanout.stdout is not None and verbose:
                sg.Print(stanout.stdout)
            sg.Print("Installation Complete!")
            sg.Print("\nTo access your OpenVPN server with an OpenVPN client you will now need to sftp to the server and retrieve the .opvn file (stores vpn connection settings)\n\n")
        except Exception as e:
            sg.Print('ERROR:\t' + str(e))
    else:
        try: 
            stanout = subprocess.run(['sudo', 'bash', '/utils/openvpn-install.sh'])
            if stanout.stdout is not None and verbose:
                print(stanout.stdout)
            print("Installation Complete!")
            print("\nTo access your OpenVPN server with an OpenVPN client you will now need to sftp to the server and retrieve the .opvn file (stores vpn connection settings)\n\n")
        except Exception as e:
            print('ERROR:\t' + str(e))
#//=========================================

#//=========================================
def configure_opennsa(gui_enabled=False):
    """OpenNSA installation procedure. Verification of the correct dependencies followed by installation of the source. Calls the setup_opennsa on the users request
    Args:
        gui_enabled (bool, optional): [Set true is GUI is being used]. Defaults to False.
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token = reload_settings()

    if gui_enabled:
        # This is the normal print that comes with simple GUI
        sg.Print('Re-routing the stdout', do_not_reroute_stdout=False, )

        sg.Print('****************************************************************************')
        sg.Print('\nWarning: It is up to the user to secure the database. Best way to do this is to change the default passwords stored in the constants.py file\n')
        sg.Print('****************************************************************************')

        #Clone OpenNSA (From Geant Gitlab)
        sg.Print('\n\n***************************************************************************')
        sg.Print('Installing OpenNSA... This may take a minute, Please wait for entire process to complete\n')
        sg.Print('****************************************************************************')

        try:
            repoURL = 'https://gitlab.geant.org/hazlinsky/opennsa3.git'
            lab_install_dir = os.getcwd()
            source_loc=apps_dir + '/opennsa3'
            os.chdir(apps_dir)
            stanout = subprocess.run(['git', 'clone', repoURL])
            if stanout.stdout is not None and verbose:
                sg.Print(stanout.stdout)

            os.chdir('opennsa3')

            # Install Dependencies
            #verify_python3()
            verify_pip()

            sg.Print('Installing OpenNSA Dependencies...\n')

            install('python3-dev')
            install('libpq-dev')

            #Pip dependencies Install
            pip_install()
            install('python3-bcrypt')

            # OpenNSA Configuration
            sg.Print("\n\nOpenNSA Configuration Starting ...")

            reply = str(input('\nWould you like for the database to be configured at this time?' +' (y/n): ')).lower().strip()
            if reply[0] == 'y':
                setup_opennsa(setup_db=True)
            else:
                setup_opennsa()

            # Certification Creation 
            reply = str(input("\nWould you like to generate a self-signed certification? (y/n): ")).lower().strip()
            if reply[0] == 'y':
                generate_ssl_cert()
                
            # Change ownership for certs to Opennsa user only.
            #gid = grp.getgrnam("nogroup").gr_gid
            #uid = pwd.getpwnam("opennsa").pw_uid
            #os.chown('keys', uid, gid)

            sg.Print('\n\n**Warning: The .cert and .key files are not R/W protected by one user. It is your responsilbity to secure these files')
            
            reply = str(input('\nWould you like to run an instance of OpenNSA now?' +' (y/n): ')).lower().strip()
            tac_loc = source_loc + '/datafiles/opennsa.tac'
            if reply[0] == 'y':
                stanout = subprocess.run(['twistd', '-yn', tac_loc])
                if stanout.stdout is not None and verbose:
                    sg.Print(stanout.stdout)
            else:
                #Navigate back to Lab Installation dir 
                os.chdir(lab_install_dir)
            
            sg.Print("\n\nInstallation Complete!")
            sg.Print('Source Code Location:' + source_loc)
        except Exception as e:
            sg.Print('ERROR:\t' + str(e))
    else:
        print('****************************************************************************')
        print('\nWarning: It is up to the user to secure the database. Best way to do this is to change the default passwords stored in the constants.py file\n')
        print('****************************************************************************')

        #Clone OpenNSA (From Geant Gitlab)
        print('\n\n***************************************************************************')
        print('Installing OpenNSA... This may take a minute, Please wait for entire process to complete\n')
        print('****************************************************************************')

        try:
            repoURL = 'https://gitlab.geant.org/hazlinsky/opennsa3.git'
            lab_install_dir = os.getcwd()
            source_loc=apps_dir + '/opennsa3'
            os.chdir(apps_dir)
            stanout = subprocess.run(['git', 'clone', repoURL])
            if stanout.stdout is not None and verbose:
                print(stanout.stdout)

            os.chdir('opennsa3')

            # Install Dependencies
            #verify_python3()
            verify_pip()

            print('Installing OpenNSA Dependencies...\n')

            install('python3-dev')
            install('libpq-dev')

            #Pip dependencies Install
            pip_install()
            install('python3-bcrypt')

            # OpenNSA Configuration
            print("\n\nOpenNSA Configuration Starting ...")

            reply = str(input('\nWould you like for the database to be configured at this time?' +' (y/n): ')).lower().strip()
            if reply[0] == 'y':
                setup_opennsa(setup_db=True)
            else:
                setup_opennsa()

            # Certification Creation 
            reply = str(input("\nWould you like to generate a self-signed certification? (y/n): ")).lower().strip()
            if reply[0] == 'y':
                generate_ssl_cert()
                
            # Change ownership for certs to Opennsa user only.
            #gid = grp.getgrnam("nogroup").gr_gid
            #uid = pwd.getpwnam("opennsa").pw_uid
            #os.chown('keys', uid, gid)

            print('\n\n**Warning: The .cert and .key files are not R/W protected by one user. It is your responsilbity to secure these files')
            
            reply = str(input('\nWould you like to run an instance of OpenNSA now?' +' (y/n): ')).lower().strip()
            tac_loc = source_loc + '/datafiles/opennsa.tac'
            if reply[0] == 'y':
                stanout = subprocess.run(['twistd', '-yn', tac_loc])
                if stanout.stdout is not None and verbose:
                    print(stanout.stdout)
            else:
                #Navigate back to Lab Installation dir 
                os.chdir(lab_install_dir)
            
            print("\n\nInstallation Complete!")
            print('Source Code Location:' + source_loc)
        except Exception as e:
            print('ERROR:\t' + str(e))
#//=========================================
 
#//=========================================
def configure_gvs(gui_enabled=False):
    """GVS Installation. 

        Assumptions:
            Proper token is specified in teh key.py file
    Args:
        gui_enabled (bool, optional): [Set true is GUI is being used]. Defaults to False.
    """
    db_user, db_name, db_password, default_path, apps_dir, gvs_token = reload_settings()

    if gui_enabled:
        # This is the normal print that comes with simple GUI
        sg.Print('Re-routing the stdout', do_not_reroute_stdout=False, )

        try:
            if not validate_gvs_key():
                sg.Print('ERROR: Unable to validate key.py file')
                return
                #Exception('ERROR: GVS Key file requires attention')

            isString = isinstance(gvs_token,str)
            if gvs_token is not None and isString:
                sg.Print('Installing GVS...\n\nThis may take a minute, Please wait for entire process to complete\n')
                lab_install_dir = os.getcwd()
                source_loc = apps_dir + '/GVS'

                repoURL = '@github.com/jwsobieski/GVS.git'
                repoURL = 'https://ColbySawyer7:' + gvs_token + repoURL

                if os.path.isdir(apps_dir + '/GVS'):
                    sg.Print('GVS Source exists, pulling most recent version now')
                    os.chdir(apps_dir + '/GVS')
                    stanout = subprocess.run(['git', 'pull', repoURL])
                    if stanout.stdout is not None and verbose:
                        sg.Print(stanout.stdout)
                else:
                    os.chdir(apps_dir)
                    stanout = subprocess.run(['git', 'clone', repoURL])
                    if stanout.stdout is not None and verbose:
                        sg.Print(stanout.stdout)

                #Navigate back to Lab Installation dir 
                os.chdir(lab_install_dir)
                
                sg.Print("\n\nInstallation Complete!")
                sg.Print('Source Code Location:' + source_loc)
            elif not isString:
                sg.Print('ERROR (Improper Key): Please verify you have the proper key/token in the keys.py file AND is a String')
            else:
                sg.Print('ERROR (Private Repo Access Denied): You have not added the proper key/token to the keys.py file')
        except Exception as e:
            sg.Print('ERROR:\t' + str(e))
    else:
        try:
            if not validate_gvs_key():
                print('ERROR: Unable to validate key.py file')
                return
                #Exception('ERROR: GVS Key file requires attention')

            isString = isinstance(gvs_token,str)
            if gvs_token is not None and isString:
                print('Installing GVS...\n\nThis may take a minute, Please wait for entire process to complete\n')
                lab_install_dir = os.getcwd()
                source_loc = apps_dir + '/GVS'

                repoURL = '@github.com/jwsobieski/GVS.git'
                repoURL = 'https://ColbySawyer7:' + gvs_token + repoURL

                if os.path.isdir(apps_dir + '/GVS'):
                    print('GVS Source exists, pulling most recent version now')
                    os.chdir(apps_dir + '/GVS')
                    stanout = subprocess.run(['git', 'pull', repoURL])
                    if stanout.stdout is not None and verbose:
                        print(stanout.stdout)
                else:
                    os.chdir(apps_dir)
                    stanout = subprocess.run(['git', 'clone', repoURL])
                    if stanout.stdout is not None and verbose:
                        print(stanout.stdout)

                #Navigate back to Lab Installation dir 
                os.chdir(lab_install_dir)
                
                print("\n\nInstallation Complete!")
                print('Source Code Location:' + source_loc)
            elif not isString:
                print('ERROR (Improper Key): Please verify you have the proper key/token in the keys.py file AND is a String')
            else:
                print('ERROR (Private Repo Access Denied): You have not added the proper key/token to the keys.py file')
        except Exception as e:
            print('ERROR:\t' + str(e))
#//=========================================
