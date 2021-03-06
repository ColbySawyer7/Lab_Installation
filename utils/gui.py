import PySimpleGUI as sg
from .toolkit import *
from os import path

SETTINGS_KEYS_TO_ELEMENT_KEYS = {'apps_dir': '-APPS DIR-', 'postgres_pwd':'-PG PWD-', 'db_user': '-DB USER-', 'db_name': '-DB NAME-', 'db_password': '-DB PSWD-', 'default_path': '-PATH-','gvs_token':'-TOKEN-', 'theme': '-THEME-'}
from .constants import SETTINGS_FILE_LOCATION, GREEN_BUTTON_COLOR, DARK_GRAY_BUTTON_COLOR, LIGHT_GRAY_BUTTON_COLOR, BLUE_BUTTON_COLOR, GREEN_CHECK_ICON, WARNING_ICON, RED_X_ICON, INFO_ICON, BRIDGES_ICON

#Load settings from file
settings = sg.UserSettings(SETTINGS_FILE_LOCATION, use_config_file=True, convert_bools_and_none=True)

#//=========================================
def install_required_python():
    sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
    sg.Print('Installing Python Dependencies')
    pip_install()
    sg.Print('Complete!')
#//=========================================

#//=========================================
def get_depen_status(postgres=False, gvs_token=False, show_popup=False):
    status = None
    instructions = None
    if postgres:
        status = validate_postgres()
        instructions = 'More Information can be found at https://www.postgresql.org/download/linux/ubuntu/'
    elif gvs_token:
        status = validate_gvs_key()
        instructions = 'To correct this issue navigate to the settings menu and verify that the token is correct'

    if status:
        selected_icon = GREEN_CHECK_ICON
        status_message = "Depedency is in compliance"
    elif status is None:
        selected_icon = WARNING_ICON
        status_message = "Unable to determine compliance of dependency at this time"

    elif not status :
        selected_icon = RED_X_ICON
        status_message = "ERROR: dependency is in NOT compliance."
        if show_popup:
            sg.popup(instructions,keep_on_top=True)
    status = [status_message, selected_icon]
    return status
#//=========================================

#//=========================================
def dependency_window():
    """Dependency Checking Menu
    """
    sg.theme(settings['Main']['theme'])

    layout = [  [sg.Text('Dependencies', font='Any 15')],
                [sg.Text('PostGreSQL 12.0+', font = 'Any 12') ,sg.Button('', image_data=get_depen_status(postgres=True)[1], button_color=(sg.theme_background_color(),sg.theme_background_color()), border_width=0)],
                [sg.Text('GVS Key file', font = 'Any 12') ,sg.Button(' ', image_data=get_depen_status(gvs_token=True)[1], button_color=(sg.theme_background_color(),sg.theme_background_color()), border_width=0)],
                [sg.Text('', key='-STATUS-', font='Any 10')],
                [sg.Button('Exit')]
            ]

    window = sg.Window('Dependency Helper', layout,size=(400,225), keep_on_top=True, finalize=True, resizable=True)

    while True:             # Event Loop
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == '':
            window['-STATUS-'].update(value=get_depen_status(postgres=True, show_popup=True)[0])
        elif event == ' ':
            window['-STATUS-'].update(value=get_depen_status(gvs_token=True, show_popup=True)[0])
    
    window.close()
#//=========================================

#//=========================================
def settings_window():
    """Settings menu for the GUI. 
        Allows users to fully manipulate the config.ini file. Returns boolean based on state of changes

    Returns:
        [bool]: [Holds if any settings have been changed (TRUE is settings changed). This is vital to submitting the changes to the main!]
    """
    sg.theme(settings['Main']['theme'])
    change = False
    status = None

    def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

    layout = [
                [sg.Text('Settings', font='Any 15 bold underline')],
                [sg.Col([
                    [TextLabel('Main Apps Directory'), sg.Input(key='-APPS DIR-'), sg.FolderBrowse(target='-APPS DIR-', initial_folder=str(settings['Main'][str('apps_dir')]))],
                    [sg.Text('Postgres', font = 'Any 10 bold underline')],
                    [TextLabel('PostGres Password'), sg.Input(key='-PG PWD-'), sg.Button(image_data=INFO_ICON , tooltip='Password for the postgres user')],
                    [sg.Text('OpenNSA', font = 'Any 10 bold underline')],
                    [TextLabel('DB Username'), sg.Input(key='-DB USER-'), sg.Button(image_data=INFO_ICON , tooltip='Username for the user given control over the OpenNSA database')],
                    [TextLabel('DB Name'), sg.Input(key='-DB NAME-'),sg.Button(image_data=INFO_ICON , tooltip='Name for the OpenNSA database')],
                    [TextLabel('DB Password'), sg.Input(key='-DB PSWD-'),sg.Button(image_data=INFO_ICON , tooltip='Password for the OpenNSA database')],
                    [TextLabel('Path to Schema'),sg.Input(key='-PATH-'), sg.FileBrowse(target='-PATH-', initial_folder=str(settings['Main'][str('default_path')]))],
                    [TextLabel('GVS Token'), sg.Input(key='-TOKEN-'),sg.Button(image_data=INFO_ICON , tooltip='Token used to retrieve the private GFS code (generated by admin) ')],
                    [sg.Text('Installer', font='Any 10 bold underline')],
                    [TextLabel('Theme'),sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-'),sg.Button(image_data=INFO_ICON , tooltip='Theme of the entire GUI')],
                ],element_justification='c', vertical_alignment='c', expand_x=True, expand_y=True)],
                [sg.Button('Save'), sg.Button('Exit')]
            ]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True, resizable=True)

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
#//=========================================

#//=========================================
def start_gui():
    """Main Menu for the GUI, Starts the menu
    """
    sg.theme(settings['Main']['theme'])
    curr_w, curr_h = sg.Window.get_screen_size()
    butt_w = int(curr_w * .025)
    butt_h = int(curr_h * .003)
    nsa_status = is_nsa_installed()

    layout = [[sg.Text('Main Menu', font='Any 15')],
                [sg.Col([
                    [sg.B('OpenNSA Installation',size=(butt_w,butt_h),disabled=nsa_status)],
                    [sg.Button('Run OpenNSA', size=(butt_w,butt_h), disabled=(not nsa_status))],
                    #[sg.B('OpenNSA Automatic Configuration', size=(butt_w,butt_h), button_color=BLUE_BUTTON_COLOR)],
                    [sg.B('OpenVPN Installation and Configuration', size=(butt_w,butt_h))],
                    [sg.B('GVS Installation', size=(butt_w,butt_h))],
                    [sg.B('Install Required Python Libraries', size=(butt_w,butt_h), button_color=BLUE_BUTTON_COLOR)],
                    [sg.B('Dependency Helper', size=(butt_w,butt_h), button_color=BLUE_BUTTON_COLOR)],
                    [sg.B('Update', size=(butt_w,butt_h), button_color=GREEN_BUTTON_COLOR)],
                    [sg.B('Settings', size=(butt_w,butt_h), button_color=DARK_GRAY_BUTTON_COLOR)],
                    [sg.B('Exit', size=(butt_w,butt_h), button_color=LIGHT_GRAY_BUTTON_COLOR)],
                ], element_justification='c', vertical_alignment='c', expand_x=True,expand_y=True)],
            ]

    window = sg.Window('BRIDGES Lab Installation', layout, resizable=True, size=(400,600), icon=BRIDGES_ICON)


    while True:             # Event Loop
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == 'Dependency Helper':
            dependency_window()
        elif event == 'Install Required Python Libraries':
            install_required_python()
        elif event == 'OpenNSA Installation':
            install_opennsa(gui_enabled=True)
        elif event == 'OpenVPN Installation and Configuration':
            configure_openvpn(gui_enabled=True)
        elif event == 'GVS Installation':
            install_gvs(gui_enabled=True)
        elif event == 'Run OpenNSA':
            run_opennsa()
        elif event == 'Update':
            try:
                update()
            except Exception as e:
                sg.popup('ERROR: ' + str(e))
            sg.popup('Up to date! Notice: some update changes may require application restart')
        elif event == 'Settings':
            theme_change = settings_window()
            if theme_change:
                window.close()
                start_gui()
#//=========================================

# TESTING HELPER (UNCOMMENT TO TEST GUI ONLY)
#start_gui()