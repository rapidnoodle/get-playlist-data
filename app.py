from utils.download_playlist_data import download_playlist_data
from utils.download_song_files import download_song_files
from utils.force_convert import response_received
from dotenv import load_dotenv
import pychrome
import time
import os

load_dotenv()

PLAYLIST_ID = os.getenv("PLAYLIST_ID")
TOKEN = os.getenv("TOKEN")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

PRE = "https://open.spotify.com/track/"

browser = pychrome.Browser(url="http://localhost:8000")
tab = browser.list_tab()[0]
tab.start()

tab.Network.enable()
tab.Network.responseReceived = response_received

playlist_data = download_playlist_data(PLAYLIST_ID, TOKEN, OUTPUT_DIR)

download_song_files(playlist_data, OUTPUT_DIR)

tab.stop()

print("Process: Task Completed")

while True:
    time.sleep(1)
