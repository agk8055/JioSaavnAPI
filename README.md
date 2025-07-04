## JioSaavn API [Unofficial]




#### JioSaavn API written in Python using Flask  

 ---
###### **NOTE:** You don't need to have JioSaavn link of the song in order to fetch the song details, you can directly search songs by their name. Fetching Songs/Albums/Playlists from URL is also supported in this API.  

 ---

### **Features**:
##### Currently the API can get the following details for a specific song in JSON format:
- **Song Name**
- **Singer Name**
- **Album Name**
- **Album URL**
- **Duration of Song**
- **Song Thumbnail URL (Max Resolution)**
- **Song Language**
- **Download Link**
- **Release Year**
- **Album Art Link (Max Resolution)**
- **Lyrics**
- .... and much more!

```json
{
    "320kbps": "true",
    "album": "Master the Blaster (From 'Master')",
    "album_url": "https://www.jiosaavn.com/album/master-the-blaster-from-master/bm08zaoA,v8_",
    "albumid": "24674412",
    "artistMap": {
      "Anirudh Ravichander": "455663",
      "Bjorn Surrao": "4186000",
      "Maalavika Mohanan": "4662798",
      "Vijay": "456196",
      "Vijay Sethupathi": "678644"
    },
    "cache_state": "false",
    "copyright_text": "(P) 2021 Sony Music Entertainment India Pvt. Ltd.",
    "disabled": "true",
    "disabled_text": "Pro Only",
    "duration": "92",
    "encrypted_drm_media_url": "ID2ieOjCrwdjlkMElYlzWCptgNdUpWD8LRE8Rbogcadp0y9nKt9e0vDwQ/c4KOC3pYwArKjHDYx14Ww52kdm4I92mytrdt3FDnQW0nglPS4=",
    "encrypted_media_path": "NMKyboFo/FjFazSsUh4NWs3kci1T1YWGH/JdPU07eeT4zCGOSqtc3Cy8/+rvxSGz",
    "encrypted_media_url": "ID2ieOjCrwfgWvL5sXl4B1ImC5QfbsDy9CHyv3PDSNjUZHvft3t06LUXJ82rJU02dJhptVREyeuyLS4zyGwl0Rw7tS9a8Gtq",
    "explicit_content": 0,
    "featured_artists": "",
    "featured_artists_id": "",
    "has_lyrics": "false",
    "id": "-4ejJN56",
    "image": "https://c.saavncdn.com/231/Master-the-Blaster-From-Master--English-2021-20210115102601-500x500.jpg",
    "is_dolby_content": false,
    "is_drm": 1,
    "label": "Sony Music Entertainment India Pvt. Ltd.",
    "label_id": "1070109",
    "label_url": "/label/sony-music-entertainment-india-pvt.-ltd.-albums/LaFAA6h1q2U_",
    "language": "tamil",
    "lyrics_snippet": "",
    "media_preview_url": "https://preview.saavncdn.com/231/62e7a34859f457ddd4103f94c2d2f0a5_96_p.mp4",
    "media_url": "https://aac.saavncdn.com/231/62e7a34859f457ddd4103f94c2d2f0a5_320.mp4",
    "music": "Anirudh Ravichander",
    "music_id": "455663",
    "origin": "none",
    "perma_url": "https://www.jiosaavn.com/song/master-the-blaster-from-master/XVwOWz5,AgU",
    "play_count": 14100426,
    "primary_artists": "Anirudh Ravichander, Bjorn Surrao",
    "primary_artists_id": "455663, 4186000",
    "release_date": "2021-01-15",
    "rights": {
      "cacheable": true,
      "code": 1,
      "delete_cached_object": false,
      "reason": "Pro Only"
    },
    "singers": "Anirudh Ravichander, Bjorn Surrao",
    "song": "Master the Blaster (From 'Master')",
    "starred": "false",
    "starring": "Vijay, Maalavika Mohanan, Vijay Sethupathi",
    "triller_available": false,
    "type": "",
    "vcode": "010910141221835",
    "vlink": "https://jiotunepreview.jio.com/content/Converted/010910141178263.mp3",
    "webp": true,
    "year": "2021"
  },
  }
```

### **Installation**:

Clone this repository using
```sh
$ git clone https://github.com/cyberboysumanjay/JioSaavnAPI
```
Enter the directory and install all the requirements using
```sh
$ pip3 install -r requirements.txt
```
Run the app using
```sh
$ python3 app.py
```
Navigate to 127.0.0.1:5000 to see the Homepage

### **Usage**:
Fetching lyrics is optional and is triggered only when it is passed as an argument in the GET Request. (**&lyrics=true**)
**If you enable lyrics search, it will take more time to fetch results**

---
##### **Universal Endpoint**: (Supports Song Name, Song Link, Album Link, Playlist Link)
```sh
http://127.0.0.1:5000/result/?query=<insert-jiosaavn-link-or-query-here>&lyrics=true
```
**Example:** Navigate to http://127.0.0.1:5000/result/?query=alone to get a JSON response of songs data in return.

----


##### **Song URL Endpoint**:
```sh
http://127.0.0.1:5000/song/?query=<insert-jiosaavn-song-link>&lyrics=true
```
**Example:** Navigate to http://127.0.0.1:5000/song/?query=https://www.jiosaavn.com/song/khairiyat/PwAFSRNpAWw to get a JSON response of song data in return.

---

##### **Playlist URL Endpoint**:
```sh
http://127.0.0.1:5000/playlist/?query=<insert-jiosaavn-playlist-link>&lyrics=true
```
**Example:** Navigate to http://127.0.0.1:5000/playlist/?query=https://www.jiosaavn.com/featured/romantic-hits-2020---hindi/ABiMGqjovSFuOxiEGmm6lQ__ to get a JSON response of playlist data in return.

---

##### **Album URL Endpoint**:
```sh
http://127.0.0.1:5000/album/?query=<insert-jiosaavn-album-link>&lyrics=true
```
**Example:** Navigate to http://127.0.0.1:5000/album/?query=https://www.jiosaavn.com/album/chhichhore/V4F3M5,cNb4_ to get a JSON response of album data in return.

---

##### **Lyrics Endpoint**:
```sh
http://127.0.0.1:5000/lyrics/?query=<insert-jiosaavn-song-link-or-song-id>&lyrics=true
```
**Example:** Navigate to http://127.0.0.1:5000/lyrics/?query=https://www.jiosaavn.com/song/khairiyat/PwAFSRNpAWw to get a JSON response of lyrics data in return.

---



