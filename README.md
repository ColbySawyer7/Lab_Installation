# Lab_Installation
![Project: BRIDGES ](https://img.shields.io/badge/Project-BRIDGES-blueviolet)
![Language: Python3](https://img.shields.io/badge/language-Python3-blue)

Automated python installed for various necessary BRIDGES infrastructure software. Notably, OpenVPN and OpenNSA. Includes OpenVPN Road Warrior installation script

## Installation
Git provides the simplest way to pull the code to any device (REQ: Linux)

    git pull https://github.com/ColbySawyer7/Lab_Installation.git

It is recommended that you install the Python packages for the script in a virtual environment dedicated to this application. To do so:
- Follow the 'Creating Virtual Environment' steps below
- Once complete,
 
        sudo python3 -m pip install -r [BR-TOOL-LOCATION]/requirements.txt

 
## Usage

### Instance Specific Information
To update parameters for your specific instance please refer to the UPDATE.md (Recommended for security if not using GUI). Please note that the br_install tool will install (w/ elevated privilege) with generic r/w/e permissions on the application folders. This means any user on the same device WILL see the application source. You will have to manually manage these folders permission to change that. [More Information on changing permissions in Ubuntu](https://help.ubuntu.com/community/FilePermissions)

### General Help
    sudo python3 br_install.py --help

  
<details><summary>Using the GUI</summary>
<p>

    sudo python3 br_install.py -i
    OR
    sudo python3 br_install.py --interface

When using the above command a window will appear. 
See example below:

[gui]: gui_example.PNG "gui"

![alt text][gui]

</p>
</details>

<details><summary>Installing OpenVPN</summary>
<p>

    sudo python3 br_install.py -v
    OR
    sudo python3 br_install.py --vpn

</p>
</details>

<details><summary>Installing OpenNSA</summary>
<p>

 Prereq: To use a more secure database authentication pair make sure to change the values detailed in UPDATE.md. 
 
 This tool also assumes that proper conf/nrm files for OpenNSA will be added to the source after the initial installation. There will be future efforts to form a wizard to assist in this configuration process.

    sudo python3 br_install.py -n
    OR
    sudo python3 br_install.py --nsa

</p>
</details>


<details><summary>Installing GVS</summary>
<p>
Prereq: A token must be generated from an authenticated user to access GVS as it is a private. Follow the UPDATE.md for more information. 

    sudo python3 br_install.py -g
    OR
    sudo python3 br_install.py --gvs

</p>
</details>

<details><summary>Creating Virtual Environment (Recommended)</summary>
<p>

#### Install Vituralenv

    python3 -m pip install virtualenv

#### Create Environment 

    virtualenv [Virtual_Environment_Name]

#### Activate Environment

    source virtual_environments/[Virtual_Environment_Name]/bin/activate

#### Install Python Packages for Tools

    sudo python3 -m pip install -r requirements.txt

</p>
</details>
