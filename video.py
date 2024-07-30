import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv('NARAKEET_API_KEY')
zip_file_path = 'Script.zip'

# Step 1: Obtain upload token
upload_token_url = 'https://api.narakeet.com/video/upload-request/zip'
headers = {
    'x-api-key': api_key,
}
upload_token_response = requests.get(upload_token_url, headers=headers)

# Print the entire response for debugging
print('Upload Token Response Status Code:', upload_token_response.status_code)
print('Upload Token Response JSON:', upload_token_response.json())

upload_token_data = upload_token_response.json()

# Check the keys in the response
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
print('Upload Response Status Code:', upload_response.status_code)

# Check if the upload was successful
if upload_response.status_code != 200:
    raise Exception('Error uploading the file:', upload_response.text)

# Step 3: Trigger the build request
build_url = 'https://api.narakeet.com/video/build'
build_data = {
    'repositoryType': repository_type,
    'repository': repository,
    'source': 'source.md'  # Update with the path to your script inside the ZIP
}
build_response = requests.post(build_url, headers={
    'Content-Type': 'application/json',
    'x-api-key': api_key,
}, json=build_data)
build_data = build_response.json()

print('Build Response Status Code:', build_response.status_code)
print('Build Response JSON:', build_data)

# Check if the statusUrl is present
if 'statusUrl' not in build_data:
    raise Exception('Status URL not found in build response')

status_url = build_data['statusUrl']

# Step 4: Poll for results
video_url = None
while not video_url:
    status_response = requests.get(status_url)
    status_data = status_response.json()
    
    print('Status Response JSON:', status_data)  # Debugging output
    
    if status_data.get('finished'):
        if status_data.get('succeeded'):
            video_url = status_data.get('result')
        else:
            raise Exception('Error generating video:', status_data.get('message'))
    else:
        time.sleep(5)  # Wait before checking again

# Step 5: Download the video
video_response = requests.get(video_url)
if video_response.status_code == 200:
    output_file_path = 'script.mp4'
    with open(output_file_path, 'wb') as video_file:
        video_file.write(video_response.content)
    print(f'Video downloaded as {output_file_path}')
else:
    raise Exception('Error downloading the video:', video_response.text)
