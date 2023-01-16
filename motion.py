import RPi.GPIO as GPIO
import time
from requests import get
import smtplib

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN) # PIR sensor


def checkSensors():
    time.sleep(5)
    while True:
        # Check if there is any motion detected
        statusPIR =  GPIO.input(4)
        if statusPIR == 1:  
            time.sleep(0.25)
            statusPIR =  GPIO.input(4)
            if statusPIR == 1:
                print("Motion detected!")
                sendEmail()
                time.sleep(60) 
        time.sleep(0.25) 

    
def sendEmail():
    # Set the email 
    ip = get('https://api.ipify.org').content.decode('utf8')
    subject = 'Kretanje detektovano'
    body = 'Aktivniran je senzor pokreta, proveri kameru na streamu:\n' + 'https://' \
           + ip + ':8080/index.html' + '\n\n\n' + 'Vreme: ' + time.strftime("%H:%M:%S", time.localtime())

    # Set up the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('osurv.projekat@gmail.com', 'gtmvzytwxconqudt')

    # Set up the message
    msg = "Subject: {}\n\n{}".format(subject, body)

    # Send the email
    server.sendmail('osurv.projekat@gmail.com', 'osurv.projekat@gmail.com', msg)

    # Disconnect from the server
    server.quit()
            
checkSensors()
