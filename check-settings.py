#!/usr/bin/env python

import argparse
import serial

parser = argparse.ArgumentParser(description='Check WorkBee settings')
parser.add_argument('--device', default='/dev/ttyUSB0', help='USB device')
args = parser.parse_args()


def parse_lines(lines):
    settings = {}
    for line in lines:
        before_space = line.split(' ')[0].rstrip()
        if before_space == 'ok':
            continue
        param, value = before_space.split('=')
        settings[param] = value.rstrip()
    return settings

# parse settings file
with open('settings.txt', 'r') as f:
    desired_settings = parse_lines(f.readlines())

# read and parse serial (Grbl)
with serial.Serial(args.device, 115200, timeout=2) as ser:
    ser.write('\x18')  # soft reset
    lines = ser.readlines()
    welcome = lines[1].split(" ")
    if welcome[0] != 'Grbl':
        raise RuntimeError('did not find the Grbl welcome message')
    print('Connected to Grbl version {}'.format(welcome[1]))
    
    ser.write(b'$$\n')
    actual_settings = parse_lines(ser.readlines())

sorted_keys = sorted(desired_settings.keys(), key=lambda k: int(k[1:]))
for key in sorted_keys:
    desired = desired_settings[key]
    actual = actual_settings[key]
    if desired != actual:
        print('Found difference in {}: desired {}, actual {}'.format(key, desired, actual))
