import os
import logging
import random
import tweepy
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

settings = {
            "client_config_backend": "service",
                "service_config": {
                    "client_json_file_path": "credentials.json",
                }
            }
# PyDrive authentication
gauth = GoogleAuth(settings=settings)
gauth.ServiceAuth()
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

root_folder_name = os.getenv('ROOT_FOLDER_NAME')

def get_root_folder_id():
    folder_list = drive.ListFile({'q': "title = '" + root_folder_name + "' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"}).GetList()

    if not folder_list:
        logger.error('Screenshots folder not found')
        return None
    
    return folder_list[0]['id']

def get_random_image_from_drive(root_folder_id):
    subfolders = drive.ListFile({'q': f"'{root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    
    if not subfolders:
        logger.error('No subfolders found in the '+ root_folder_name + ' folder')
        return None, None
    
    #Random subfolder
    random_subfolder = random.choice(subfolders)
    subfolder_id = random_subfolder['id']
    subfolder_name = random_subfolder['title']
    
    # List all images in the selected subfolder
    images = drive.ListFile({'q': f"'{subfolder_id}' in parents and trashed=false"}).GetList()
    
    if not images:
        logger.error(f'No images found in subfolder: {subfolder_name}')
        return None, None
    
    #Random Img
    random_image = random.choice(images)
    image_id = random_image['id']
    
    return image_id, subfolder_name

def download_image_from_drive(file_id, destination):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(destination)
    logger.info(f'Image {file_id} downloaded to {destination}')

def tweet_image():
    root_folder_id = get_root_folder_id()
    if not root_folder_id:
        return

    image_id, subfolder_name = get_random_image_from_drive(root_folder_id)
    if not image_id or not subfolder_name:
        return
    
    local_image_path = './temp_image.jpg'
    try:
        download_image_from_drive(image_id, local_image_path)
        logger.info('Image downloaded')

        media = api.media_upload(local_image_path)
        logger.info('Image uploaded to Twitter')

        client.create_tweet(text=subfolder_name, media_ids=[media.media_id_string])
        logger.info('Tweet created')

        os.remove(local_image_path)
        logger.info('Local image file removed')

    except Exception as e:
        logger.error(f'Failed to tweet: {e}')

def main():
    while True:
        now = datetime.utcnow()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        sleep_time = (next_hour - now).total_seconds()

        logger.info(f'Current time: {now}, sleeping for {sleep_time} seconds until next hour.')

        time.sleep(sleep_time)

        tweet_image()

if __name__ == "__main__":
    main()