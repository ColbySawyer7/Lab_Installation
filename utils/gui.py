import PySimpleGUI as sg
from toolkit import *
from os import path


#TODO: CHANGE FROM JSON TO INI SETTINGS STORAGE
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'apps_dir': '-APPS DIR-', 'db_user': '-DB USER-', 'db_name': '-DB NAME-', 'db_password': '-DB PSWD-', 'default_path': '-PATH-', 'theme': '-THEME-'}
SETTINGS_FILE_LOCATION = 'utils/config.ini'

settings = sg.UserSettings(SETTINGS_FILE_LOCATION, use_config_file=True, convert_bools_and_none=True)

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
        if event == 'Exit':
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
    BLUE_BUTTON_COLOR = '#FFFFFF on #2196f2'
    GREEN_BUTTON_COLOR ='#FFFFFF on #00c851'
    LIGHT_GRAY_BUTTON_COLOR = f'#212021 on #e0e0e0'
    DARK_GRAY_BUTTON_COLOR = '#e0e0e0 on #212021'

    layout = [[sg.Col([[sg.B('OpenNSA Installation', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        #[sg.B('OpenNSA Automatic Configuration', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('OpenVPN Installation and Configuration', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('GVS Installation', size=(40,2), button_color=BLUE_BUTTON_COLOR)],
                        [sg.B('Update', size=(40,2), button_color=GREEN_BUTTON_COLOR)],
                        [sg.B('Settings', size=(40,2), button_color=DARK_GRAY_BUTTON_COLOR)],
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

start_gui()