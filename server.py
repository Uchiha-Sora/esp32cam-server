import requests
import cv2
import numpy as np
from fastapi import FastAPI
from io import BytesIO

app = FastAPI()

cam_url = "http://10.18.114.67/capture"

@app.get("/")
def read_root():
    return {"message": "ESP32 Cam with Server Testing"}

@app.get("/frame")
def get_frame():
    response = requests.get(cam_url)
    if response.status_code == 200:
        img_array = np.asarray(bytearray(response.content), dtype = np.unit8)
        frame = cv2.imdecode(img_array, -1)
        _, img_encoded = cv2.imencode('jpg', frame)
        return StreamingResponse(ByteIO(img_encoded.tobytes()), media_type = "image/jpeg")
    return {"error":"Couldn't Fetch Frame"}