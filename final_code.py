import argparse
import sys
import numpy as np
import sounddevice as sd
import time
import msvcrt
import keyboard as kb
import threading
import random


# Function to change int variables into string variables
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

# This part of script is used to parse command-line arguments related to audio devices
# It allows the user to list available devices and select a specific device for output.
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
args = parser.parse_args(remaining)

start_idx = 0

# Playback function
def callback(outdata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    global start_idx
    t = (start_idx + np.arange(frames)) / samplerate
    t = t.reshape(-1, 1)  # Change from row vector to column vector

    # To play the same sine wave to both output channels use this:
    outdata[:] = a * np.sin(2 * np.pi * f * t)  # Compute the sine wave
    start_idx += frames


samplerate = sd.query_devices(args.device, 'output')['default_samplerate']

# Close the database connection

########## EXPERIMENT PARAMETERS #########

nTrials = 4  # Number of iterations per condition, should be divisible by 4 (the code assumes 4 blocks of trials, i.e. 3 breaks
nTestTrials = 1  # Number of iterations per condition
doStartupTest = 1  # Play a signal through all motors to make sure everything is working
stimuliDuration = 0.2  # duration of stimuli (in secs)
delayBetweenStimuli = 0.05  # delay between stimuli 1 and stimuli 2
responseTimeWindow = 5  # time window for response
delayAfterResponse = 0.5  # time after response is given until the next is played

# You can change the frequency and amplitude
f = 50
a = 0.1

# This part of the script  lets you choose the Participant ID (introduced using the keyboard)
print("Choose Participant ID:")
try:
    # Read the input event (assuming it returns a string)
    participant_str = kb.read_event(suppress=True).name
    # Convert the input string to an integer
    participantID = int(participant_str)
    print(f"Participant ID: {participantID}\n")

except ValueError:
    print("Invalid input. Please enter a valid number.")

# Function for introducing new information to the text file
def write_to_file(file_path, content):
    with open(file_path, 'a') as file:  # Use 'a' for append mode to add content to an existing file
        file.write(content)

# Figure out what your path to the file is and change it!
file_path = r"D:\Iceland Project\experiment_results.txt"

# These two line opens the file in write mode, effectively clearing its contents, delete if you want all the information of all the participants in the same file
with open(file_path, 'w'):
    pass

experiment_summary = f"""

Experiment Summary for Participant: {participantID}
Time of stimuli: {stimuliDuration}
Time between stimuli: {delayBetweenStimuli}
Frequency: {f}
Amplitude: {a}
"""

write_to_file(file_path, experiment_summary)

nCoils = 32
# Lets you choose how many times you want the actuators to vibrate (write the number in the command window)
num_vibrations=int(input("Enter the number of vibrations you want to generate: "))

# Define patterns
patterns = [
    [[0, 15], [3, 12]],
    [[1, 14], [2, 13]],
    [[4, 11], [7, 8]]
]
available_numbers = list(range(1, len(patterns) + 1))

# Startup test, change the number below, in parentheses into the number of patterns you want to have in one test
for _ in range(3):

    if doStartupTest:
        print('Running startup test...')
        all_channels = list(range(nCoils))

        print("Available patterns:")
        for i, pattern_set in enumerate(patterns):
            print(f"Pattern {i + 1}. Motor set 1: {pattern_set[0]}, Motor set 2: {pattern_set[1]}")

        # Generate random number for pattern selection
        while True:
            random_pattern = random.choice(available_numbers)
            print("Pattern number:", random_pattern)

            if 1 <= random_pattern <= len(patterns):
                selected_pattern_set = patterns[random_pattern - 1]
                available_numbers.remove(random_pattern)  # Remove selected pattern from available patterns
                break



        motor_set_1 = selected_pattern_set[0]
        motor_set_2 = selected_pattern_set[1]

        print(f'Selected pattern: Motor set 1: {motor_set_1}, Motor set 2: {motor_set_2}')
        write_to_file(file_path,
                      f"The participant was subjected to pattern {random_pattern}: Motor set 1: {motor_set_1}, Motor set 2: {motor_set_2} \n")
        # Generate vibrations of the actuators
        asio_ch1 = sd.AsioSettings(channel_selectors=motor_set_1)
        asio_ch2 = sd.AsioSettings(channel_selectors=motor_set_2)
        start_idx = 0
        # Check what number the port of the Madiface XT RME audio device was connected to and change it in the "device=" parts
        for _ in range(num_vibrations):
            with sd.OutputStream(device=8, channels=2, callback=callback,
                                samplerate=samplerate, extra_settings=asio_ch1):
                time.sleep(1)
                sd.stop()

            with sd.OutputStream(device=8, channels=2, callback=callback,
                                samplerate=samplerate, extra_settings=asio_ch2):
                time.sleep(1)
                sd.stop()



    print("Choose orientation: V for VERTICAL, H for HORIZONTAL. Press Q to quit.")

    # Introduce the answer of the participant using the keyboard and store the information in the text file
    while True:
        response = kb.read_event(suppress=True).name.lower()

        if response == 'v':
            print("You selected: VERTICAL")
            write_to_file(file_path, "The participant felt a vertical motion.\n")
            break  # Exit the loop after writing to the file
        elif response == 'h':
            print("You selected: HORIZONTAL")
            write_to_file(file_path, "The participant felt a horizontal motion.\n")
            break  # Exit the loop after writing to the file
        elif response == 'q':
            print("Exiting the program.")
            break  # Exit the loop if 'q' is pressed
        else:
            print("Invalid input. Please choose V, H, or Q to quit.")

    print("Remaining available numbers:", available_numbers)

print(f"Results for Participant {participantID} saved to {file_path}")