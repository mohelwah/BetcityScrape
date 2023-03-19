# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs

prefs.hardware['audioLib'] = 'ptb'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
# Store info about the experiment session
psychopyVersion = '2022.2.5'
expName = 'builder_audio_for_experimentation'  # from the Builder filename that created this script
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
}
# --- Show participant info dialog --
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
                                 extraInfo=expInfo, runtimeInfo=None,
                                 originPath='/Users/mpincu2/Desktop/Projects/Syncopy Design Lab/EEG Micah project/Psychopy_Tasks_for_ASTRO/PVT/builder_audio_for_experimentation.py',
                                 savePickle=True, saveWideText=True,
                                 dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename + '.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

# Set up the window
win = visual.Window(size=[400, 400], fullscr=False, color='black')

# Create a text stimulus for the timer
timer = visual.TextStim(win, text="", pos=(0, 0), color="white", height=0.2)

# --- Initialize components for Routine "trial" ---
sound_1 = sound.Sound('A', secs=-1, stereo=True, hamming=True,
                      name='sound_1')
sound_1.setVolume(1.0)

# update component parameters for each repeat
sound_1.setSound('A', secs=50, hamming=True) #I ALSO TRIED COMMENTING THIS OUT
sound_1.setVolume(1.0, log=False)

# Initialize sound parameters
# tone_playing = False
tone_duration = 0.2
tone_iti = 3.0

# Clear any existing events
event.clearEvents()

# Set the interstimulus interval range for the visual stimuli
isi_range = [2, 4]

# Set the duration of the feedback display for the visual stimuli
feedback_duration = 1.0

# Initialize the trial counter and RT list
trial_num = 1
rts = []
isi_clock = core.Clock()
response = None

# Initialize the clock
experimentClock = core.Clock()
trial_clock = core.Clock()


def check_sound():
    # start playing if it is within the initial period, and isn't already playing
    math = np.mod(experimentClock.getTime(), tone_iti)
    if math < tone_duration:
        if sound_1.status == NOT_STARTED:
            now = core.getTime()
            sound_1.play(when=now)
        else:
            now = core.getTime()
            sound_1.play(when=now)
    else:
        sound_1.stop()

#V2 of check_sound():
#def check_sound():
#    # start playing if it is within the initial period, and isn't already playing
#    math = np.mod(experimentClock.getTime(), tone_iti)
#    if math < tone_duration:
#        if sound_1.status == NOT_STARTED:
#            now = core.getTime()
#            sound_1.play(when=now)
#            print('tone starting',now)
#            sound_1.status == STARTED
#    else:
#        sound_1.stop()

while experimentClock.getTime() < 600:  # 10 minutes
    check_sound()
    # Wait for the interstimulus interval to elapse
    isi_duration = np.random.uniform(isi_range[0], isi_range[1])
    isi_clock.reset()
    while isi_clock.getTime() < isi_duration:
        check_sound()
        win.flip()

    # Start the clock for this trial
    trial_clock.reset()
    timer.setText("0")

    # Display the timer and wait for a response
    while not response:
        timer.setText("{:.0f}".format(trial_clock.getTime() * 1000))
        timer.draw()
        win.flip()
        check_sound()
        keys = event.getKeys()
        if 'escape' in keys:
            response = 'escape'
        elif 'space' in keys:
            response = trial_clock.getTime()

    # Check if the response was the 'escape' key
    if response == 'escape':
        break

    # Show the response time for 1 second
    feedback_clock = core.Clock()
    feedback_text = visual.TextStim(win, text="{:.0f}".format(response * 1000), pos=(0, 0), color="white", height=0.2)
    while feedback_clock.getTime() < 1.0:
        check_sound()
        feedback_text.draw()
        win.flip()

    # Clear the screen before the next trial
    win.flip(clearBuffer=True)

    # Get the RT and add it to the list
    rt = response * 1000
    rts.append(rt)

    # Clear the response variable
    response = None

    # Increment the trial counter
    trial_num += 1

# Close the window
win.close()

# Print the RTs for each trial
print('RTs: ', rts)