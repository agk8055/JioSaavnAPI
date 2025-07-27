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
        lyrics = False
        songdata = True
        query = request.args.get('query')
        lyrics_ = request.args.get('lyrics')
        songdata_ = request.args.get('songdata')
        if lyrics_ and lyrics_.lower() != 'false':
            lyrics = True
        if songdata_ and songdata_.lower() != 'true':
            songdata = False
        if query:
            logger.info(f"Searching for song: {query}")
            result = jiosaavn.search_for_song(query, lyrics, songdata)
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
        id = jiosaavn.get_album_id(query)
        songs = jiosaavn.get_album(id, lyrics)
        return jsonify(songs)
    else:
        error = {
            "status": False,
            "error": 'Query is required to search albums!'
        }
        return jsonify(error)


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
            id = jiosaavn.get_album_id(query)
            songs = jiosaavn.get_album(id, lyrics)
            return jsonify(songs)

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
