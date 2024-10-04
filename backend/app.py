from contextlib import asynccontextmanager
from io import BytesIO

import easyocr
import imagehash
import numpy as np
from fastapi import FastAPI, File, UploadFile
from loguru import logger
from PIL import Image
import time

# Save all files and result to cached
# by a dictionary with key is image hash
cache = {}

# Initialize the model to None
# Load the ML model
reader = easyocr.Reader(
    ["vi", "en"],
    gpu=True,
    detect_network="craft",
    model_storage_directory="./my_model",
    download_enabled=False,
)

app = FastAPI()


@app.post("/preloaded_ocr")
async def ocr(file: UploadFile = File(...)):
    # Read image from route
    request_object_content = await file.read()
    pil_image = Image.open(BytesIO(request_object_content))
    pil_hash = imagehash.average_hash(pil_image)

    if pil_hash in cache:
        logger.info("Getting result from cache!")
        return cache[pil_hash]
    else:
        logger.info("Predicting. Please wait...")
        # Get the detection from EasyOCR
        np_image = np.array(pil_image)
        detection = reader.readtext(np_image)

        # Create the final result
        result = {"bboxes": [], "texts": [], "probs": []}
        for bbox, text, prob in detection:
            # Convert a list of NumPy int elements to premitive numbers
            bbox = np.array(bbox).tolist()
            result["bboxes"].append(bbox)
            result["texts"].append(text)
            result["probs"].append(prob)

        # Save the result to cache
        cache[pil_hash] = result

        return result