#!/usr/bin/env python3

# External module imp
import RPi.GPIO as GPIO
import datetime
import time
import tweepy

#Twitter cuccok
consumer_key = "P1fiQctzQjNUquTcAWQ8Q5s2b"
consumer_secret = "4VuvORKnbbF4cWrxpOXLphuBzEjadMuh2TyJmHXrCaNdtYHmuy"
access_token = "1219939164369584128-aXvSCNBRwKxZhY4zqtl7Ihtrp1muot"
access_token_secret = "lwfgnFN9gUbDfz3bkDakrgPcOigti0GpG4GNN3AQqd2Bi"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret) 
api = tweepy.API(auth)

init = False

GPIO.setmode(GPIO.BOARD) # GPIO tábla

def get_last_watered():
    try:
        f = open("last_watered.txt", "r") 
        return f.readline() #kilistazza a fajlt
    except:
        return "Eddig még nem volt használva!"
      
def get_status(pin = 8):
    GPIO.setup(pin, GPIO.IN) 
    return GPIO.input(pin)

def init_output(pin):
    GPIO.setup(pin, GPIO.OUT) #beallitja hogy kimeneti jel lesz
    GPIO.output(pin, GPIO.HIGH) # kikapcs
    GPIO.output(pin, GPIO.LOW) # bekapcs
    
def auto_water(delay = 5, pump_pin = 7, water_sensor_pin = 8):
    vizszamlal = 0
    init_output(pump_pin) #beallitja hogy a 7es pin(pumpa) lesz az output
    print("Elindult! CTRL + C a megszakítás!")
    try:
        while 1 and vizszamlal < 10:
            time.sleep(delay)
            wet = get_status(pin = water_sensor_pin) == 0
            if not wet:
                if vizszamlal < 5:
                    pump_on(pump_pin, 1)
                vizszamlal += 1
            else:
                vizszamlal = 0
    except KeyboardInterrupt: # Ha CTRL+C lesz
        GPIO.cleanup() # GPIO megszuntetes

def pump_on(pump_pin = 7, delay = 1):
    init_output(pump_pin) #Pumpa pin beallitas
    f = open("last_watered.txt", "a")
    f.write("Utoljára öntözve {}".format(datetime.datetime.now()))
    f.write("\n")
    f.close()
    GPIO.output(pump_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pump_pin, GPIO.LOW) #Elinditja a pumpat
    print(get_status(pin=16))
    try:
        status = "Pumpa beinditva, egy kis loketnyi idore! {}".format(datetime.datetime.now())
        api.update_status(status) #Tweet
    except tweepy.TweepError as error:
        if error.api_code == 187:
            print('Hiba a duplikalt uzenetekben.'+status)
        else:
            raise error
