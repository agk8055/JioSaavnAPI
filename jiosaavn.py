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


def get_multiple_songs(song_ids, lyrics):
    """
    Fetch multiple songs in a single API request for better performance.
    
    Args:
        song_ids (list): List of song IDs to fetch
        lyrics (bool): Whether to include lyrics in the response
    
    Returns:
        dict: Response with status and songs data
    """
    try:
        if not song_ids:
            return {
                "status": False,
                "error": "No song IDs provided"
            }
        
        # Join song IDs with comma for the API request
        ids_param = ','.join(song_ids)
        song_details_base_url = endpoints.song_details_base_url + ids_param
        
        # Adjust timeout based on number of songs
        base_timeout = 15
        timeout_per_song = 0.5  # Additional seconds per song
        dynamic_timeout = base_timeout + (len(song_ids) * timeout_per_song)
        dynamic_timeout = min(dynamic_timeout, 60)  # Cap at 60 seconds
        
        logger.info(f"Making request to: {song_details_base_url}")
        logger.info(f"Requesting {len(song_ids)} songs with {dynamic_timeout}s timeout")
        response = requests.get(song_details_base_url, timeout=dynamic_timeout)
        response.raise_for_status()
        
        response_text = response.text.encode().decode('unicode-escape')
        songs_response = json.loads(response_text)
        
        songs_data = []
        failed_ids = []
        
        # Process each song ID
        for song_id in song_ids:
            if song_id in songs_response:
                try:
                    song_data = helper.format_song(songs_response[song_id], lyrics)
                    songs_data.append(song_data)
                except Exception as e:
                    logger.error(f"Error formatting song {song_id}: {str(e)}")
                    failed_ids.append(song_id)
            else:
                logger.warning(f"Song ID {song_id} not found in response")
                failed_ids.append(song_id)
        
        # Prepare response
        result = {
            "status": True,
            "songs": songs_data,
            "total_requested": len(song_ids),
            "total_found": len(songs_data),
            "failed_ids": failed_ids
        }
        
        if failed_ids:
            result["message"] = f"Some songs could not be fetched: {failed_ids}"
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in get_multiple_songs: {str(e)}")
        return {
            "status": False,
            "error": f"Request failed: {str(e)}"
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in get_multiple_songs: {str(e)}")
        return {
            "status": False,
            "error": f"Invalid response format: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_multiple_songs: {str(e)}")
        return {
            "status": False,
            "error": f"An unexpected error occurred: {str(e)}"
        }


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


def _select_highest_quality_image(images):
    try:
        if not images or not isinstance(images, list):
            return None
        # Try to pick by explicit quality field ordering if present
        quality_priority = {
            '500x500': 4,
            '480x480': 3,
            '320x320': 2,
            '150x150': 1
        }
        def score(img):
            q = img.get('quality') or ''
            return quality_priority.get(q, 0)
        best = max(images, key=score)
        # Fallback: if url has size patterns, prefer largest by parsing digits
        if not best.get('url') and images:
            best = images[0]
        return best
    except Exception:
        return images[0] if images else None


def global_search(query):
    """Call the Cloudflare Worker global search and normalize response.
    Keeps positions and topQuery, chooses highest-quality image and download url.
    """
    if not query:
        return {"success": False, "error": "Query is required"}
    try:
        url = endpoints.global_search_base_url + query
        logger.info(f"Making request to: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid response"}

        # Expecting { success, data: { sections... } }
        result = {
            "success": bool(data.get('success', True)),
            "data": {}
        }
        payload = data.get('data') or {}

        def process_section(section_name):
            section = payload.get(section_name)
            if not section:
                return None
            results = section.get('results') or []
            normalized = []
            for item in results:
                obj = dict(item) if isinstance(item, dict) else {}
                # Highest quality image
                img = _select_highest_quality_image(obj.get('image'))
                if img:
                    if isinstance(img, dict):
                        obj['image'] = img.get('url')
                    elif isinstance(img, str):
                        obj['image'] = img
                # Albums: rename artist -> primaryArtists
                if section_name == 'albums':
                    if 'artist' in obj and 'primaryArtists' not in obj:
                        obj['primaryArtists'] = obj.get('artist')
                        try:
                            del obj['artist']
                        except Exception:
                            pass
                    # Albums: rename url -> album_url
                    if 'url' in obj and 'album_url' not in obj:
                        obj['album_url'] = obj.get('url')
                        try:
                            del obj['url']
                        except Exception:
                            pass
                # Playlists: rename url -> playlist_url
                if section_name == 'playlists':
                    if 'url' in obj and 'playlist_url' not in obj:
                        obj['playlist_url'] = obj.get('url')
                        try:
                            del obj['url']
                        except Exception:
                            pass
                normalized.append(obj)
            return {
                "results": normalized,
                "position": section.get('position')
            }

        for name in [
            'topQuery', 'songs', 'albums', 'playlists', 'artists'
        ]:
            processed = process_section(name)
            if processed is not None:
                result['data'][name] = processed

        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in global_search: {str(e)}")
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in global_search: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred"}


def _select_highest_quality_download_url(downloads):
    try:
        if not downloads:
            return None
        if isinstance(downloads, list):
            # Items may be {quality, url}
            def score(item):
                q = (item or {}).get('quality') or ''
                if isinstance(q, str) and q.isdigit():
                    try:
                        return int(q)
                    except Exception:
                        return 0
                # fallback by inspecting url
                u = (item or {}).get('url') or ''
                if '320' in u: return 320
                if '160' in u: return 160
                if '96' in u: return 96
                return 0
            best = max(downloads, key=score)
            return (best or {}).get('url')
        return None
    except Exception:
        return None


def get_artist_details(artist_id):
    """Fetch and normalize artist details from worker endpoint.
    - image collapsed to best url string
    - topSongs/singles: select highest-quality download url into downloadUrl (string)
    - topAlbums: collapse image to best url
    - similarArtists: collapse image to best url
    """
    if not artist_id:
        return {"success": False, "error": "Artist id is required"}
    try:
        url = endpoints.artist_details_base_url + artist_id
        logger.info(f"Making request to: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid response"}
        payload = (data or {}).get('data') or {}

        # Remove availableLanguages if present
        try:
            if 'availableLanguages' in payload:
                del payload['availableLanguages']
        except Exception:
            pass

        # Root image
        root_img = _select_highest_quality_image(payload.get('image'))
        if root_img:
            payload['image'] = root_img.get('url') if isinstance(root_img, dict) else root_img

        # Helper to normalize artists to primary only and collapse image
        def keep_primary_artists_only(container):
            try:
                if not isinstance(container, dict):
                    return container
                primary_list = (container.get('primary') or [])
                normalized_primary = []
                for a in primary_list:
                    artist_obj = dict(a)
                    aimg = _select_highest_quality_image(artist_obj.get('image'))
                    if aimg:
                        artist_obj['image'] = aimg.get('url') if isinstance(aimg, dict) else aimg
                    normalized_primary.append(artist_obj)
                return { 'primary': normalized_primary }
            except Exception:
                return { 'primary': container.get('primary', []) } if isinstance(container, dict) else container

        # Top songs
        songs = payload.get('topSongs') or []
        normalized_songs = []
        for s in songs:
            song = dict(s)
            img = _select_highest_quality_image(song.get('image'))
            if img:
                song['image'] = img.get('url') if isinstance(img, dict) else img
            best_dl = _select_highest_quality_download_url(song.get('downloadUrl'))
            if best_dl:
                song['downloadUrl'] = best_dl
            # Replace artists object with a single primaryartist string
            try:
                artists_block = song.get('artists') or {}
                primary_list = artists_block.get('primary') or []
                primary_names = []
                for a in primary_list:
                    name = (a or {}).get('name')
                    if name:
                        primary_names.append(name)
                if primary_names:
                    song['primaryartist'] = ', '.join(primary_names)
                if 'artists' in song:
                    del song['artists']
            except Exception:
                if 'artists' in song:
                    try:
                        del song['artists']
                    except Exception:
                        pass
            normalized_songs.append(song)
        payload['topSongs'] = normalized_songs

        # Remove singles entirely as not needed
        try:
            if 'singles' in payload:
                del payload['singles']
        except Exception:
            pass

        # Top albums: image only
        albums = payload.get('topAlbums') or []
        normalized_albums = []
        for a in albums:
            album = dict(a)
            img = _select_highest_quality_image(album.get('image'))
            if img:
                album['image'] = img.get('url') if isinstance(img, dict) else img
            # Replace artists object with a single primaryartist string
            try:
                artists_block = album.get('artists') or {}
                primary_list = artists_block.get('primary') or []
                primary_names = []
                for aobj in primary_list:
                    name = (aobj or {}).get('name')
                    if name:
                        primary_names.append(name)
                if primary_names:
                    album['primaryartist'] = ', '.join(primary_names)
                if 'artists' in album:
                    del album['artists']
            except Exception:
                if 'artists' in album:
                    try:
                        del album['artists']
                    except Exception:
                        pass
            # Rename url -> album_url
            try:
                if 'url' in album and 'album_url' not in album:
                    album['album_url'] = album.get('url')
                    del album['url']
            except Exception:
                pass
            normalized_albums.append(album)
        payload['topAlbums'] = normalized_albums

        # Similar artists: image only
        sim_artists = payload.get('similarArtists') or []
        normalized_sim = []
        for ar in sim_artists:
            artist = dict(ar)
            img = _select_highest_quality_image(artist.get('image'))
            if img:
                artist['image'] = img.get('url') if isinstance(img, dict) else img
            normalized_sim.append(artist)
        payload['similarArtists'] = normalized_sim

        return {"success": bool(data.get('success', True)), "data": payload}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in get_artist_details: {str(e)}")
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_artist_details: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred"}


def get_song_suggestions(song_id):
    """Fetch and normalize song recommendations for a given song id.
    - Collapse image to best URL string
    - Keep only primary artists (as a primaryartist string)
    - Select highest-quality downloadUrl as a single string
    """
    if not song_id:
        return {"success": False, "error": "Song id is required"}
    try:
        url = f"{endpoints.song_suggestions_base_url}{song_id}/suggestions"
        logger.info(f"Making request to: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return {"success": False, "error": "Invalid response"}
        items = (data or {}).get('data') or []
        normalized = []
        for itm in items:
            obj = dict(itm)
            # Image
            img = _select_highest_quality_image(obj.get('image'))
            if img:
                obj['image'] = img.get('url') if isinstance(img, dict) else img
            # Primary artists only -> primaryartist string
            try:
                artists_block = obj.get('artists') or {}
                primary_list = artists_block.get('primary') or []
                names = []
                for a in primary_list:
                    name = (a or {}).get('name')
                    if name:
                        names.append(name)
                if names:
                    obj['primaryartist'] = ', '.join(names)
                if 'artists' in obj:
                    del obj['artists']
            except Exception:
                if 'artists' in obj:
                    try:
                        del obj['artists']
                    except Exception:
                        pass
            # Download url best
            best_dl = _select_highest_quality_download_url(obj.get('downloadUrl'))
            if best_dl:
                obj['downloadUrl'] = best_dl
            normalized.append(obj)
        return {"success": bool(data.get('success', True)), "data": normalized}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in get_song_suggestions: {str(e)}")
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_song_suggestions: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred"}