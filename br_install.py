#Installation Script for BRIDGES Lab
#-h or --help for assistance

import argparse, subprocess, os, sys
from constants import db_user, db_name, db_password, default_path, apps_dir
from key import gvs_token

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateObject, DuplicateDatabase

#//=========================================
#   Python Version Verification
#//=========================================
if not (sys.version_info.major == 3 and sys.version_info.minor >= 0):
    print("This script requires Python 3.0 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)
#//=========================================

#//=========================================
#   Application Menu
#//=========================================
parser = argparse.ArgumentParser(description="Welcome to the BRIDGES Installation Helper Script")

options = parser.add_mutually_exclusive_group()
parser_vpn = options.add_argument('-v', '--vpn', action='store_true', help='Install OpenVPN and its dependencies')
parser_nsa = options.add_argument('-n','--nsa', action='store_true', help='Install OpenNSA and its dependencies')
parser_gvs = options.add_argument('-g','--gvs', action='store_true', help='Install GVS and its dependencies')
#parser_all = options.add_argument('-a','--all', action='store_true', help='Install All and their dependencies')
parser_update = options.add_argument('-u','--update', action='store_true', help='Update installation helper')

volume = parser.add_mutually_exclusive_group()
#parser_quiet = volume.add_argument('-q','--quiet', action='store_true', help='Quiet usage') 

args = parser.parse_args()

verbose = True
if args.quiet:
    verbose = False

#//=========================================

#//=========================================
def display_security_warn():
    """Displays Warning for insecure default database paramters
        Intended to be displayed upon initial use of tool
    """
    print('**************************************************************************************************************************************************')
    print('\nWarning: It is up to the user to secure the database. Best way to do this is to change the default passwords stored in the constants.py file\n')
    print('**************************************************************************************************************************************************')
#//=========================================

#//=========================================
def update():
    """Performs 'Update' of Script source. Pulls down the latest from git

        Assumptions:
            Working Directory is Lab_Installation
    """
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
def configure_openvpn():
    """Uses the OpenVPN Road Warrior Install (external open source project) to install and setup OpenVPN
    """
    #Hard Code Install
    #print('Installing OpenVPN...\n\nThis may take a minute, Please wait for entire process to complete\n')
    #install(['openvpn', 'easy-rsa'])

    #OpenVPN Road Warrior Install
    #This approach utlizes an opensource OpenVPN install and config shell script from Github
    # repo = 'https://github.com/Nyr/openvpn-install.git'\
    stanout = subprocess.run(['sudo', 'bash', 'openvpn-install.sh'])
    if stanout.stdout is not None and verbose:
        print(stanout.stdout)
    print("Installation Complete!")
    print("\nTo access your OpenVPN server with an OpenVPN client you will now need to sftp to the server and retrieve the .opvn file (stores vpn connection settings)\n\n")
#//=========================================

#//=========================================
def configure_opennsa():
    """OpenNSA installation procedure. Verification of the correct dependencies followed by installation of the source. Calls the setup_opennsa on the users request
    """
    display_security_warn()
    #Clone OpenNSA (From Geant Gitlab)
    print('Installing OpenNSA...\n\nThis may take a minute, Please wait for entire process to complete\n')
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
        setup_opennsa(True)
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
#//=========================================
 
#//=========================================
def configure_gvs():
    """GVS Installation. 

        Assumptions:
            Proper token is specified in teh key.py file
    """
    #TODO: Verify token file is present (otherwise this will fail)
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
#//=========================================

#//=========================================
#   Main Driving Code
#//=========================================
#OpenVPN
if args.vpn:
    configure_openvpn()
#OpenNSA
if args.nsa:
    configure_opennsa()
#GVS
if args.gvs:
    configure_gvs()
#All
if args.all:
    configure_openvpn()
    configure_opennsa()
    configure_gvs()
    print('Installation Successful')
#Update
if args.update:
    update()
#//=========================================