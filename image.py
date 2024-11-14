from flask import Flask, request, jsonify, send_file, redirect, url_for
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import requests
from io import BytesIO
from google.cloud import storage
import os
import uuid

app = Flask(__name__)

def resize_image(img, size):
    return img.resize(size)

def sharpen_image(img):
    return img.filter(ImageFilter.SHARPEN)

def convert_to_grayscale(img):
    return img.convert("L")

def rotate_image(img, angle):
    return img.rotate(angle)

def blur_image(img, radius):
    return img.filter(ImageFilter.GaussianBlur(radius))

def add_watermark(img, text, position, opacity, font_size):
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    font = ImageFont.truetype("arial.ttf", font_size)  # Use a truetype font
    draw.text(position, text, fill=(255, 255, 255, opacity), font=font)
    watermarked_image = Image.alpha_composite(img.convert('RGBA'), watermark)
    return watermarked_image.convert('RGB')

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    blob.make_public()  # Make the blob publicly accessible
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    return blob.public_url  # Return the public URL of the uploaded image

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    image_url = data.get('image_url')
    size = tuple(data.get('size', (800, 600)))
    sharpen = data.get('sharpen', False)
    grayscale = data.get('grayscale', False)
    rotate = data.get('rotate', None)
    blur = data.get('blur', None)
    watermark_text = data.get('watermark_text', None)
    watermark_position = tuple(data.get('watermark_position', (0, 0)))
    watermark_opacity = data.get('watermark_opacity', 128)
    watermark_font_size = data.get('watermark_font_size', 36)
    convert_to_webp = data.get('convert_to_webp', False)

    if not image_url:
        return jsonify({"error": "image_url is required"}), 400

    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    if size:
        img = resize_image(img, size)
    
    if sharpen:
        img = sharpen_image(img)
    
    if grayscale:
        img = convert_to_grayscale(img)
    
    if rotate is not None:
        img = rotate_image(img, rotate)
    
    if blur is not None:
        img = blur_image(img, blur)
    
    if watermark_text:
        img = add_watermark(img, watermark_text, watermark_position, watermark_opacity, watermark_font_size)

    # Determine the output format and file extension
    if convert_to_webp:
        output_path = 'processed_image.webp'
        img.save(output_path, format='WEBP')
        destination_blob_name = f"{uuid.uuid4()}.webp"
    else:
        output_path = 'processed_image.jpg'
        img = img.convert("RGB")  # Convert to RGB before saving as JPEG
        img.save(output_path)
        destination_blob_name = f"{uuid.uuid4()}.jpg"

    
    bucket_name = "hwtest_images"
    public_url = upload_to_gcs(bucket_name, output_path, destination_blob_name)

    return jsonify({"message": f"Image processed and uploaded to {bucket_name}/{destination_blob_name}", "public_url": public_url}), 200

@app.route('/resize_image', methods=['GET'])
def resize_image_endpoint():
    bucket_name = request.args.get('bucket')
    image_name = request.args.get('image')
    width = request.args.get('width')
    height = request.args.get('height')

    if not bucket_name or not image_name:
        return jsonify({"error": "bucket and image parameters are required"}), 400

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_name)
    image_data = blob.download_as_bytes()

    img = Image.open(BytesIO(image_data))

    if width and height:
        try:
            width = int(width)
            height = int(height)
            img = resize_image(img, (width, height))
        except ValueError:
            return jsonify({"error": "width and height must be integers"}), 400

    
    img = img.convert("RGB")

    output = BytesIO()
    img.save(output, format='JPEG')
    output.seek(0)

    return send_file(output, mimetype='image/jpeg')

@app.route('/image/upload/f_auto,q_auto/hw/flags/<image_name>', methods=['GET'])
def redirect_resize(image_name):
    bucket_name = "hwtest_images"
    
    
    return redirect(url_for('resize_image_endpoint', bucket=bucket_name, image=image_name))

if __name__ == '__main__':
    app.run(debug=True)
