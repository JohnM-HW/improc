# improc
Test Image processor that can replace cloudinary



# Image Processing API

This Flask application provides endpoints for processing images, including resizing, sharpening, converting to grayscale, rotating, blurring, adding watermarks, and converting to WebP format. The processed images are uploaded to a Google Cloud Storage bucket and made publicly accessible.

## Features

- Resize images
- Sharpen images
- Convert images to grayscale
- Rotate images
- Blur images
- Add watermarks to images
- Convert images to WebP format
- Upload processed images to Google Cloud Storage
- Redirect and resize images via URL parameters

## Prerequisites

- Python 3.6 or higher
- Google Cloud SDK
- Google Cloud Storage bucket
- Google Cloud Vision API enabled

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment:
   ```python -m venv venv
    source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up Google Cloud credentialst:
   ```
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"

   ```

## Usage
1. Run the Flask application:
    ```
    python app.py
    ````

2. Use the following endpoints to process images:

### Process Image
**Endpoint:** /process_image
**Method:** POST
**Description:** Processes an image from a URL and uploads it to Google Cloud Storage.
**Request Body:**
```
{
  "image_url": "https://example.com/image.jpg",
  "size": [800, 600],
  "sharpen": false,
  "grayscale": false,
  "rotate": null,
  "blur": null,
  "watermark_text": "Sample Watermark",
  "watermark_position": [50, 50],
  "watermark_opacity": 128,
  "watermark_font_size": 36,
  "convert_to_webp": false
}
```

