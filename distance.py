# Module Imports
import RPi.GPIO as GPIO
import time
import argparse
import requests
import json

TRIGGER_PIN = 12
ECHO_PIN = 10
INTERVAL = .05
MAX_DISTANCE = 100

API = '/api/proximity/'
port = 5001
server_url = '192.168.0.8'
full_url = ''
debug = False

parser = argparse.ArgumentParser()
parser.add_argument('-S', '--server')
parser.add_argument('-P', '--port')
parser.add_argument('-D', '--debug')

args = parser.parse_args()

if (args.server):
    server_url = args.server

if (args.port):
    port = args.port

if (args.debug):
    res = (args.debug).lower()
    if res == "false":
        debug = False
    elif res == "true":
        debug = True

# create the post address url.
full_url = 'http://{}:{}{}'.format(server_url, port, API)


def setup():

    GPIO.setmode(GPIO.BOARD)   # Set the GPIO pins mode - Also set in drive.py

    # Turn GPIO warn off - CAN ALSO BE Set in drive.py
    GPIO.setwarnings(False)

    GPIO.setup(TRIGGER_PIN, GPIO.OUT)   # Set the Front Trigger pin to output
    GPIO.setup(ECHO_PIN, GPIO.IN)       # Set the Front Echo pin to input

    print('posting data to:{}'.format(full_url))


def get_distance():
    GPIO.output(TRIGGER_PIN, False)
    time.sleep(INTERVAL)
    pulse_start = 0
    pulse_end = 0

    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance


def destroy():
    print('\n... Shutting Down...\n')
    GPIO.cleanup()


def post_data(distance):
    data = json.dumps({'proximity': int(distance)})

    try:
        r = requests.post(
            full_url,
            json={"proximity": int(distance)})
        if debug:
            print('data sent: {}     ---  response received: {}'.format(data, r))
    except requests.exceptions.Timeout:

        print('Timeout error, connecting to websocket server.')
    except requests.exceptions.RequestException as e:
        print('error:', e)


def main():
    setup()
    try:
        while 1:
            distance = get_distance()
            if 0 <= distance < MAX_DISTANCE:
                # print('Distance: {} cm' .format(int(distance)))
                post_data(distance)
    except:
        destroy()


if __name__ == '__main__':

    main()
