import cv2
#camera use and detection 
import os
# for camera access
from tensorflow.keras.models import load_model
#image detection and overall performance
import numpy as np
from pygame import mixer
#beep using mixer function of pygame
import time


# Initialize the mixer and load the alarm sound
mixer.init()
sound = mixer.Sound('alarm.wav')

# Load Haarcascades for face and eye detection
face = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_alt.xml')
leye = cv2.CascadeClassifier('haarcascade/haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier('haarcascade/haarcascade_righteye_2splits.xml')
eyes = cv2.CascadeClassifier('haarcascade/haarcascade_eye.xml')

lbl = ['Closed eyes', 'Open eyes']

# Load the trained model
model = load_model('CNN__model.h5')
path = os.getcwd()
cap = cv2.VideoCapture(0)  # Access the camera
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
count = 0
score = 0
thicc = 2
rpred = [99]
lpred = [99]

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face.detectMultiScale(gray, minNeighbors=5, scaleFactor=1.1, minSize=(25, 25))  # Face detection
    eye = eyes.detectMultiScale(gray)  # Eye detection
    left_eye = leye.detectMultiScale(gray)  # Left eye detection
    right_eye = reye.detectMultiScale(gray)  # Right eye detection
    
    cv2.rectangle(frame, (0, height - 50), (200, height), (0, 0, 0), thickness=cv2.FILLED)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (150, 150, 150), 1)

    for (x, y, w, h) in eye:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (150, 150, 150), 1)

    for (x, y, w, h) in right_eye:
        r_eye = frame[y:y + h, x:x + w]
        count += 1
        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (100, 100))
        r_eye = r_eye / 255.0
        r_eye = r_eye.reshape(100, 100, 1)  # Ensure the last dimension is 1 for grayscale
        r_eye = np.expand_dims(r_eye, axis=0)
        predictions = model.predict(r_eye)
        rpred = (predictions > 0.5).astype("int32")

        if rpred[0] == 1:
            lbl = 'Open'
        else:
            lbl = 'Closed'
        break

    for (x, y, w, h) in left_eye:
        l_eye = frame[y:y + h, x:x + w]
        count += 1
        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (100, 100))
        l_eye = l_eye / 255.0
        l_eye = l_eye.reshape(100, 100, 1)  # Ensure the last dimension is 1 for grayscale
        l_eye = np.expand_dims(l_eye, axis=0)
        predictions = model.predict(l_eye)
        lpred = (predictions > 0.5).astype("int32")

        if lpred[0] == 1:
            lbl = 'Open'
        else:
            lbl = 'Closed'
        break

    if rpred[0] == 0 and lpred[0] == 0:
        score += 1
        cv2.putText(frame, "Closed", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    else:
        score -= 1
        cv2.putText(frame, "Open", (10, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

    if score < 0:
        score = 0
    cv2.putText(frame, 'Score:' + str(score), (100, height - 20), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
    
    if score > 10:
        # Person is feeling sleepy so we beep the alarm
        cv2.imwrite(os.path.join(path, 'image.jpg'), frame)
        try:
            sound.play()
        except:
            pass
        if thicc < 16:
            thicc += 2
        else:
            thicc -= 2
            if thicc < 2:
                thicc = 2
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), thicc)
    
    cv2.imshow('Driver drowsiness detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()