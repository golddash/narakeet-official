# Narakeet Video Generator

This project is a Flask-based web application that allows users to upload PDF and text files, convert the PDF into images, zip the images with the text file, and then create a video using the Narakeet API. The application also provides a download link for the generated video.

## Features

- **Upload Files**: Users can upload a PDF and a text file.
- **PDF to Image Conversion**: The PDF is converted into individual images.
- **ZIP Creation**: The images and text file are compressed into a ZIP file.
- **Video Generation**: The ZIP file is uploaded to Narakeet to generate a video.
- **Download Link**: Users receive a link to download the generated video.

## Requirements

- Python 3.x
- Flask
- Requests
- Python-dotenv
- pdf2image
- Werkzeug

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/narakeet-video-generator.git
    cd narakeet-video-generator
    ```

2. **Create a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the project root and add your Narakeet API key:

    ```bash
    NARAKEET_API_KEY=your_narakeet_api_key
    ```

5. **Run the application:**

    ```bash
    python app.py
    ```

6. **Navigate to the application:**

    Open your web browser and go to `http://127.0.0.1:5000/`.

## Usage

### Uploading Files

- On the homepage, upload a PDF file and a text file.
- The application converts the PDF to images, creates a ZIP file with the images and the text file, and sends it to the Narakeet API.
- After processing, you will be redirected to a page with a download link for the generated video.

### Error Handling

- The application provides feedback if the uploaded files are in an invalid format or if there is an error during the video generation process.

## Project Structure

