# Lab_Installation
Automated python installed for various necessary BRIDGES infrastructure software. Notably, OpenVPN and OpenNSA. Includes OpenVPN Road Warrior installation script

## Installation
Git provides the simplest way to pull the code to any device (REQ: Linux)

Command:
    git pull https://github.com/ColbySawyer7/Lab_Installation.git
 
## Usage

### Instace Specific Information
To update parameters for your specific instance please refer to the constants.py file. You can make your changes
here prior to configuration to properly secure and personlize the application instances.

### General Help
''''
  python3 br_install.py -h
''''
OR

  python3 br_install.py --help
  
### Installing OpenVPN
 
  python3 br_install.py -v
  
OR

  python3 br_install.py --vpn
  
### Installting OpenNSA

### Prereq:
  To use a more secure database authentication pair make sure to change the values in constants.py

  python3 br_install.py -n
  
OR

  python3 br_install.py --nsa
  
### Installting GVS

#### Prereq:
  A token must be generated from an authenticated user to access GVS as it is a private. Use the key.py to store the proper access token. 

  python3 br_install.py -g
  
OR

  python3 br_install.py --gvs
