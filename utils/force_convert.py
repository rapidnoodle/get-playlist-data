from utils.wait_until_located import wait_until_located
from selenium.webdriver.common.by import By
from utils import driver
import time


downloaded = False


def response_received(**kwargs):
    response = kwargs.get("response")
    url = response.get("url")

    if "https://api.soundloaders.com/files/" in url:
        global downloaded
        downloaded = True


def force_convert(id):
    driver.get("https://www.soundloaders.com/spotify-downloader/")

    uriInput = wait_until_located(
        By.CLASS_NAME, "DownloaderTrackPage_Input__ZTfhW")
    submit = wait_until_located(
        By.CLASS_NAME, "DownloaderTrackPage_Button__C_Hd5")

    uriInput.send_keys(f"https://open.spotify.com/track/{id}")
    submit.click()

    parent_div = "//div[@class=\"DownloaderTrackPage_Result__w54Ap\"]"

    download = wait_until_located(
        By.XPATH, parent_div + "/button[@class=\"Button_Button__qiii_\"]")
    download.click()

    global downloaded

    while not downloaded:
        time.sleep(1)

    time.sleep(4)

    another = wait_until_located(
        By.XPATH, parent_div + "/button[@class=\"DownloaderTrackPage_DownloadAnother__8uu0Y\"]")
    another.click()

    downloaded = False
