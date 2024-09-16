# Random Image Twitter Bot

A python script that automates the process of posting random images on twitter every hour. The python script retrieves the image from a random subfolder in the root folder specified in google drive, saves the subfolders name and uses it as the caption to post the tweet. It uses the following technologies:

* **Tweepy** for interacting with Twitter API.
* **PyDrive** for accessing and downloading images from Google Drive.
* **OAuth** for authentication and token management.

## Features
* Authenticates with Twitter and Google Drive using OAuth.
* Periodically generates and posts a randomly selected image from Google Drive to Twitter.
* Automatically refreshes Google Drive tokens if they are close to expiring.

## Requirements
The requirements are very light and you can get started by keeping this script running 24/7 and the following:

* Twitter Developer account and API keys.
* Google Developer account with a Google Drive API setup.
* A .env file containing environment variables for API keys and folder names.

## Setup