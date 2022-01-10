import PySimpleGUI as sg
from .toolkit import *
from os import path, times_result

SETTINGS_KEYS_TO_ELEMENT_KEYS = {'apps_dir': '-APPS DIR-', 'db_user': '-DB USER-', 'db_name': '-DB NAME-', 'db_password': '-DB PSWD-', 'default_path': '-PATH-', 'theme': '-THEME-'}
from .constants import SETTINGS_FILE_LOCATION, GREEN_BUTTON_COLOR, DARK_GRAY_BUTTON_COLOR, LIGHT_GRAY_BUTTON_COLOR, BLUE_BUTTON_COLOR, GREEN_CHECK_ICON, WARNING_ICON, RED_X_ICON

settings = sg.UserSettings(SETTINGS_FILE_LOCATION, use_config_file=True, convert_bools_and_none=True)

def dependency_window():
    sg.theme(settings['Main']['theme'])
    status = ''

    selected_icon = WARNING_ICON
    if status == 'comp':
        selected_icon = GREEN_CHECK_ICON
        status_message = "Depedency is in compliance"
    elif status == 'noncomp':
        selected_icon = RED_X_ICON
        status_message = "ERROR: dependency is in NOT compliance; this will prevent the application from running"
    else:
        selected_icon = WARNING_ICON
        status_message = "Unable to determine compliance of dependency at this time"

    layout = [  [sg.Text('Dependencies', font='Any 15')],
                [sg.Text('PostGreSQL 12.0+', font = 'Any 12') ,sg.Button('', image_data=selected_icon, button_color=(sg.theme_background_color(),sg.theme_background_color()), border_width=0)],
                [sg.Text('', key='-STATUS-', font='Any 10')],
                [sg.Button('Exit')]]

    window = sg.Window('Dependency Helper', layout,size=(400,175), keep_on_top=True, finalize=True)

    while True:             # Event Loop
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == '':
            window['-STATUS-'].update(value=status_message)
    
    window.close()

def settings_window():
    sg.theme(settings['Main']['theme'])
    change = False
    status = None

    def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

    layout = [  [sg.Text('Settings', font='Any 15')],
                [TextLabel('Main Apps Directory'), sg.Input(key='-APPS DIR-'), sg.FolderBrowse(target='-APPS DIR-')],
                [sg.Text('OpenNSA', font = 'Any 10')],
                [TextLabel('DB Username'), sg.Input(key='-DB USER-')],
                [TextLabel('DB Name'), sg.Input(key='-DB NAME-')],
                [TextLabel('DB Password'), sg.Input(key='-DB PSWD-')],
                [TextLabel('Path to Schema'),sg.Input(key='-PATH-'), sg.FolderBrowse(target='-PATH-')],
                [sg.Text('Installer', font='Any 10')],
                [TextLabel('Theme'),sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-')],
                [sg.Button('Save'), sg.Button('Exit')]  ]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings['Main'][str(key)])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    while True:
        event, fields = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == 'Save':
            try:
                for key, value in fields.items():
                    for k, v in SETTINGS_KEYS_TO_ELEMENT_KEYS.items():
                        if v == key:
                            settings['Main'].set(k,value)
                            change = True
                status='Saved Successful'
                break
            except Exception as e:
                status='ERROR: Save Failed'
                break

    window.close()
    if status:
        sg.popup(status)

    return change

def start_gui():
    sg.theme(settings['Main']['theme'])

    layout = [[sg.Text('Main Menu', font='Any 15')],
            [sg.Col([[sg.B('OpenNSA Installation', size=(40,2))],
            #[sg.B('OpenNSA Automatic Configuration', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
            [sg.B('OpenVPN Installation and Configuration', size=(40,2))],
            [sg.B('GVS Installation', size=(40,2))],
            [sg.B('Dependency Helper', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
            [sg.B('Update', size=(40,2), button_color=GREEN_BUTTON_COLOR)],
            [sg.B('Settings', size=(40,2), button_color=DARK_GRAY_BUTTON_COLOR)],
            [sg.B('Exit', size=(40,2), button_color=LIGHT_GRAY_BUTTON_COLOR)],], element_justification='c', vertical_alignment='c', expand_x=True,expand_y=True)]]

    window = sg.Window('BRIDGES Lab Installation', layout, resizable=True, size=(400,400), icon='assets/bridges.jpg')

    while True:             # Event Loop
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == 'Dependency Helper':
            dependency_window()
        elif event == 'OpenNSA Installation':
            configure_opennsa()
        elif event == 'OpenVPN Installation and Configuration':
            configure_openvpn()
        elif event == 'GVS Installation':
            configure_gvs()
        elif event == 'Update':
            update()
            sg.popup('Up to date!')
        elif event == 'Settings':
            theme_change = settings_window()
            if theme_change:
                window.close()
                start_gui()

# TESTING HELPER (UNCOMMENT TO TEST GUI ONLY)
#start_gui()