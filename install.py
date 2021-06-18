#Installation Script for BRIDGES Lab
#Prereqg: Git
import argparse, subprocess, os
# Menu 
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
    
# Pip Dependency Helper func
def pip_install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Standard Package Installer 
# **package must be String[]
def install(package):
    stanout = subprocess.run(['sudo', 'apt', 'install', package] )
    if stanout.stdout is not None:
        print(stanout.stdout)

#OpenVPN
if args.vpn:
    print('Installing OpenVPN...\n\nThis may take a minute, Please wait for entire process to complete\n')
    install(['openvpn', 'easy-rsa'])
    print("Installation Complete!")
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

    #Navigate back to Lab Installation dir 
    os.chdir('..')
    os.chdir('Lab_Installation')
    print("Installation Complete!")
    print("\nNote: OpenNSA is its own directory and you must navigate back to the parent directory to find it for futher use\ndir='opennsa'\n\n")
if args.update:
    update()