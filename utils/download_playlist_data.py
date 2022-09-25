from utils.song_to_url import song_to_url
import requests
import json
import os


def get_track_data(track):
    data = track["track"]
    obj = {
        "id": data["id"],
        "name": data["name"],
        "artists": [artist["name"] for artist in data["artists"]]
    }

    obj["soundLoadersUrl"] = song_to_url(obj["artists"], obj["name"])

    return obj


def get_playlist_data(playlist_id, token):
    playlist_data = {
        "playlistId": playlist_id,
        "songs": []
    }

    print(f"Process: Retrieving playlist data from {playlist_id}...")

    data = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers={"Authorization": f"Bearer {token}"}).json()

    if "items" not in data:
        raise Exception("Critical Error: Please reset your Spotify API token")

    items = data["items"]

    print(f"Success: Retrieved playlist data from {playlist_id}")

    playlist_data["songs"] = [get_track_data(track) for track in items]
    return playlist_data


def download_playlist_data(playlist_id, token, output_dir):
    playlist_data = get_playlist_data(playlist_id, token)

    print(f"Process: Writing playlist data from {playlist_id} to file...")

    dir = f"{output_dir}/playlist-{playlist_id}"
    if not os.path.exists(dir):
        os.mkdir(dir)

    with open(f"{dir}/metadata.json", "w") as file:
        json.dump(playlist_data, file)

    print(f"Success: Playlist data from {playlist_id} written")

    return playlist_data
