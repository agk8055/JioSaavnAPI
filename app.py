from flask import Flask, request, redirect, jsonify, json, render_template
import time
import jiosaavn
import os
import logging
from traceback import print_exc
from flask_cors import CORS
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET", 'jiosaavnapi_agk')
CORS(app)

# Add error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({
        "status": False,
        "error": "Internal Server Error. Please try again later."
    }), 500

# Add error handler for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "status": False,
        "error": "Resource not found"
    }), 404

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/song/')
def search():
    try:
        query = request.args.get('query')
        limit = request.args.get('limit', 10)  # Default limit is 10
        
        # Convert limit to integer, with validation
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 50:  # Set a reasonable maximum
                limit = 50
        except (ValueError, TypeError):
            limit = 10
        
        if query:
            logger.info(f"Searching for song: {query} with limit: {limit}")
            result = jiosaavn.search_songs_new_api(query, limit)
            return jsonify(result)
        else:
            error = {
                "status": False,
                "error": 'Query is required to search songs!'
            }
            return jsonify(error)
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({
            "status": False,
            "error": "An error occurred while processing your request"
        }), 500


@app.route('/song/get/')
def get_song():
    lyrics = False
    id = request.args.get('id')
    lyrics_ = request.args.get('lyrics')
    if lyrics_ and lyrics_.lower() != 'false':
        lyrics = True
    if id:
        resp = jiosaavn.get_song(id, lyrics)
        if not resp:
            error = {
                "status": False,
                "error": 'Invalid Song ID received!'
            }
            return jsonify(error)
        else:
            return jsonify(resp)
    else:
        error = {
            "status": False,
            "error": 'Song ID is required to get a song!'
        }
        return jsonify(error)


@app.route('/song/get-multiple/')
def get_multiple_songs():
    try:
        lyrics = False
        ids = request.args.get('ids')
        lyrics_ = request.args.get('lyrics')
        
        if lyrics_ and lyrics_.lower() != 'false':
            lyrics = True
            
        if not ids:
            error = {
                "status": False,
                "error": 'Song IDs are required! Please provide comma-separated IDs in the "ids" parameter.'
            }
            return jsonify(error)
        
        # Split the IDs by comma and clean them
        song_ids = [id.strip() for id in ids.split(',') if id.strip()]
        
        if not song_ids:
            error = {
                "status": False,
                "error": 'No valid song IDs provided!'
            }
            return jsonify(error)
        
        # Add practical limits
        MAX_SONGS = 100  # Maximum number of songs per request
        if len(song_ids) > MAX_SONGS:
            error = {
                "status": False,
                "error": f'Too many song IDs! Maximum {MAX_SONGS} songs allowed per request. You provided {len(song_ids)} songs.'
            }
            return jsonify(error)
        
        logger.info(f"Fetching multiple songs: {len(song_ids)} songs")
        
        # Get songs data using the new function
        songs_data = jiosaavn.get_multiple_songs(song_ids, lyrics)
        
        if not songs_data:
            error = {
                "status": False,
                "error": 'Failed to fetch songs data!'
            }
            return jsonify(error)
        
        return jsonify(songs_data)
        
    except Exception as e:
        logger.error(f"Error in get_multiple_songs endpoint: {str(e)}")
        return jsonify({
            "status": False,
            "error": "An error occurred while processing your request"
        }), 500


@app.route('/playlist/')
def playlist():
    lyrics = False
    query = request.args.get('query')
    lyrics_ = request.args.get('lyrics')
    if lyrics_ and lyrics_.lower() != 'false':
        lyrics = True
    if query:
        id = jiosaavn.get_playlist_id(query)
        songs = jiosaavn.get_playlist(id, lyrics)
        return jsonify(songs)
    else:
        error = {
            "status": False,
            "error": 'Query is required to search playlists!'
        }
        return jsonify(error)


@app.route('/album/')
def album():
    lyrics = False
    query = request.args.get('query')
    lyrics_ = request.args.get('lyrics')
    if lyrics_ and lyrics_.lower() != 'false':
        lyrics = True
    if query:
        # Query is expected to be an album link. Use saavn.dev adapter
        result = jiosaavn.get_album_by_link(query, lyrics)
        status_code = 200 if result and result.get('success') else 500
        return jsonify(result), status_code
    else:
        error = {
            "success": False,
            "error": 'Query (album link) is required to fetch album!'
        }
        return jsonify(error), 400


@app.route('/lyrics/')
def lyrics():
    query = request.args.get('query')

    if query:
        try:
            if 'http' in query and 'saavn' in query:
                id = jiosaavn.get_song_id(query)
                lyrics = jiosaavn.get_lyrics(id)
            else:
                lyrics = jiosaavn.get_lyrics(query)
            response = {}
            response['status'] = True
            response['lyrics'] = lyrics
            return jsonify(response)
        except Exception as e:
            error = {
                "status": False,
                "error": str(e)
            }
            return jsonify(error)

    else:
        error = {
            "status": False,
            "error": 'Query containing song link or id is required to fetch lyrics!'
        }
        return jsonify(error)


@app.route('/result/')
def result():
    lyrics = False
    query = request.args.get('query')
    lyrics_ = request.args.get('lyrics')
    if lyrics_ and lyrics_.lower() != 'false':
        lyrics = True

    if 'saavn' not in query:
        return jsonify(jiosaavn.search_for_song(query, lyrics, True))
    try:
        if '/song/' in query:
            print("Song")
            song_id = jiosaavn.get_song_id(query)
            song = jiosaavn.get_song(song_id, lyrics)
            return jsonify(song)

        elif '/album/' in query:
            print("Album")
            result = jiosaavn.get_album_by_link(query, lyrics)
            return jsonify(result)

        elif '/playlist/' or '/featured/' in query:
            print("Playlist")
            id = jiosaavn.get_playlist_id(query)
            songs = jiosaavn.get_playlist(id, lyrics)
            return jsonify(songs)

    except Exception as e:
        print_exc()
        error = {
            "status": True,
            "error": str(e)
        }
        return jsonify(error)
    return None


@app.route('/keep-alive/')
def keep_alive():
    return jsonify({
        "status": True,
        "message": f"Service is running at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    })


@app.route('/search/')
def global_search_route():
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({
                "success": False,
                "error": 'Query is required to search!'
            }), 400
        logger.info(f"Global search for: {query}")
        result = jiosaavn.global_search(query)
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in global_search_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/artist/')
def artist_details_route():
    try:
        artist_id = request.args.get('id')
        if not artist_id:
            return jsonify({
                "success": False,
                "error": 'Artist id is required!'
            }), 400
        logger.info(f"Artist details for: {artist_id}")
        result = jiosaavn.get_artist_details(artist_id)
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in artist_details_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/song/suggestions/')
def song_suggestions_route():
    try:
        song_id = request.args.get('id')
        if not song_id:
            return jsonify({
                "success": False,
                "error": 'Song id is required!'
            }), 400
        logger.info(f"Song suggestions for: {song_id}")
        result = jiosaavn.get_song_suggestions(song_id)
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in song_suggestions_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/search/playlists/')
def search_playlists_route():
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({
                "success": False,
                "error": 'Query is required!'
            }), 400
        logger.info(f"Search playlists for: {query}")
        result = jiosaavn.search_playlists(query)
        # If upstream returned an HTTP status, prefer that; otherwise map success
        status_code = result.get('status') or (200 if result.get('success') else 500)
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in search_playlists_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/search/albums/')
def search_albums_route():
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({
                "success": False,
                "error": 'Query is required!'
            }), 400
        logger.info(f"Search albums for: {query}")
        result = jiosaavn.search_albums(query)
        status_code = result.get('status') or (200 if result.get('success') else 500)
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in search_albums_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/search/artists/')
def search_artists_route():
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({
                "success": False,
                "error": 'Query is required!'
            }), 400
        logger.info(f"Search artists for: {query}")
        result = jiosaavn.search_artists(query)
        status_code = result.get('status') or (200 if result.get('success') else 500)
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in search_artists_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/artist/songs/')
def artist_songs_route():
    try:
        artist_id = request.args.get('id')
        sort_by = request.args.get('sortBy', 'latest')
        sort_order = request.args.get('sortOrder', 'desc')
        
        if not artist_id:
            return jsonify({
                "success": False,
                "error": 'Artist ID is required!'
            }), 400
        
        logger.info(f"Artist songs for: {artist_id}, sortBy: {sort_by}, sortOrder: {sort_order}")
        result = jiosaavn.get_artist_songs(artist_id, sort_by, sort_order)
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in artist_songs_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


@app.route('/artist/albums/')
def artist_albums_route():
    try:
        artist_id = request.args.get('id')
        sort_by = request.args.get('sortBy', 'latest')
        sort_order = request.args.get('sortOrder', 'desc')
        
        if not artist_id:
            return jsonify({
                "success": False,
                "error": 'Artist ID is required!'
            }), 400
        
        logger.info(f"Artist albums for: {artist_id}, sortBy: {sort_by}, sortOrder: {sort_order}")
        result = jiosaavn.get_artist_albums(artist_id, sort_by, sort_order)
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in artist_albums_route: {str(e)}")
        return jsonify({
            "success": False,
            "error": 'An error occurred while processing your request'
        }), 500


# Initialize keep-alive service when app starts
def init_keep_alive():
    try:
        from keep_alive import run_scheduler
        import threading
        
        # Start the keep-alive service in a separate thread
        keep_alive_thread = threading.Thread(target=run_scheduler)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()
        logger.info("Keep-alive service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize keep-alive service: {e}")

# Initialize keep-alive when app starts
init_keep_alive()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5100))
    
    logger.info(f"\nServer is running on http://localhost:{port}")
    logger.info("Keep-alive service is running (pings every 10 minutes)")
    logger.info("Press Ctrl+C to stop the server\n")
    
    # For local development, you can still run with python app.py
    app.run(host='0.0.0.0', port=port, debug=False)
