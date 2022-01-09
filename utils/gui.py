import PySimpleGUI as sg
from .toolkit import *

def start_gui():
    sg.theme('light grey')
    BLUE_BUTTON_COLOR = '#FFFFFF on #2196f2'
    GREEN_BUTTON_COLOR ='#FFFFFF on #00c851'
    LIGHT_GRAY_BUTTON_COLOR = f'#212021 on #e0e0e0'
    DARK_GRAY_BUTTON_COLOR = '#e0e0e0 on #212021'

    layout = [[sg.Col([[sg.B('OpenNSA Installation', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('OpenNSA Automatic Configuration', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('OpenVPN Installation and Configuration', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('GTS Installation', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('Update', size=(40,2), button_color=GREEN_BUTTON_COLOR)],
                        [sg.B('Exit', size=(40,2), button_color=LIGHT_GRAY_BUTTON_COLOR)],], element_justification='c', vertical_alignment='c', expand_x=True,expand_y=True)]]

    window = sg.Window('BRIDGES Lab Installation', layout, resizable=True, size=(400,400), icon='assets/bridges.jpg')

    while True:             # Event Loop
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == 'Do Something':
            window['-GIF-'].metadata = 0
        elif event == 'OpenNSA Installation':
            configure_opennsa()
        elif event == '':
            configure_openvpn()
        elif event == '':
            configure_gvs()
        elif event == 'Update':
            update()
