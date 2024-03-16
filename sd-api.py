import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from flask import Flask, request, jsonify
from pathlib import Path
import os
import aiohttp
import asyncio
import random


app = Flask(__name__)

class StableError(Exception):
    def __init__(self, status_code, message="StableAPI Error"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class StableAPI:

    url = "http://localhost:7860"
    TIMEOUT = 100

    @classmethod
    async def generateImage(cls, input, width, height):

        with open('payload3.json', 'r') as file:
            payload = json.load(file)

        async with aiohttp.ClientSession() as session:
            response = requests.post(url=f'{cls.url}/sdapi/v1/txt2img', json=payload)
            r = response.json()

            for i in r['images']:
                image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

                png_payload = {
                    "image": "data:image/png;base64," + i
                }
                response2 = requests.post(url=f'{cls.url}/sdapi/v1/png-info', json=png_payload)

                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", response2.json().get("info"))
                image.save('output.png', pnginfo=pnginfo)

@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    line = data.get('prompt')
    width, height = data.get('width'), data.get('height')

    asyncio.run(StableAPI.generateImage(line, width, height))
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
