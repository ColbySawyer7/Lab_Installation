#Installation Script for BRIDGES Lab
#-h or --help for assistance

from utils.gui import start_gui
from utils.toolkit import *

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
parser_all = options.add_argument('-a','--all', action='store_true', help='Install All and their dependencies')
parser_gui = options.add_argument('-i', '-interface', action='store_true', help='Start the Lab Installation tools GUI')
parser_update = options.add_argument('-u','--update', action='store_true', help='Update installation helper')

volume = parser.add_mutually_exclusive_group()
parser_quiet = volume.add_argument('-q','--quiet', action='store_true', help='Quiet usage') 

args = parser.parse_args()

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
#GUI
if args.gui:
    install('python3-tk')
    start_gui()
#Update
if args.update:
    update()

#//=========================================