import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from cred import *
import csv
import numpy as np
import pandas as pd
import os
from requests.exceptions import ReadTimeout

# current directory
curr_dir = os.getcwd()

# file path to training_data.npz
file = os.path.join(curr_dir, "data.csv")

# authentication without users
client_credentials_manager = SpotifyClientCredentials(client_id = CID, client_secret = SECRET)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager, requests_timeout=10, retries=10)

# alter playlist_link appropriately (Spotify --> playlist --> share --> copy link to playlist)
playlist_link = "https://open.spotify.com/playlist/4Dg0J0ICj9kKTGDyFu0Cv4?si=1a615d379fef48d9"
# extracting URI from playlist_link
playlist_URI = playlist_link.split("/")[-1].split("?")[0]

def get_playlist_tracks(playlist_URI):
    """ writes spotipy data into data.csv file in current directory

    Args: 
        playlist_URI: (string) URI of the playlist

    Returns: 
        tracks: pagenated songs from the playlist (if playlist contains more than 100 songs)

    """

    results = sp.playlist_tracks(playlist_URI)
    tracks = results['items']

    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    return tracks

def writeFile(track_name, track_audio_features, track_popularity):
    """ writes spotipy data into data.csv file in current directory

    Args: 
        track_name: (string) title of song
        track_audio_features: (JSON object or dictionary) audio features of the song
        track_popularity: (int) popularity of the song (calculated by Spotify) (should potentially switch this with playcount)

    Returns: None
        turns {"title":___ , "danceability": ___ ...(essential audio features of the song)... , "popularity": ___} 
        into pd.dataframe object, then stores it inside data.csv file

    """

    essential_features = {"danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness", 
            "liveness", "valence", "tempo", "duration_ms", "time_signature"}
    
    # extract essential features
    essential_track_audio_features = {k: track_audio_features[k] for k in track_audio_features.keys() & essential_features}

    # add track_name and track_popularity
    essential_track_audio_features["title"] = track_name
    essential_track_audio_features["popularity"] = track_popularity

    # write headers to data.csv
    if not os.path.exists(file):
        header = essential_track_audio_features.keys()

        with open('data.csv', 'w', encoding = 'UTF8', newline = "") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    
    # non-header data
    non_header_data = essential_track_audio_features.values()

    # write rest of data
    with open('data.csv', "a", encoding = "UTF8", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(non_header_data)


def checkFile():
    """ checks if training_data.csv file exists in directory and removes it if it does

    Args: None

    Returns: None
        deletes "data.csv" if it exists so that data_scraper.py doesn't write to previous file when re-ran

    """

    if os.path.exists(file):  # if data.csv already exists 
        # delete previous data.csv
        os.remove(file)
        print("... Outputting new data.csv ...")

if __name__ == "__main__":
    # check if data.csv already exists from last run, delete and rewrite if true
    checkFile()
    
    # obtaining actual playlist via spotipy
    playlist_tracks = get_playlist_tracks(playlist_URI)
    
    # iterate through track_uri
    for track in playlist_tracks:
        # track_uri = uri of curr track
        track_uri = track["track"]["uri"]
        # track name
        track_name = track["track"]["name"]
        # track popularity (spotipy doesn't offer a method for play count)
        track_popularity = track["track"]["popularity"]
        
        # sometimes Spotify throws a ReadTimeOut error and socket runs out of time
        try:
            # track popularity (spotipy doesn't offer a method for play count)
            # track_audio_analysis = sp.audio_analysis(track_uri)
            # track audio features
            track_audio_features = sp.audio_features(track_uri)[0]
        except ReadTimeout:
            print("Spotify timed out ... trying again ..." + "\n")
            # track audio analysis
            # track_audio_analysis = sp.audio_analysis(track_uri)
            # track audio features
            track_audio_features = sp.audio_features(track_uri)[0]
        
        # writeFile(track_audio_analysis, track_audio_features)
        writeFile(track_name, track_audio_features, track_popularity)

    print("Done writing to data.csv!")