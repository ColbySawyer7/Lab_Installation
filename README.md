# Lab_Installation
Automated python installed for various necessary BRIDGES infrastructure software. Notably, OpenVPN and OpenNSA. Includes OpenVPN Road Warrior installation script

## Installation
Git provides the simplest way to pull the code to any device (REQ: Linux)

Command:

  git pull https://github.com/ColbySawyer7/Lab_Installation.git
 
## Usage
### General Help

  python3 br_install.py -h
  
OR

  python3 br_install.py --help
  
### Installing OpenVPN
 
  python3 br_install.py -v
  
OR

  python3 br_install.py --vpn
  
### Installting OpenNSA

  python3 br_install.py -n
  
OR

  python3 br_install.py --nsa
  
### Installting GVS

#### Prereq:
  A token must be generated from an authenticated user to access GVS as it is a private. Use the key.py to store the proper access token. 

  python3 br_install.py -g
  
OR

  python3 br_install.py --gvs
