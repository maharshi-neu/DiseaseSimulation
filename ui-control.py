import PySimpleGUI as sg
from src import Simulator, cfg

row=1
col=1
person=300
I0=3
qday=5

def simulatecode():
# Runs a Simulation Code
    sim = Simulator()
    sim.run()   


sg.theme('DarkAmber')   # Add a touch of color

layout = [

# Default values for slider, text box and validation if no values passed
# Frequency reduced if both central and Travel enabled

[
sg.Frame('Disease Options', [
    [sg.Radio('COVID-19', 'num', default=True, key='r-covid') ,sg.Radio('Influenza', 'num', key='influ'), sg.Button('Set')]] )
],
[
    sg.Frame('Layout customization', [[
        sg.Text('Enter the number of row and column for generating community Grid')],
        [sg.Text('Number of rows:', key='row1'), sg.InputText(row, size=(6, 1),key='community-rows')],
        [sg.Text('Number of Columns:', key='row2'), sg.InputText(col, size=(6, 1),key='community-cols')],
        [sg.Text('Number of Days of Simulation:', key='ndays'), sg.InputText(60, size=(6, 1),key='n-days')],
        [sg.Text('Number of Persons:', key='person'), sg.InputText(person, size=(6, 1), key='person-count')],
        [sg.Text('People Initially infected:', key='initial-infected'), sg.InputText(I0, size=(6, 1),key='infected-count')],
        ])
        # Validation for Integer
],
[
    sg.Frame('Transmission Probability', [
        [sg.Slider(range=(0, 1), default_value=cfg.TRANSMISSION_PROBABILITY, size=(30, 10),
                    orientation="h", resolution=0.1, key='prob-slider')]
        ]),
        # Validation for Integer
],

[
    sg.Frame('Travel Frequency(Inter Community)', [
        [sg.Slider(range=(0, 0.1), default_value=0.01, size=(30, 10),
                    orientation="h", resolution=0.01, key='freq-slider')]
        ]),
        # Validation for Integer
],

[
    sg.Frame('Preventive measures', [[
        sg.Checkbox(
            'Mask', key='mask'), sg.Checkbox('Vaccine', key='vaccine')],
        [sg.Text('Mask effectiveness'),
        sg.Slider(range=(0, 1), default_value=0,size=(20, 10), orientation="h", resolution=0.1, key='mask-slider')],
        [sg.Text('Ratio of Population wearing mask'),
            sg.Slider(range=(0, 1), default_value=0, size=(20, 10), orientation="h", resolution=0.1, key='mask-ratio-slider')]
    ])
],

[
    sg.Frame('Barriers Imposed', [[
        sg.Checkbox(
            'Quarantine', key='quarantine'),
        sg.Text('Quarantine at Day:', key='qday'), sg.InputText(qday, size=(6, 1), key='qday-value'),sg.Button('Lockdown')

    ]])
],

[
    sg.Frame('Movement', [[
        sg.Checkbox(
            'Inter Community', key='travel'), sg.Checkbox('Central Location', key='centralLocation')
    ]])
],

[
    sg.Frame('Symptoms', [[ 
        sg.Checkbox(
            'Enable for Asymtomatic', key='symptomatic')
    ]])
],

[
    sg.Frame('Contact Tracing', [[ 
        sg.Checkbox(
            'Enable Contact Tracing', key='c-tracing')
    ]])
],

[
    sg.Frame('Controls', [[
        sg.Button('Run'), sg.Exit('Exit')
    ]])
]

]

# Layout2 option for Viewing predefined scenarios and radio button to choose between layout
window = sg.Window('Disease Simulation',  layout, resizable=True,location=(0,0))

while True: 
    event, values = window.Read()
    if event ==  'Set':
        if values['influ']:
            cfg.TRANSMISSION_PROBABILITY = 0.50
            window['prob-slider'].update(cfg.TRANSMISSION_PROBABILITY)
            cfg.RECOVERED_PERIOD_IN_DAYS = 5
            #window['community-cols'] = 1
        else:
            cfg.TRANSMISSION_PROBABILITY = 0.90
            window['prob-slider'].update(cfg.TRANSMISSION_PROBABILITY)
            cfg.RECOVERED_PERIOD_IN_DAYS = 14

    if values and values.get('mask'):
        cfg.MASKS = True
    else:
        cfg.MASKS = False

    if  values and values.get('vaccine'):
        cfg.VACCINE = True
    else:
        cfg.VACCINE = False
    ###
    if values and values.get('quarantine'):
        cfg.QUARANTINE = True
    else:
        cfg.QUARANTINE = False

    if  values and values.get('travel'):
        cfg.TRAVEL = True
    else:
        cfg.TRAVEL = False

    if values and values.get('centralLocation'):
        cfg.CENTRAL_LOCATION = True
    else:
        cfg.CENTRAL_LOCATION = False

    if values and values.get('symptomatic'):
        cfg.SYMPTOMATIC_ASYMPTOMATIC = True
    else:
        cfg.SYMPTOMATIC_ASYMPTOMATIC = False

    if values and values.get('q-day'):
        cfg.QUARANTINE_AT_DAY = int(values['qday-value'])
    else:
        cfg.QUARANTINE_AT_DAY = 5

    if event == 'Run':
    # Default handling value if value is zero
        if values['n-days'] == '':
            cfg.RUN_TIME_IN_DAYS = 60
        else:
            cfg.RUN_TIME_IN_DAYS = int(values['n-days'])
        if values['community-cols'] == '':
            cfg.COMMUNITY_COLS == 1
        else:
            cfg.COMMUNITY_COLS = int(values['community-cols'])

        if values['community-rows'] == '':
            cfg.COMMUNITY_ROWS == 1
        else:
            cfg.COMMUNITY_ROWS = int(values['community-rows'])
        if values['person-count'] =='':
            cfg.POPULATION = 300
        else:
            cfg.POPULATION = int(values['person-count'])

        if values['infected-count'] =='':
            cfg.I0 = 3
        else:
            cfg.I0 = int(values['infected-count'])

        cfg.TRANSMISSION_PROBABILITY = float(values['prob-slider'])

        if cfg.CENTRAL_LOCATION and cfg.TRAVEL :
            cfg.TRAVEL_FREQUENCY = 0.01
        else:
            cfg.TRAVEL_FREQUENCY = float(values['freq-slider'])

        cfg.MASK_EFFECTIVENESS = float(values['mask-slider'])
        cfg.RATIO_OF_POP_WITH_MASKS = float(values['mask-ratio-slider'])

        if values['c-tracing']:
            cfg.CONTACT_TRACING = True
        else:
            cfg.CONTACT_TRACING = False

        simulatecode()
    if event =='Lockdown':
        window['travel'].update(False)
        window['freq-slider'].update(0.00)
        window['community-rows'].update(15)
        window['community-cols'].update(15)
        window['person-count'].update(300)
        window['centralLocation'].update(True)

    if event == sg.WIN_CLOSED:
        window.close()
        break
    if event =='Exit':
        window.Close()
        break
