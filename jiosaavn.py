import requests
import endpoints
import helper
import json
from traceback import print_exc
import re
import logging

logger = logging.getLogger(__name__)


def search_for_song(query, lyrics, songdata):
    try:
        if query.startswith('http') and 'saavn.com' in query:
            id = get_song_id(query)
            return get_song(id, lyrics)

        search_base_url = endpoints.search_base_url+query
        logger.info(f"Making request to: {search_base_url}")
        response = requests.get(search_base_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        response_text = response.text.encode().decode('unicode-escape')
        pattern = r'\(From "([^"]+)"\)'
        response_data = json.loads(re.sub(pattern, r"(From '\1')", response_text))
        
        if 'songs' not in response_data or 'data' not in response_data['songs']:
            logger.error(f"Unexpected response format: {response_data}")
            return None
            
        song_response = response_data['songs']['data']
        if not songdata:
            return song_response
            
        songs = []
        for song in song_response:
            id = song['id']
            song_data = get_song(id, lyrics)
            if song_data:
                songs.append(song_data)
        return songs
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in search_for_song: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in search_for_song: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in search_for_song: {str(e)}")
        return None


def get_song(id, lyrics):
    try:
        song_details_base_url = endpoints.song_details_base_url+id
        logger.info(f"Making request to: {song_details_base_url}")
        response = requests.get(song_details_base_url, timeout=10)
        response.raise_for_status()
        
        response_text = response.text.encode().decode('unicode-escape')
        song_response = json.loads(response_text)
        
        if id not in song_response:
            logger.error(f"Song ID {id} not found in response")
            return None
            
        song_data = helper.format_song(song_response[id], lyrics)
        return song_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in get_song: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in get_song: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_song: {str(e)}")
        return None


def get_song_id(url):
    res = requests.get(url, data=[('bitrate', '320')])
    try:
        return(res.text.split('"pid":"'))[1].split('","')[0]
    except IndexError:
        return res.text.split('"song":{"type":"')[1].split('","image":')[0].split('"id":"')[-1]


def get_album(album_id, lyrics):
    songs_json = []
    try:
        response = requests.get(endpoints.album_details_base_url+album_id)
        if response.status_code == 200:
            songs_json = response.text.encode().decode('unicode-escape')
            songs_json = json.loads(songs_json)
            return helper.format_album(songs_json, lyrics)
    except Exception as e:
        print(e)
        return None


def get_album_id(input_url):
    res = requests.get(input_url)
    try:
        return res.text.split('"album_id":"')[1].split('"')[0]
    except IndexError:
        return res.text.split('"page_id","')[1].split('","')[0]


def get_playlist(listId, lyrics):
    try:
        response = requests.get(endpoints.playlist_details_base_url+listId)
        if response.status_code == 200:
            songs_json = response.text.encode().decode('unicode-escape')
            songs_json = json.loads(songs_json)
            return helper.format_playlist(songs_json, lyrics)
        return None
    except Exception:
        print_exc()
        return None


def get_playlist_id(input_url):
    res = requests.get(input_url).text
    try:
        return res.split('"type":"playlist","id":"')[1].split('"')[0]
    except IndexError:
        return res.split('"page_id","')[1].split('","')[0]


def get_lyrics(id):
    url = endpoints.lyrics_base_url+id
    lyrics_json = requests.get(url).text
    lyrics_text = json.loads(lyrics_json)
    return lyrics_text['lyrics']
