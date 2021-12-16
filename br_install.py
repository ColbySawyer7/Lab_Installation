#Installation Script for BRIDGES Lab
#Note: OpenNSA is installed in the working dir parent. We dont not yet support specifying dir for OpenNSA
#Prereqg: Git
#-h or --help for assistance
import argparse, subprocess, os, sys, pwd, grp
from constants import db_user, db_name, db_password, default_path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

if not (sys.version_info.major == 3 and sys.version_info.minor >= 0):
    print("This script requires Python 3.0 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

# Menu Build
parser = argparse.ArgumentParser(description="Welcome to the BRIDGES Installation Helper Script")
options = parser.add_mutually_exclusive_group()
parser_vpn = options.add_argument('-v', '--vpn', action='store_true', help='Install OpenVPN and its dependencies')
parser_nsa = options.add_argument('-n','--nsa', action='store_true', help='Install OpenNSA and its dependencies')
parser_update = options.add_argument('-u','--update', action='store_true', help='Update installation helper')
args = parser.parse_args()

#Update Method for Lab Script
def update():
    stanout = subprocess.run(['git', 'pull'])
    if stanout.stdout is not None:
        print(stanout.stdout)
    print("Update Complete!")

def verify_pip():
    # Verify Pip is installed
    pip_cmd = "sudo apt install python3-pip"
    os.system(pip_cmd)

def verify_python3():
    python3_command = ['sudo', 'apt', 'install', 'python3']
    python_remove_command = ['sudo', 'apt', 'purge', 'python']
    python_redirect_command = ['sudo' ,'ln' ,'-s' ,'/usr/bin/python3' ,'/usr/bin/python']
    stanout = subprocess.run(python_remove_command)
    if stanout.stdout is not None:
        print(stanout.stdout)

    stanout = subprocess.run(python3_command)
    if stanout.stdout is not None:
        print(stanout.stdout)

    stanout = subprocess.run(python_redirect_command)
    if stanout.stdout is not None:
        print(stanout.stdout)
  
    print("Python Version Verified")

# Pip Dependency Helper func
# **package must be String
def pip_install():
    command = ["sudo", "pip", "install","-r", "requirements.txt"]
    stanout = subprocess.run(command)
    if stanout.stdout is not None:
        print(stanout.stdout)

# Standard Package Installer 
# **package must be String
def install(package):
    command = ['sudo', 'apt', 'install'] + [package]
    stanout = subprocess.run(command)
    if stanout.stdout is not None:
        print(stanout.stdout)

def setup_opennsa(setup_db=False):

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
                    'alter user '+db_user+' password '+db_password+';'
            ]
            for command in commands:
                try:
                    cursor.execute(command)
                except psycopg2.IntegrityError:
                    conn.rollback()
        conn.commit()
        cursor.close()
        conn.close()
        print('Database created')
        path = default_path
        schema_path = input("Please specify the ENTIRE path to the schema.sql file (leave blank for default path)")
        if os.path.isfile(schema_path):
            if schema_path[-3] == 'sql':
                path = schema_path

        #Connect to new OpenNSA DB and fill from SQL file
        conn = psycopg2.connect(host='localhost', user='opennsa')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("Filling Databse from file: " + path)
        with conn.cursor() as cursor:
            cursor.execute(open(path, "r").read())
            conn.commit()
            cursor.close()
            conn.close()
            print('Database filled from file' + path)

    stanout = subprocess.run(['python', 'setup.py', 'build'])
    if stanout.stdout is not None:
        print(stanout.stdout)

    stanout = subprocess.run(['sudo', 'python', 'setup.py', 'install'])
    if stanout.stdout is not None:
        print(stanout.stdout)

    print("OpenNSA Instance Setup complete")

def generate_ssl_cert():
    command = ['sudo', 'openssl', 'req', '-x509' ,'-nodes', '-days' ,'365', '-newkey','rsa:2048', '-keyout', 'opennsa-selfsigned.key', '-out', 'opennsa-selfsigned.crt']
    stanout = subprocess.run(command)
    if stanout.stdout is not None:
        print(stanout.stdout)
    
    if not os.path.exists('keys'):
            os.makedirs('keys')
    if not os.path.exists('certs'):
        os.makedirs('certs')
    commands = [
        ['sudo','cp','opennsa-selfsigned.key', 'keys/opennsa-selfsigned.key'],
        ['sudo','cp','opennsa-selfsigned.crt', 'certs/opennsa-selfsigned.crt'],
    ]
    for command in commands:
        stanout = subprocess.run(command)
        if stanout.stdout is not None:
            print(stanout.stdout)

#OpenVPN
if args.vpn:
    #Hard Code Install
    #print('Installing OpenVPN...\n\nThis may take a minute, Please wait for entire process to complete\n')
    #install(['openvpn', 'easy-rsa'])

    #OpenVPN Road Warrior Install
    #This approach utlizes an opensource OpenVPN install and config shell script from Github
    # repo = 'https://github.com/Nyr/openvpn-install.git'\
    stanout = subprocess.run(['sudo', 'bash', 'openvpn-install.sh'])
    if stanout.stdout is not None:
        print(stanout.stdout)
    print("Installation Complete!")
    print("\nTo access your OpenVPN server with an OpenVPN client you will now need to sftp to the server and retrieve the .opvn file (stores vpn connection settings)\n\n")
#OpenNSA
if args.nsa:
    #Clone OpenNSA (From Geant Gitlab)
    print('Installing OpenNSA...\n\nThis may take a minute, Please wait for entire process to complete\n')
    repoURL = 'https://gitlab.geant.org/hazlinsky/opennsa3.git'
    os.chdir('..')
    stanout = subprocess.run(['git', 'clone', repoURL])
    if stanout.stdout is not None:
        print(stanout.stdout)

    os.chdir('opennsa3')

    # Install Dependencies
    verify_python3()
    verify_pip()

    print('Installing OpenNSA Dependencies...\n\n')
    install('python3-dev')
    install('libpq-dev')
    #PostGreSQL Install
    install('postgresql')
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
    reply = str(input("\nWould you like to generate a self-singed certification? (y/n)")).lower().strip()
    if reply[0] == 'y':
        generate_ssl_cert()
        
    # Change ownership for certs to Opennsa user only.
    #gid = grp.getgrnam("nogroup").gr_gid
    #uid = pwd.getpwnam("opennsa").pw_uid
    #os.chown('keys', uid, gid)
    print('\n\n**Warning: The .cert and .key files are not R/W protected by one user. It is your responsilbity to secure these files')
    
    reply = str(input('\nWould you like to run an instance of OpenNSA now?' +' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        command = ['twistd', '-yn', 'opennsa.tac']
    else:
        #Navigate back to Lab Installation dir 
        os.chdir('..')
        os.chdir('Lab_Installation')
        
    print("\n\nInstallation Complete!")
    print("\nNote: OpenNSA is its own directory and you must navigate back to the parent directory to find it for futher use\ndir='opennsa3'\n\n")
    print('\n ALERT: It is up to the user to secure the Database after creation. Passwords used for creation are too simple for production')
if args.update:
    update()