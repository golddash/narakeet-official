# Flask Video Processing Application

This Flask application allows users to upload ZIP files containing video assets, which are then processed to generate a video using the Narakeet API. Once the video is generated, a download link is provided.

## Features

- Upload ZIP files containing video assets.
- Process the uploaded ZIP files using the Narakeet API.
- Provide a download link for the generated video.

## Requirements

- Python 3.x
- Flask
- Requests
- python-dotenv

You can install the required Python packages using:

```bash
pip install -r requirements.txt
```

Create a .env file in the root directory with the following content:

```bash
NARAKEET_API_KEY=your_api_key_here
```
## Running the Application

Create the 'uploads' directory if it doesn't exist:

```bash
mkdir -p uploads
```

Run the Flask application:

```bash
python app.py
```

or

```bash
python3 app.py
```

The application will be accessible at 'http://127.0.0.1:5000/'.

