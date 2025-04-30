import requests
import cv2
import numpy as np
from fastapi import FastAPI
from io import BytesIO
from starlette.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    msg: str
    
# Your ESP32-CAM snapshot URL
cam_url = "http://10.18.114.67/capture"

@app.get("/")
def read_root():
    return {"message": "ESP32 Cam with Server Testing"}

@app.get("/frame")
def get_frame():
    # Fetch snapshot
    response = requests.get(cam_url)
    if response.status_code == 200:
        # Decode image
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, -1)
        _, img_encoded = cv2.imencode('.jpg', frame)

        # Return JPEG image as a streaming response
        return StreamingResponse(BytesIO(img_encoded.tobytes()), media_type="image/jpeg")
    
    return {"error": "Couldn't Fetch Frame"}

@app.post("/esp32Controller")
def revcive_msg(data:Data):
    print(f"Received from ESP32: {message.msg}")
    return {"status": "success", "received": message.msg}
    
