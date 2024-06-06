import os
import logging
import random
import tweepy
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# PyDrive authentication
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env
load_dotenv()

# API creds
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

client = tweepy.Client(BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Authentication
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Interval and debug
INTERVAL = 5
debug = 1

def get_root_folder_id():
    folder_list = drive.ListFile({'q': "title = 'Screenshots' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"}).GetList()
    if not folder_list:
        logger.error('Screenshots folder not found')
        return None
    
    return folder_list[0]['id']

def get_random_image_from_drive(root_folder_id):
    # List all subfolders in the "Screenshots" folder
    subfolders = drive.ListFile({'q': f"'{root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    
    if not subfolders:
        logger.error('No subfolders found in the Screenshots folder')
        return None, None
    
    # Select a random subfolder
    random_subfolder = random.choice(subfolders)
    subfolder_id = random_subfolder['id']
    subfolder_name = random_subfolder['title']
    
    # List all images in the selected subfolder
    images = drive.ListFile({'q': f"'{subfolder_id}' in parents and trashed=false"}).GetList()
    
    if not images:
        logger.error(f'No images found in subfolder: {subfolder_name}')
        return None, None
    
    # Select a random image
    random_image = random.choice(images)
    image_id = random_image['id']
    
    return image_id, subfolder_name

def download_image_from_drive(file_id, destination):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(destination)
    logger.info(f'Image {file_id} downloaded to {destination}')

def main():
    root_folder_id = get_root_folder_id()
    if not root_folder_id:
        return

    while True:
        cur_time = datetime.utcnow() + timedelta(hours=1)
        logger.info(f'Tweeting at {cur_time.time()}')
        
        image_id, subfolder_name = get_random_image_from_drive(root_folder_id)
        if not image_id or not subfolder_name:
            time.sleep(INTERVAL)
            continue
        
        local_image_path = './temp_image.jpg'
        try:
            # Download the random image from Google Drive
            download_image_from_drive(image_id, local_image_path)
            logger.info('Image downloaded')

            # Upload the image to Twitter
            media = api.media_upload(local_image_path)
            logger.info('Image uploaded to Twitter')

            # Create the tweet with the image and subfolder name as the caption
            client.create_tweet(text=subfolder_name, media_ids=[media.media_id_string])
            logger.info('Tweet created')

            # Remove the local image file
            os.remove(local_image_path)
            logger.info('Local image file removed')

        except Exception as e:
            logger.error(f'Failed to tweet: {e}')

        # Wait for the specified interval before the next tweet
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()