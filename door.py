import RPi.GPIO as GPIO
import time
import smtplib
import netifaces




GPIO.setmode(GPIO.BOARD);

door_pin=16
lock_pin=18
GPIO.setup(door_pin,GPIO.IN)
GPIO.setup(lock_pin,GPIO.IN)




def sendEmail(mode):
    
    if(mode==0):
        subject="HEY:View door status and camera LINK"
        msg="check door status and camera stream at at http://"
    else:
        subject="Forgot to lock door!!!!"
        msg="hey you forgot to lock the door check door status and camera stream at http://"
    
    ip=netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
    body=msg+ip+":8080/index.html"
    
    print(body)

    
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login('osurv.projekat@gmail.com','gtmvzytwxconqudt')

    msg="Subject:{}\n\n{}".format(subject,body)
    server.sendmail('osurv.projekat@gmail.com','vpavle021@gmail.com',msg)
    server.quit()


def write_door_state(door,lock):
	doorOmsg=" door:open"
	doorCmsg=" door:closed"
	lockOmsg=" lock:open"
	lockCmsg=" lock:closed"
	buff=open('status.txt','w')
	if(door):
		buff.write(doorOmsg+'\n')
	else:
		buff.write(doorCmsg+'\n')
	if(lock):
		buff.write(lockOmsg)
	else:
		buff.write(lockCmsg)
	buff.close()
	
	


lastdoorstate=1
lastlockstate=1

sendEmail(0)

while(1):
    doorin=GPIO.input(door_pin)
    lockin=GPIO.input(lock_pin)
   
    
    if(lastdoorstate==1 and doorin==0):
        i=0
        numberofseconds=120
        print("waiting to lock door")
        while(i<(numberofseconds/4)):
            doorin=GPIO.input(door_pin)
            lockin=GPIO.input(lock_pin)
            write_door_state(doorin,lockin)
            print("door:",doorin)
            print("lock:",lockin)
            i=i+1
            time.sleep(4);
        if(lockin==1 and doorin==0):
            print("you forgot to lock the door")
            sendEmail(1)



    write_door_state(doorin,lockin)
    lastdoorstate=doorin
    lastlockstate=lockin
    print("door:",doorin)
    print("lock:",lockin)
    time.sleep(4)





