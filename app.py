# from flask import Flask, render_template, request, redirect, url_for, flash
# import requests
# import time
# import os
# from dotenv import load_dotenv

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# load_dotenv()
# api_key = os.getenv('NARAKEET_API_KEY')

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'zip_file' not in request.files:
#         flash('No file part')
#         return redirect(url_for('index'))

#     zip_file = request.files['zip_file']
    
#     if zip_file.filename == '':
#         flash('No selected file')
#         return redirect(url_for('index'))

#     if zip_file:
#         zip_file_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_file.filename)
#         zip_file.save(zip_file_path)
        
#         try:
#             video_url = process_video(zip_file_path)
#             return redirect(url_for('download', video_url=video_url))
#         except Exception as e:
#             flash(str(e))
#             return redirect(url_for('index'))

# @app.route('/download')
# def download():
#     video_url = request.args.get('video_url')
#     if not video_url:
#         flash('No video URL provided')
#         return redirect(url_for('index'))
#     return render_template('download.html', video_url=video_url)

# def process_video(zip_file_path):
#     # Step 1: Obtain upload token
#     upload_token_url = 'https://api.narakeet.com/video/upload-request/zip'
#     headers = {'x-api-key': api_key}
#     upload_token_response = requests.get(upload_token_url, headers=headers)
#     upload_token_data = upload_token_response.json()

#     if 'repository' not in upload_token_data:
#         raise Exception('Repository key not found in upload token response')

#     repository = upload_token_data['repository']
#     repository_type = upload_token_data['repositoryType']
#     upload_url = upload_token_data['url']
#     content_type = upload_token_data['contentType']

#     # Step 2: Upload the ZIP file
#     file_size = os.path.getsize(zip_file_path)
#     with open(zip_file_path, 'rb') as file:
#         upload_response = requests.put(upload_url, headers={
#             'Content-Type': content_type,
#             'Content-Length': str(file_size),
#         }, data=file)

#     if upload_response.status_code != 200:
#         raise Exception('Error uploading the file:', upload_response.text)

#     # Step 3: Trigger the build request
#     build_url = 'https://api.narakeet.com/video/build'
#     build_data = {
#         'repositoryType': repository_type,
#         'repository': repository,
#         'source': 'source.md'
#     }
#     build_response = requests.post(build_url, headers={
#         'Content-Type': 'application/json',
#         'x-api-key': api_key,
#     }, json=build_data)
#     build_data = build_response.json()

#     if 'statusUrl' not in build_data:
#         raise Exception('Status URL not found in build response')

#     status_url = build_data['statusUrl']

#     # Step 4: Poll for results
#     video_url = None
#     while not video_url:
#         status_response = requests.get(status_url)
#         status_data = status_response.json()

#         if status_data.get('finished'):
#             if status_data.get('succeeded'):
#                 video_url = status_data.get('result')
#             else:
#                 raise Exception('Error generating video:', status_data.get('message'))
#         else:
#             time.sleep(5)

#     return video_url

# if __name__ == '__main__':
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
import os
import requests
import time
import zipfile
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

load_dotenv()
api_key = os.getenv('NARAKEET_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'image_{i}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

def create_zip(file_paths, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))

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

@app.route('/upload-files', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        text_file = request.files.get('text_file')

        if not (pdf_file and allowed_file(pdf_file.filename) and text_file and allowed_file(text_file.filename)):
            flash('Invalid file format or missing files')
            return redirect(url_for('upload_files'))

        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(pdf_file.filename))
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(text_file.filename))
        pdf_file.save(pdf_path)
        text_file.save(text_path)

        # Convert PDF to images
        image_paths = convert_pdf_to_images(pdf_path)

        # Create ZIP file
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'files.zip')
        create_zip(image_paths + [text_path], zip_path)

        try:
            video_url = process_video(zip_path)
            return redirect(url_for('download', video_url=video_url))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('upload_files'))

    return render_template('upload_files.html')

@app.route('/download')
def download():
    video_url = request.args.get('video_url')
    if not video_url:
        flash('No video URL provided')
        return redirect(url_for('index'))
    return render_template('download.html', video_url=video_url)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
