import io
import base64
import numpy as np
from PIL import Image
from flask_cors import CORS
from flask import Flask, request, jsonify


app = Flask(__name__)
CORS(app)  # Add this line to enable CORS for the entire app


def pad_image(img_array, block_size):
    # Pad the image array to make its dimensions divisible by block_size
    height, width, channels = img_array.shape
    pad_height = (block_size - height % block_size) % block_size
    pad_width = (block_size - width % block_size) % block_size
    padded_img = np.pad(img_array, ((0, pad_height), (0, pad_width), (0, 0)), mode='constant')
    return padded_img

def quantize(block, quality):
    # Keep the real part of the first `quality` frequencies, set the rest to zero
    quantized_block = np.zeros_like(block, dtype=np.complex128)
    quantized_block.real[:quality, :quality] = block.real[:quality, :quality]
    return quantized_block

def compress_image(img_data, quality=50):
    # Load the image from bytes using PIL
    img = Image.open(io.BytesIO(img_data)).convert("RGB")  # Load as RGB
    img_array = np.array(img, dtype=np.float32)

    # Set the block size for DCT
    block_size = 4

    # Pad the image to ensure each block is 8x8
    padded_img_array = pad_image(img_array, block_size)

    # Perform block-based DCT on the image
    height, width, channels = padded_img_array.shape
    compressed_img = np.zeros((height, width, channels), dtype=np.float32)

    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            block = padded_img_array[y:y+block_size, x:x+block_size, :]
            dct_block = np.fft.fft2(block, axes=(0, 1), norm="ortho")
            quantized_block = quantize(dct_block, quality)
            compressed_img[y:y+block_size, x:x+block_size, :] = quantized_block.real

    # Perform block-based IDCT on the compressed image
    decompressed_img = np.zeros((height, width, channels), dtype=np.float32)

    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            quantized_block = compressed_img[y:y+block_size, x:x+block_size, :]
            idct_block = np.fft.ifft2(quantized_block, axes=(0, 1), norm="ortho").real
            decompressed_img[y:y+block_size, x:x+block_size, :] = idct_block

    # Clip the decompressed image values to be in the valid pixel range (0 to 255)
    decompressed_img = np.clip(decompressed_img, 0, 255)

    # Create a new image in bytes format
    compressed_img = Image.fromarray(decompressed_img.astype(np.uint8))
    img_bytes = io.BytesIO()
    compressed_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Encode the compressed image as base64
    compressed_image_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    return compressed_image_base64

@app.route('/compress', methods=['POST'])
def compress_endpoint():
    # Get the list of image data from the form data
    image_files = request.files.getlist('image')

    # Set the desired quality (you can adjust this as needed)
    quality = 70

    # List to store the results for each image
    results = []

    for image_file in image_files:
        # Get the image data from the form data
        img_data = image_file.read()

        # Get the original image size in bytes
        original_size = len(img_data)

        # Compress the image
        compressed_image_base64 = compress_image(img_data, quality=quality)

        # Get the compressed image size in bytes
        compressed_size = len(base64.b64decode(compressed_image_base64))

        # Append the result for this image to the results list
        results.append({
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compressed_image_base64": compressed_image_base64
        })

    # Return the results as the response in JSON format
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
