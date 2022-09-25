from utils.get_synced_lyrics import check, add_id_to_queue
from utils.force_convert import force_convert
import requests
import os


def download_song_files(playlist_data, output_dir):
    check.start()
    for song in playlist_data["songs"]:
        song_dir = f"{output_dir}/playlist-{playlist_data['playlistId']}/song-{song['id']}"
        if not os.path.exists(song_dir):
            os.mkdir(song_dir)

        add_id_to_queue(song["id"], song_dir)

        while True:
            res = requests.get(song["soundLoadersUrl"], headers={
                "Content-Type": "audio/mpeg"})
            if res.status_code >= 400:
                print(f"Error: Cannot GET {song['name']} mp3 data")
                print(f"Process: Running ForceConvert on {song['name']}...")

                force_convert(song["id"])
                continue
            break

        print(f"Success: Retrieved mp3 data from {song['name']}")
        print(f"Process: Writing {song['name']} mp3 data to file...")

        with open(f"{song_dir}/audio.mp3", "wb") as audio:
            audio.write(res.content)

        print(f"Success: {song['name']} mp3 data written")
    check.join()
