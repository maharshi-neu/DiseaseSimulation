import PySimpleGUI as sg
from src import Simulator, cfg


def simulatecode():
    # Runs a Simulation Code
    sim = Simulator()
    sim.run()


sg.theme('DarkAmber')   # Add a touch of color

layout = [

# Slider for Transmission probablity
# Slider for Travel Frequency
# Frequency reduced if both central and Travel enabled

    [
        sg.Frame('Layout customization', [[
            sg.Text('Enter the number of row and column for generating community Grid')],
            [sg.Text('Number of rows:', key='row1'), sg.InputText(
                '', size=(6, 1), key='community-rows')],
            [sg.Text('Number of Columns:', key='row2'), sg.InputText('', size=(6, 1), key='community-cols')]])
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
            [sg.Slider(range=(0, 1), default_value=0, size=(30, 10),
                       orientation="h", resolution=0.1, key='freq-slider')]
            ]),
            # Validation for Integer
    ],

    [
        sg.Frame('Preventive measures', [[
            sg.Checkbox(
                'Mask', key='-mask-'), sg.Checkbox('Vaccine', key='-vaccine-')],
            [sg.Text('Mask effectiveness'),
            sg.Slider(range=(0, 1), default_value=0, size=(30, 10), orientation="h", resolution=0.1, key='mask-slider')],
            [sg.Text('Ratio of Population wearing mask'),
                sg.Slider(range=(0, 1), default_value=0, size=(30, 10), orientation="h", resolution=0.1, key='mask-ratio-slider')]
                # Slider for Mask effectiveness
                # Ratio of Population with mask slider
        ])
    ],

    [
        sg.Frame('Barriers Imposed', [[
            sg.Checkbox(
                'Quarantine', key='-quarantine-')
                # Quarantine at which day text box
        ]])
    ],

    [
        sg.Frame('Movement', [[
            sg.Checkbox(
                'Inter Community', key='-travel-'), sg.Checkbox('Central Location', key='-centralLocation-')
        ]])
    ],

    [
        sg.Frame('Symptoms', [[  # Change to radio button for Symptomatic and Asymptomatic
            sg.Checkbox(
                'Are you Symtomatic', key='-symptomatic-')
        ]])
    ],

    [
        sg.Frame('Controls', [[
            sg.Button('Run'), sg.Exit('Stop'),
        ]])
    ]

]

# Layout2 option for Viewing predefined scenarios and radio button to choose between layout

window = sg.Window('Disease Simulation', layout)
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


if event == 'Run':
    # Default handling value if value is zero
    cfg.COMMUNITY_ROWS = int(values['community-rows'])
    cfg.COMMUNITY_COLS = int(values['community-cols'])

    cfg.TRANSMISSION_PROBABILITY = float(values['prob-slider'])
    cfg.TRAVEL_FREQUENCY = float(values['freq-slider'])
    
    cfg.MASK_EFFECTIVENESS = float(values['mask-slider'])
    cfg.RATIO_OF_POP_WITH_MASKS = float(values['mask-ratio-slider'])

    simulatecode()

window.Close()
