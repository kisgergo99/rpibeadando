from flask import Flask, render_template, redirect, url_for
import psutil
import datetime
import water
import os
import sys
import Adafruit_DHT


app = Flask(__name__) #Elindul a flask

def template(title = "HELLO!", text = ""):
    now = datetime.datetime.now()
    timeString = now
    humidity, temperature = Adafruit_DHT.read_retry(11,23)
    sensor = "Hőmérséklet: {0:0.1f} C Páratartalom: {1:0.1f} %".format(temperature, humidity)
    print(sensor)
    templateDate = {
        'title' : title,
        'time' : timeString,
        'text' : text,
        'sensor' : sensor
        }
    return templateDate

@app.route("/")
def hello():
    templateData = template()
    return render_template('main.html', **templateData)

@app.route("/last_watered")
def check_last_watered():
    templateData = template(text = water.get_last_watered())
    return render_template('main.html', **templateData)

@app.route("/sensor")
def action():
    status = water.get_status()
    message = ""
    if (status == 1):
        message = "Öntözz meg!"
    else:
        message = "Nem kell öntözés!"

    templateData = template(text = message)
    return render_template('main.html', **templateData)

@app.route("/water")
def action2():
    water.pump_on() #pumpa bekapcsolasa gombnyomasra
    templateData = template(text = "Öntözés kész!")
    return render_template('main.html', **templateData)

@app.route("/auto/water/<toggle>")
def auto_water(toggle):
    fut = False
    if toggle == "ON": #Gombkapcsolo valtozo
        templateData = template(text = "Automata öntözés bekapcsolva")
        for process in psutil.process_iter():
            try:
                if process.cmdline()[1] == 'auto_water.py':
                    templateData = template(text = "Már fut")
                    fut = True
            except:
                pass
        if not fut:
            os.system("python3 auto_water.py&") #beinditjuk
            
            
    else:
        templateData = template(text = "Automata öntözés kikapcsolva")
        os.system("pkill -f water.py") #kilövés

    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='192.168.1.10', port=80, debug=True)
