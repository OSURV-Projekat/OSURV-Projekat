import RPi.GPIO as GPIO
import threading
import netifaces
import smtplib
import time


PIR_SENSOR = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_SENSOR, GPIO.IN) # PIR sensor   
    

def SendEmail():
    # Set the email 
    ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
    subject = 'Detektovano kretanje'
    body = 'Aktivniran je senzor pokreta, proveri kameru na streamu:\n' + 'http://' + ip + ':8080/index.html' + '\n\n\n' + 'Vreme: ' + time.strftime("%H:%M:%S", time.localtime())

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
    time.sleep(15)
   
    

timePeriod = 5 # Seconds
timeActive = 0
timeInactive = 0


try:
    time.sleep(2) # Sleeps for 2 seconds to stabilize the sensor
    print("PIR Sensor (CTRL+C to exit)")
    while True:
        if GPIO.input(PIR_SENSOR):
            timeActive += 0.5
            print("Motion detected! Counter: {}".format(int(timeActive * 2)))
            time.sleep(0.5) # Add a delay to avoid false positives
        else:
            timeInactive += 0.5
            print("No motion! Counter: {}".format(int(timeInactive * 2)))
            time.sleep(1)
            
        if timePeriod <= timeActive + timeInactive:
            print("Reseting activity times")
            if timeActive >= 2: #Active at least 40% to avoid false positives
                print
                print("There is confirmed motion activity, sending email notification!")
                print
                SendEmail()
            timeActive = 0
            timeInactive = 0
            
                 
            

except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
