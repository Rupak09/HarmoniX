import streamlit as st
import requests
import re
import time

DEEZER_API_KEY = "8a24827cb4msh94a6cd7724c166ep1ebd7ajsn653fbbfcf8b0"
DEEZER_API_HOST = "deezerdevs-deezer.p.rapidapi.com"


if 'current_song' not in st.session_state:
    st.session_state.current_song = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'playlists' not in st.session_state:
    st.session_state.playlists = {}
if 'now_playing_queue' not in st.session_state:
    st.session_state.now_playing_queue = []
if 'queue_position' not in st.session_state:
    st.session_state.queue_position = 0

def search_songs(query):
    url = "https://deezerdevs-deezer.p.rapidapi.com/search"
    querystring = {"q": query}
    headers = {
        "X-RapidAPI-Key": DEEZER_API_KEY,
        "X-RapidAPI-Host": DEEZER_API_HOST
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

def play_song(song):
    st.session_state.current_song = song
    if song not in st.session_state.now_playing_queue:
        st.session_state.now_playing_queue.append(song)
    st.session_state.queue_position = st.session_state.now_playing_queue.index(song)

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def add_to_playlist(song, playlist_name):
    if playlist_name not in st.session_state.playlists:
        st.session_state.playlists[playlist_name] = []
    if song not in st.session_state.playlists[playlist_name]:
        st.session_state.playlists[playlist_name].append(song)
        st.success(f"Added '{song['title']}' to the playlist '{playlist_name}'.")
    else:
        st.warning(f"'{song['title']}' is already in the playlist '{playlist_name}'.")
    
    # Add to Now Playing queue
    if song not in st.session_state.now_playing_queue:
        st.session_state.now_playing_queue.append(song)

def remove_from_playlist(song, playlist_name):
    if playlist_name in st.session_state.playlists and song in st.session_state.playlists[playlist_name]:
        st.session_state.playlists[playlist_name].remove(song)
        st.success(f"Removed '{song['title']}' from the playlist '{playlist_name}'.")
    else:
        st.warning(f"'{song['title']}' is not in the playlist '{playlist_name}'.")

def clear_playlist(playlist_name):
    if playlist_name in st.session_state.playlists:
        st.session_state.playlists[playlist_name].clear()
        st.success(f"Playlist '{playlist_name}' cleared.")

def delete_playlist(playlist_name):
    if playlist_name in st.session_state.playlists:
        del st.session_state.playlists[playlist_name]
        st.success(f"Playlist '{playlist_name}' deleted.")
    else:
        st.warning(f"Playlist '{playlist_name}' does not exist.")

def play_next_song():
    if st.session_state.now_playing_queue:
        st.session_state.queue_position = (st.session_state.queue_position + 1) % len(st.session_state.now_playing_queue)
        st.session_state.current_song = st.session_state.now_playing_queue[st.session_state.queue_position]
        st.experimental_rerun()

def play_from_queue():
    if st.session_state.now_playing_queue:
        st.session_state.current_song = st.session_state.now_playing_queue[st.session_state.queue_position]
        st.experimental_rerun()

st.title("HarmoniX Music Player")

# Sidebar for music controls and playlists
st.sidebar.subheader("Music Controls")
volume = st.sidebar.slider("Volume", 0, 100, 50)

# Playlist management
st.sidebar.subheader("Playlists")
new_playlist_name = st.sidebar.text_input("Create new playlist:")
if st.sidebar.button("Create Playlist") and new_playlist_name:
    if new_playlist_name not in st.session_state.playlists:
        st.session_state.playlists[new_playlist_name] = []
        st.sidebar.success(f"Playlist '{new_playlist_name}' created.")
    else:
        st.sidebar.warning(f"Playlist '{new_playlist_name}' already exists.")

# Display playlists
for playlist_name in list(st.session_state.playlists.keys()):
    st.sidebar.write(f"Playlist: {playlist_name}")
    for song in st.session_state.playlists[playlist_name]:
        st.sidebar.write(f"- {song['title']}")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button(f"Play '{playlist_name}'"):
            st.session_state.now_playing_queue = st.session_state.playlists[playlist_name].copy()
            if st.session_state.now_playing_queue:
                play_song(st.session_state.now_playing_queue[0])
    with col2:
        if st.button(f"Clear '{playlist_name}'"):
            clear_playlist(playlist_name)
    with col3:
        if st.button(f"Delete '{playlist_name}'"):
            delete_playlist(playlist_name)
    st.sidebar.markdown("---")

# Main content area
search_query = st.text_input("Search for a song:")
search_button = st.button("Search")

if search_button and search_query:
    results = search_songs(search_query)
    if results and 'data' in results:
        st.session_state.search_results = results['data']
    else:
        st.session_state.search_results = None
        st.write("No results found or there was an error with the search.")

# Display search results
if st.session_state.search_results is not None:
    st.subheader("Search Results:")
    for index, track in enumerate(st.session_state.search_results):
        col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
        
        with col1:
            st.image(track.get('album', {}).get('cover_small', ''), width=56)
        
        with col2:
            title = track.get('title', 'Unknown Title')
            artist = track.get('artist', {}).get('name', 'Unknown Artist')
            album = track.get('album', {}).get('title', 'Unknown Album')
            duration = format_duration(track.get('duration', 0))
            
            st.write(f"**{title}**")
            st.write(f"Artist: {artist}")
            st.write(f"Album: {album}")
            st.write(f"Duration: {duration}")
        
        with col3:
            key = f"play_{index}_{track.get('id', '')}"
            if st.button("Play", key=key):
                play_song(track)
        
        with col4:
            playlist_select = st.selectbox("Select Playlist", list(st.session_state.playlists.keys()), key=f"playlist_select_{index}")
            if st.button("Add to Playlist", key=f"add_{index}_{track.get('id', '')}"):
                add_to_playlist(track, playlist_select)
        
        st.markdown("---")

# Display current song and player
if st.session_state.current_song:
    st.subheader("Now Playing")
    album_cover = st.session_state.current_song.get('album', {}).get('cover_medium')
    if album_cover:
        st.image(album_cover)
    
    title = st.session_state.current_song.get('title', 'Unknown Title')
    artist = st.session_state.current_song.get('artist', {}).get('name', 'Unknown Artist')
    st.write(f"🎵 {title} by {artist}")
    
    preview_url = st.session_state.current_song.get('preview')
    if preview_url:
        st.audio(preview_url, start_time=0)
    else:
        st.write("No audio available for this track.")
    
    # Display additional song information
    st.subheader("Song Information")
    album = st.session_state.current_song.get('album', {}).get('title', 'Unknown Album')
    duration = format_duration(st.session_state.current_song.get('duration', 0))
    rank = st.session_state.current_song.get('rank', 'Unknown')
    
    st.write(f"Album: {album}")
    st.write(f"Duration: {duration}")
    st.write(f"Rank: {rank}")

# Display Now Playing Queue
st.subheader("Now Playing Queue")
for index, song in enumerate(st.session_state.now_playing_queue):
    st.write(f"{index + 1}. {song['title']} by {song['artist']['name']}")

# Add button to play from queue
if st.button("Play Next from Queue"):
    play_from_queue()

# Display current state of music controls
st.sidebar.subheader("Current Player State")
st.sidebar.write(f"Volume: {volume}")
if st.session_state.current_song:
    st.sidebar.write(f"Currently playing: {st.session_state.current_song.get('title', 'Unknown Title')}")

# Add a footer
st.markdown("---")
#st.markdown("Created with Streamlit and Deezer API")