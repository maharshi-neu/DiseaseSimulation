import PySimpleGUI as sg
from src import Simulator, cfg


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
    [sg.Radio('COVID-19', 'num', default=True, key='r-covid') ,sg.Radio('Influenza', 'num', key='influ')]] )
],
[
    sg.Frame('Layout customization', [[
        sg.Text('Enter the number of row and column for generating community Grid')],
        [sg.Text('Number of rows:', key='row1'), sg.InputText(
            '', size=(6, 1), key='community-rows')],
        [sg.Text('Number of Columns:', key='row2'), sg.InputText('', size=(6, 1), key='community-cols')],
        [sg.Text('Number of Persons:', key='person'), sg.InputText('', size=(6, 1), key='person-count')],
        [sg.Text('People Initially infected:', key='initial-infected'), sg.InputText('', size=(6, 1), key='infected-count')],
        ])
        # Validation for Integer
],
[
    sg.Frame('Transmission Probability', [
        [sg.Slider(range=(0, 1), default_value=0, size=(30, 10),
                    orientation="h", resolution=0.1, key='prob-slider')]
        ]),
        # Validation for Integer
],

[
    sg.Frame('Travel Frequency', [
        [sg.Slider(range=(0, 0.1), default_value=0, size=(30, 10),
                    orientation="h", resolution=0.01, key='freq-slider')]
        ]),
        # Validation for Integer
],

[
    sg.Frame('Preventive measures', [[
        sg.Checkbox(
            'Mask', key='-mask-'), sg.Checkbox('Vaccine', key='-vaccine-')],
        [sg.Text('Mask effectiveness'),
        sg.Slider(range=(0, 1), default_value=0,size=(20, 10), orientation="h", resolution=0.1, key='mask-slider')],
        [sg.Text('Ratio of Population wearing mask'),
            sg.Slider(range=(0, 1), default_value=0, size=(20, 10), orientation="h", resolution=0.1, key='mask-ratio-slider')]
    ])
],

[
    sg.Frame('Barriers Imposed', [[
        sg.Checkbox(
            'Quarantine', key='-quarantine-'),
        sg.Text('Quarantine at Day:', key='qday'), sg.InputText('', size=(6, 1), key='qday-value'),

    ]])
],

[
    sg.Frame('Movement', [[
        sg.Checkbox(
            'Inter Community', key='-travel-'), sg.Checkbox('Central Location', key='-centralLocation-')
    ]])
],

[
    sg.Frame('Symptoms', [[ 
        sg.Checkbox(
            'Check if Symtomatic', key='-symptomatic-')
    ]])
],

[
    sg.Frame('Contact Tracing', [[ 
        sg.Checkbox(
            'Check to view Contact Tracing', key='c-tracing')
    ]])
],

[
    sg.Frame('Controls', [[
        sg.Button('Run'), sg.Exit('Stop'),
    ]])
]

]

# Layout2 option for Viewing predefined scenarios and radio button to choose between layout

window = sg.Window('Disease Simulation', layout, location=(0,0))
event, values = window.Read()

if values['-mask-']:
    cfg.MASKS = True
else:
    cfg.MASKS = False

if values['-vaccine-']:
    cfg.VACCINE = True
else:
    cfg.VACCINE = False
###
if values['-quarantine-']:
    cfg.QUARANTINE = True
else:
    cfg.QUARANTINE = False

if values['-travel-']:
    cfg.TRAVEL = True
else:
    cfg.TRAVEL = False

if values['-centralLocation-']:
    cfg.CENTRAL_LOCATION = True
else:
    cfg.CENTRAL_LOCATION = False

if values['-symptomatic-']:
    cfg.SYMPTOMATIC_ASYMPTOMATIC = True
else:
    cfg.SYMPTOMATIC_ASYMPTOMATIC = False

if values['qday-value']=='':
    cfg.QUARANTINE_AT_DAY = 5
else:
    cfg.QUARANTINE_AT_DAY = int(values['qday-value'])

if event == 'Run':
# Default handling value if value is zero
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

    if values['c-tracing'] == True:
        cfg.CONTACT_TRACING = True
    else:
        cfg.CONTACT_TRACING = False

    simulatecode()   
#if event == 'STOP':


window.Close()