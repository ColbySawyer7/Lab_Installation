# Lab_Installation
![Project: BRIDGES ](https://img.shields.io/badge/Project-BRIDGES-blueviolet)
![Language: Python3](https://img.shields.io/badge/language-Python3-blue)

## Updating the constants for your instance
#### Complete the Following:
 - Find the config.ini file (located in the utils dir)
 - Open this file
 - Make appropriate changes (ONLY CHANGE VALUES)
 - Appropriately save file
 - Restart Application
  
More Information on the current parameters available in the configuration file:
| Parameter     | Usage     | Default Value        |   More information | 
|---------------|-----------|----------------------|--------------------|
|[Main]|Section header|N/A|(DO NOT REMOVE THIS) | 
|db_user| Specifies the database username to be used for the PostGreSQL database) Primarily for the OpenNSA required database |opennsa | 
|db_name| Specifies the database name to be used for the PostGreSQL database) Primarily for the OpenNSA required database|opennsa | 
|db_password| Specifies the database password to be used for the PostGreSQL database) Primarily for the OpenNSA required database| opennsa | SECURITY WARNING**
|default_path| The path to the OpenNSA database schema file| opennsa/datafiles/schema.sql | This shouldnt change, OpenNSA manages this file |
|apps_dir| The path where all the application sources will be installed | /usr/local | 
|theme| GUI specific parameter, it is recommended you only change this in the GUI settings|Python | 