#Installation Script for BRIDGES Lab
#Note: OpenNSA is installed in the working dir parent. We dont not yet support specifying dir for OpenNSA
#Prereqg: Git
#-h or --help for assistance
import argparse, subprocess, os, sys
if not (sys.version_info.major == 3 and sys.version_info.minor >= 7):
    print("This script requires Python 3.7 or higher!")
    print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
    ans = input("Would you like to install Python3.7? (y/n)")
    if ans == 'y' or ans == 'yes':
        os.system("sudo apt install python3.7")
        print("Python3.7 Installed -- Retry with command: python3.7 br_install.py [-h |-o |-n |-u]")
        sys.exit(1)
    else:
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
    pip_cmd = "sudo apt install python-pip"
    os.system(pip_cmd)

# Pip Dependency Helper func
def pip_install(package):
    command = ["sudo", "pip", "install"] + package
    stanout = subprocess.run(command)
    if stanout.stdout is not None:
        print(stanout.stdout)

# Standard Package Installer 
# **package must be String[]
def install(package):
    command = ['sudo', 'apt', 'install'] + package
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
    print('Installing OpenNSA...\n\nThis may take a minute, Please wait for entire process to complete\n')
    repoURL = 'https://github.com/NORDUnet/opennsa.git'
    os.chdir('..')
    stanout = subprocess.run(['git', 'clone', repoURL])
    if stanout.stdout is not None:
        print(stanout.stdout)
    os.chdir('opennsa')
    # Install Dependencies  
    verify_pip() 
    print('Installing OpenNSA Dependencies...\n\n')
    #Twisted Install
    pip_install('twisted[tls]')
    #Psycopg Install
    install(['python3-dev', 'libpq-dev'])
    pip_install('psycopg2')
    #Twistar Install
    pip_install('twistar')
    #PostGreSQL Install
    install(['postgresql'])
    #pyOPenSSL Install
    pip_install('pyOpenSSL')
    # OpenNSA Configuration
    #stanout = subprocess.run('python', 'setup.py', 'build')
    #if stanout.stdout is not None:
    #    print(stanout.stdout)
    #stanout = subprocess.run('sudo', 'python', 'setup.py', 'install')
    #if stanout.stdout is not None:
    #    print(stanout.stdout)
    #Creating opennsa DB
    #
    #Navigate back to Lab Installation dir 
    os.chdir('..')
    os.chdir('Lab_Installation')
    print("Installation Complete!")
    print("\nNote: OpenNSA is its own directory and you must navigate back to the parent directory to find it for futher use\ndir='opennsa'\n\n")
if args.update:
    update()