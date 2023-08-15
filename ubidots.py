import time
import requests
import math
import random
import RPi.GPIO as GPIO
import threading
import dht11

TOKEN = "BBFF-4bmyMz2wVLdu6DRAUk8jjnK5yqvZeR"
DEVICE_LABEL = "raspi"
VARIABLE_LABEL_1 = "temprature"
VARIABLE_LABEL_2 = "humidity"
VARIABLE_LABEL_3 = "ultrasonic1"
VARIABLE_LABEL_4 = "ultrasonic2"

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#set GPIO Pins
GPIO_TRIGGER1 = 18
GPIO_ECHO1 = 15
GPIO_TRIGGER2 = 22
GPIO_ECHO2 = 23
LEDR = 25
LEDG = 8
instance = dht11.DHT11(pin = 4)

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER1, GPIO.OUT)
GPIO.setup(GPIO_ECHO1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)
GPIO.setup(GPIO_ECHO2, GPIO.IN)
GPIO.setup(LEDG, GPIO.OUT)
GPIO.setup(LEDR, GPIO.OUT)

def distance1():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER1, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER1, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO1) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO1) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def distance2():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER2, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER2, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO2) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO2) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def build_payload(variable_1, variable_2, variable_3, variable_4):
    # Creates two random values for sending data
    result = instance.read()
    if result.is_valid():
        GPIO.output(LEDG, GPIO.HIGH)
        value_1 = round(result.temperature - 3.1,2)
        value_2 = result.humidity - 3.1
        value_3 = round(distance1(),1)
        value_4 = round(distance2(),1)

        payload = {variable_1: value_1,
                variable_2: value_2,
                variable_3: value_3,
                variable_4: value_4}

        return payload
    else:
        value_3 = round(distance1(),1)
        value_4 = round(distance2(),1)

        payload = {
                variable_3: value_3,
                variable_4: value_4}
        print("Error: %d" % result.error_code) #humidity
    GPIO.output(LEDG, GPIO.LOW)



def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        print(req.json())
        status = req.status_code
        attempts += 1
        GPIO.output(LEDG, GPIO.LOW)
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3, VARIABLE_LABEL_4)

    print("[INFO] Attemping to send data")
    print("[INFO] send payload to ubidots => " + str(payload))
    post_request(payload)   #kirim data ke ubidots
    print("[INFO] finished")


if __name__ == '__main__':
    while (True):
        main()
        time.sleep(1)
        print("\n")