from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import time
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()
api_key = os.getenv('NARAKEET_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'zip_file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    zip_file = request.files['zip_file']
    
    if zip_file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if zip_file:
        zip_file_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_file.filename)
        zip_file.save(zip_file_path)
        
        try:
            video_url = process_video(zip_file_path)
            return redirect(url_for('download', video_url=video_url))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))

@app.route('/download')
def download():
    video_url = request.args.get('video_url')
    if not video_url:
        flash('No video URL provided')
        return redirect(url_for('index'))
    return render_template('download.html', video_url=video_url)

def process_video(zip_file_path):
    # Step 1: Obtain upload token
    upload_token_url = 'https://api.narakeet.com/video/upload-request/zip'
    headers = {'x-api-key': api_key}
    upload_token_response = requests.get(upload_token_url, headers=headers)
    upload_token_data = upload_token_response.json()

    if 'repository' not in upload_token_data:
        raise Exception('Repository key not found in upload token response')

    repository = upload_token_data['repository']
    repository_type = upload_token_data['repositoryType']
    upload_url = upload_token_data['url']
    content_type = upload_token_data['contentType']

    # Step 2: Upload the ZIP file
    file_size = os.path.getsize(zip_file_path)
    with open(zip_file_path, 'rb') as file:
        upload_response = requests.put(upload_url, headers={
            'Content-Type': content_type,
            'Content-Length': str(file_size),
        }, data=file)

    if upload_response.status_code != 200:
        raise Exception('Error uploading the file:', upload_response.text)

    # Step 3: Trigger the build request
    build_url = 'https://api.narakeet.com/video/build'
    build_data = {
        'repositoryType': repository_type,
        'repository': repository,
        'source': 'source.md'
    }
    build_response = requests.post(build_url, headers={
        'Content-Type': 'application/json',
        'x-api-key': api_key,
    }, json=build_data)
    build_data = build_response.json()

    if 'statusUrl' not in build_data:
        raise Exception('Status URL not found in build response')

    status_url = build_data['statusUrl']

    # Step 4: Poll for results
    video_url = None
    while not video_url:
        status_response = requests.get(status_url)
        status_data = status_response.json()

        if status_data.get('finished'):
            if status_data.get('succeeded'):
                video_url = status_data.get('result')
            else:
                raise Exception('Error generating video:', status_data.get('message'))
        else:
            time.sleep(5)

    return video_url

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

