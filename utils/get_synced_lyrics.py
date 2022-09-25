import urllib.request
import urllib.error
import urllib.parse
import unicodedata
import threading
import time
import json
import math
import os
import re


class Musixmatch:
    base_url = "https://apic-desktop.musixmatch.com/ws/1.1/macro.subtitles.get?format=json&namespace=lyrics_richsynched&subtitle_format=mxm&app_id=web-desktop-app-v1.0&"
    headers = {"authority": "apic-desktop.musixmatch.com",
               "cookie": "x-mxm-token-guid="}

    def __init__(self, token=None):
        self.set_token(token)

    def set_token(self, token):
        self.token = token

    def find_lyrics(self, song):
        durr = song.duration / 1000 if song.duration else ""
        params = {
            "q_album": " ",
            "q_artist": " ",
            "q_artists": " ",
            "q_track": " ",
            "track_spotify_id": song.uri,
            "q_duration": durr,
            "f_subtitle_length": math.floor(durr) if durr else "",
            "usertoken": self.token,
        }

        req = urllib.request.Request(self.base_url + urllib.parse.urlencode(
            params, quote_via=urllib.parse.quote), headers=self.headers)
        try:
            response = urllib.request.urlopen(req).read()
        except (urllib.error.HTTPError, urllib.error.URLError, ConnectionResetError) as e:
            print(f"Error: {repr(e)}")
            return

        r = json.loads(response.decode())
        if r['message']['header']['status_code'] != 200 and r['message']['header'].get('hint') == 'renew':
            print("Error: Invalid Musixmatch token")
            return
        body = r["message"]["body"]["macro_calls"]

        if body["matcher.track.get"]["message"]["header"]["status_code"] != 200:
            if body["matcher.track.get"]["message"]["header"]["status_code"] == 404:
                print("Error: Lyrics not found on Musixmatch")
            elif body["matcher.track.get"]["message"]["header"]["status_code"] == 401:
                print(
                    "Error: Too many requests to Musixmatch; increase request cooldown")
            else:
                print(
                    f"Error: {body['matcher.track.get']['message']['header']}")
            return
        elif isinstance(body["track.lyrics.get"]["message"].get("body"), dict):
            if body["track.lyrics.get"]["message"]["body"]["lyrics"]["restricted"]:
                print("Error: Musixmatch lyrics restricted")
                return
        return body

    @staticmethod
    def get_unsynced(song, body):
        if song.is_instrumental:
            lines = [{"text": "♪ Instrumental ♪",
                      "minutes": 0, "seconds": 0, "hundredths": 0}]
        elif song.has_unsynced:
            lyrics_body = body["track.lyrics.get"]["message"].get("body")
            if lyrics_body is None:
                return False
            lyrics = lyrics_body["lyrics"]["lyrics_body"]
            if lyrics:
                lines = [{"text": line, "minutes": 0, "seconds": 0, "hundredths": 0}
                         for line in list(filter(None, lyrics.split('\n')))]
            else:
                lines = [{"text": "", "minutes": 0,
                          "seconds": 0, "hundredths": 0}]
        else:
            lines = None
        song.lyrics = lines
        return True

    @staticmethod
    def get_synced(song, body):
        if song.is_instrumental:
            lines = [{"text": "♪ Instrumental ♪",
                      "minutes": 0, "seconds": 0, "hundredths": 0}]
        elif song.has_synced:
            subtitle_body = body["track.subtitles.get"]["message"].get("body")
            if subtitle_body is None:
                return False
            subtitle = subtitle_body["subtitle_list"][0]["subtitle"]
            if subtitle:
                lines = [{"text": line["text"] or "♪", "minutes": line["time"]["minutes"], "seconds": line["time"]
                          ["seconds"], "hundredths": line["time"]["hundredths"]} for line in json.loads(subtitle["subtitle_body"])]
            else:
                lines = [{"text": "", "minutes": 0,
                          "seconds": 0, "hundredths": 0}]
        else:
            lines = None
        song.subtitles = lines
        return True

    @staticmethod
    def gen_lrc(song, outdir='', filename=''):
        lyrics = song.subtitles
        if lyrics is None:
            print(
                f"Error: Synced lyrics not found on Musixmatch for {song.title}")
            lyrics = song.lyrics
            if lyrics is None:
                print(
                    f"Error: Unsynced lyrics not found on Musixmatch for {song.title}")
                return False
        print(f"Process: Formatting lyrics for {song.title}...")
        tags = [
            "[by:fashni]\n",
            f"[ar:{song.artist}]\n",
            f"[ti:{song.title}]\n",
        ]
        if song.album:
            tags.append(f"[al:{song.album}]\n")
        if song.duration:
            tags.append(
                f"[length:{int((song.duration/1000)//60):02d}:{int((song.duration/1000)%60):02d}]\n")

        lrc = [f"[{line['minutes']:02d}:{line['seconds']:02d}.{line['hundredths']:02d}]{line['text']}\n" for line in lyrics]
        lines = tags + lrc

        fn = filename or slugify(f"{song}")
        filepath = os.path.join(outdir, fn) + ".lrc"
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Success: Lyrics saved for {song} to {filepath}")
        return True


class Song(object):
    def __init__(self, uri, artist="", title="", album=""):
        self.artist = artist
        self.title = title
        self.album = album
        self.uri = uri
        self.duration = 0
        self.has_synced = False
        self.has_unsynced = False
        self.is_instrumental = False
        self.lyrics = None
        self.subtitles = None
        self.coverart_url = None

    def __str__(self) -> str:
        return self.uri

    @property
    def info(self):
        return self.__dict__

    def update_info(self, body):
        meta = body["matcher.track.get"]["message"]["body"]
        if not meta:
            return
        coverart_sizes = ["100x100", "350x350", "500x500", "800x800"]
        coverart_urls = list(filter(
            None, [meta["track"][f"album_coverart_{size}"] for size in coverart_sizes]))
        self.coverart_url = coverart_urls[-1] if coverart_urls else None
        self.title = meta["track"]["track_name"]
        self.artist = meta["track"]["artist_name"]
        self.album = meta["track"]["album_name"]
        self.duration = meta["track"]["track_length"] * 1000
        self.has_synced = meta["track"]["has_subtitles"]
        # or meta["track"]["has_lyrics_crowd"]
        self.has_unsynced = meta["track"]["has_lyrics"]
        self.is_instrumental = meta["track"]["instrumental"]


# https://github.com/django/django/blob/main/django/utils/text.py
def slugify(value):
    value = str(value)
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s()'-]", "", value)
    return re.sub(r"[-]+", "-", value).strip("-_")


def get_lrc(mx, song, outdir, fn='lyrics'):
    print(f"Process: Searching song {song}")
    body = mx.find_lyrics(song)
    if body is None:
        return False
    song.update_info(body)
    print(f"Success: Song {song} found")
    print(f"Process: Searching lyrics for {song}")
    mx.get_synced(song, body)
    mx.get_unsynced(song, body)
    status = mx.gen_lrc(song, outdir=outdir, filename=fn)
    return status


def get_lyrics_by_id(id, outdir):
    global queued_ids
    global cooldown
    if cooldown:
        return
    cooldown = True

    run_time = time.strftime("%Y%m%d_%H%M%S")
    MX_TOKEN = "2203269256ff7abcb649269df00e14c833dbf4ddfb5b36a1aae8b0"
    mx = Musixmatch(MX_TOKEN)
    PREF = "https://open.spotify.com/track/"

    failed = False
    try:
        success = get_lrc(mx, Song(id), outdir)
        if not success:
            failed = True

        print("Process: Starting cooldown for Musixmatch token (30)...")
        time.sleep(30)
    except KeyboardInterrupt as e:
        print(f"Error: {repr(e)}")

    if failed:
        print(f"Error: Failed to fetch lyrics for {id}")
    else:
        print(f"Success: Fetched lyrics from {id}")

    cooldown = False


def add_id_to_queue(id, outdir):
    bundle = (id, outdir)
    global queued_ids
    if bundle in queued_ids:
        return
    queued_ids.append(bundle)


def check_queue():
    while True:
        time.sleep(1)
        while len(queued_ids) > 0:
            get_lyrics_by_id(queued_ids[0][0], queued_ids[0][1])
            while cooldown:
                time.sleep(1)
            queued_ids.pop(0)


queued_ids = []
cooldown = False
check = threading.Thread(name="check", target=check_queue)
