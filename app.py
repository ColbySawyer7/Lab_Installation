from pywebio.output import *
from pywebio.input import *
import time

def start_gui():
    put_markdown('# Welcome to the Lab Installation GUI')
# Table to display status of dependencies
    put_table([
        ['Requirement', 'Status'],
        ['Python 3', 'Compliant'], 
        ['PostGreSQL', 'Unknown']
        ])
    


    
