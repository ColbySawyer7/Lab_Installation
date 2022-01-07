# Constants File
# Usage: 
#   User can define instance-specific information for the various installation options

#OpenNSA Database Authentication
db_user='opennsa'
db_name='opennsa'
db_password='opennsa'

#Applications Directory path. All of the sources will be installed in this location
#This should adhere to industry standard. Unlikely this will need to be changed
apps_dir='/usr/local'

#Path to opennsa schema file. This file is supplied by OpenNSA source.
#DEFAULT: THIS YOU SHOULDNT HAVE TO CHANGE
default_path='opennsa/datafiles/schema.sql'

