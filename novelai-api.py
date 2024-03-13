from flask import Flask, request, jsonify
import aiohttp
import asyncio
import zipfile
from pathlib import Path
import os
from dotenv import load_dotenv

app = Flask(__name__)

class NovelAIError(Exception):
    def __init__(self, status_code, message="NovelAI Error"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class NovelAI:
    BASE_ADDRESS = 'https://api.novelai.net'
    TIMEOUT = 100

    @classmethod
    async def getToken(cls):
        load_dotenv()
        key = os.getenv("NOVELAI_KEY")
        return key

    @classmethod
    async def generateImage(cls, input, width, height):
        token = await cls.getToken()
        base = " best quality, amazing quality, very aesthetic, absurdres"
        negative = "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            url = cls.BASE_ADDRESS + "/ai/generate-image"
            payload = {
                "input": input + base,
                "model": "nai-diffusion-3",
                "parameters": {
                    "legacy": False,
    "quality_toggle": False,
    "width": width,
    "height": height,
    "scale": 8,
    "sampler": "k_euler",
    "steps": 28,
    "n_samples": 1,
    "reference_strength": 0.0,
    "noise": 0,
    "uc_preset": 1,
    "controlnet_strength": 1,
    "dynamic_thresholding": False, 
    "dynamic_thresholding_percentile": 0.999, 
    "dynamic_thresholding_mimic_scale": 10.0, 
    "sm": True, 
    "sm_dyn": False, 
    "skip_cfg_below_sigma": 0.0,
    "uncond_scale": 1,
    "cfg_rescale": 0,
    "noise_schedule": "native",
    "seed": 0,
    "negative_prompt": negative
                    
                }
            }
            async with session.post(url, headers=headers, json=payload, timeout=cls.TIMEOUT) as response:
                if response.status == 200:
                    data = await response.read()
                    return data
                else:
                    error = await response.json()
                    raise NovelAIError(response.status, error.get("message", "Unknown error!"))

@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    line = data.get('prompt')
    width, height = data.get('width'), data.get('height')
    image_data = asyncio.run(NovelAI.generateImage(line, width, height))

    # Save the ZIP file
    zip_path = Path("results/image.zip")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path.write_bytes(image_data)

# Extract the contents of the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        extracted_images = zip_ref.namelist()
        
        for image_file in extracted_images:
            # Rename the copy to image_{i}.png
            extracted_image_path = zip_path.parent / f"image.png"
            zip_ref.extract(image_file, path=zip_path.parent)
            (zip_path.parent / image_file).rename(extracted_image_path)
            i = 0
        for image_file in extracted_images:
            # Ensure the extracted image file is named as image.png
            if i == 0:
                extracted_image_path = zip_path.parent / "image.png"
            else:
                extracted_image_path = zip_path.parent / f"image_{i}.png"
            
            # Increment index if the file already exists
            while extracted_image_path.exists():
                i += 1
                extracted_image_path = zip_path.parent / f"image_{i}.png"

            zip_ref.extract(image_file, path=zip_path.parent)
            (zip_path.parent / image_file).rename(extracted_image_path)
            i += 1



    # Delete the original ZIP file
    zip_path.unlink()

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
