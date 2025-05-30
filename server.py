import requests
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from io import BytesIO
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from PIL import Image

import os

app = FastAPI()
IMAGE_PATH = "latest.jpg"
class Data1(BaseModel):
    msg: str

class Data2(BaseModel):
    temperature: float
    
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
def revcive_msg(data:Data1):
    print(f"Received from ESP32: {data.msg}")
    return {"status": "success", "received": data.msg}

@app.post("/test")
def revcive_msg(data:Data2):
    print(f"Received : {data}")
    return {"status": "success", "received": data}
    
@app.post("/send_data")
async def receive_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    # Save the image to a known location
    image_path = '/tmp/received.jpg'
    image.save(image_path)
    print(f"Image saved at {image_path}")
    return JSONResponse(content={"status": "Image received", "filename": file.filename})

@app.post("/livecam")
async def receive_image(file: UploadFile = File(...)):
    contents = await file.read()
    with open(IMAGE_PATH, "wb") as f:
        f.write(contents)
    return JSONResponse(content={"status": "received"})

@app.get("/latest.jpg")
async def get_latest_image():
    if os.path.exists(IMAGE_PATH):
        return FileResponse(IMAGE_PATH, media_type="image/jpeg")
    return JSONResponse(content={"error": "No image yet"}, status_code=404)
