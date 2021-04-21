import PySimpleGUI as sg
from src import Simulator
from src import Config

cfg = Config()
def simulatecode():
    # Runs a Simulation Code
    sim = Simulator()
    sim.run()



sg.theme('DarkAmber')   # Add a touch of color

layout = [

# Slider for Transmission probablity
# Slider for Travel Frequency
#Frequency reduced if both central and Travel enabled

    [
        sg.Frame('Layout customization', [[
            sg.Text('Enter the number of row and column for generating community Grid')],
            [sg.Text('Number of rows:', key='row1'),sg.InputText()],
            [sg.Text('Number of Columns:', key='row2'),sg.InputText()]])
            #Validation for Integer
    ],
    [
        sg.Frame('Preventive measures', [[
            sg.Checkbox(
                'Mask', key='-mask-'), sg.Checkbox('Vaccine', key='-vaccine-')
                #Slider for Mask effectiveness
                #Ratio of Population with mask slider
        ]])
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
        sg.Frame('Symptoms', [[ # Change to radio button for Symptomatic and Asymptomatic
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

#Layout2 option for Viewing predefined scenarios and radio button to choose between layout

window = sg.Window('Disease Simulation', layout)
event, values = window.Read()

if values['-mask-']:
    cfg.MASKS = True
else :
    cfg.MASKS = False

if values['-vaccine-']:
    cfg.VACCINE = True
else :
    cfg.VACCINE = False
###
if values['-quarantine-']:
    cfg.QUARANTINE = True
else :
    cfg.QUARANTINE = False

if values['-travel-']:
    cfg.TRAVEL = True
else :
    cfg.TRAVEL = False

if values['-centralLocation-']:
    cfg.CENTRAL_LOCATION = True
else :
    cfg.CENTRAL_LOCATION = False

if values['-symptomatic-']:
    cfg.SYMPTOMATIC_ASYMPTOMATIC = True
else :
    cfg.SYMPTOMATIC_ASYMPTOMATIC = False




if event == 'Run':
    cfg.COMMUNITY_ROWS=5
    cfg.COMMUNITY_COLS=5
    simulatecode()

window.Close()