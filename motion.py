import requests
import cv2, time, pandas 
from datetime import datetime
import urllib
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


static_back = None 
motion_list = [ None, None ] 
times = []

# video baslatilir
video = cv2.VideoCapture('http://192.168.1.38:8080/video')
#gonderici mail bilgileri

gmail_user ="*" 
gmail_pwd ="*"

#mail gonderme fonksiyonu
def mail(to, subject, text, attach):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject 
    msg.attach(MIMEText(text))
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attach, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition','attachment; filename=%s' %os.path.basename(attach))
    msg.attach(part) 
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    mailServer.close()


while True: 
    # videodan anlik resimler okur
    check, frame = video.read()  
    motion = 0
  
    # renkli fotografi gri yapar
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
  
    # gri fotografi gaussionblura cevirir degisim daha kolay anlasilir 
    gray = cv2.GaussianBlur(gray, (21, 21), 0) 

    if static_back is None: 
        static_back = gray 
        continue
     
    diff_frame = cv2.absdiff(static_back, gray) 
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1] 
    thresh_frame = cv2.dilate(thresh_frame, None, iterations = 7) 
  
    # hareketin kontoru algilanir 
    (_, cnts, _) = cv2.findContours(thresh_frame.copy(),  
                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
  
    for contour in cnts: 
        if cv2.contourArea(contour) < 100000: 
            continue
        motion = 1
  
        (x, y, w, h) = cv2.boundingRect(contour) 
        # hareket olan cisim yesil cerceveye alinir
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 
  
    # Appending status of motion 
    motion_list.append(motion)  
    motion_list = motion_list[-2:] 
  
    # eger hareket varsa
    if motion_list[-1] == 1 and motion_list[-2] == 0:
        dimg= video.read()[1]
        timestart=datetime.now().strftime('%d-%m-%Y_%H:%M')   
        cv2.imwrite(timestart + '.jpg', dimg)            
        #times.append(datetime.now())      
        data = urllib.urlopen("https://api.thingspeak.com/update?api_key=4PYM18O67H3853J8&field1="+timestart);
        data2= urllib.urlopen("https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=H1JSYH19QHUOAWPT&status="+"Misafiriniz Var! :"+timestart);
        time.sleep(8.0)
        mail("yasemincerci14@gmail.com","Merhaba bu mail Raspberry'den geldi","Misafir Var!",'/home/pi/Desktop/%s.jpg'%(timestart))
        
           
    #cv2.imshow("Gray Frame", gray) 
    #cv2.imshow("Difference Frame", diff_frame) 
    #cv2.imshow("Threshold Frame", thresh_frame) 
    #cv2.imshow("Color Frame", frame) 
   
video.release() 
cv2.destroyAllWindows()
