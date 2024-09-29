import requests
import pandas as pd
import streamlit as st
import gdown
import os
import io

# Function to stream CSV data from Google Drive
def stream_csv_from_gdrive():
    url = 'https://drive.google.com/uc?id=1dcAQZaZ3cWc9p2HTYDfwWWlVBfsMQCDZ'  # Google Drive link
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        # Create a BytesIO buffer to read the content
        buffer = io.StringIO(response.content.decode('utf-8'))
        for chunk in pd.read_csv(buffer, chunksize=1000):  # Adjust chunk size as needed
            yield chunk
    else:
        st.error("Failed to fetch the CSV file from Google Drive.")

# Initialize the DataFrame
df_chunks = stream_csv_from_gdrive()
df = pd.concat(df_chunks)  # Combine the chunks into a single DataFrame
names = df["original_title"]

tmdb_genres = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

# Function to fetch movie details from TMDb with pagination
def fetch_movie(start, end):
    api_key = os.getenv("TMDB_API_KEY")
    movies = []
    
    for movie in names[start:end]:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                movies.append(data['results'][0])

    return movies

# Function to recommend movies based on similarity
def recommendmovies(movie):
    if movie:
        movie_row = df[df['original_title'] == movie]
        
        if not movie_row.empty:
            similarity_scores = movie_row.iloc[0, 1:].values
            similar_indices = similarity_scores.argsort()[-6:][::-1]  
            recommended_movies = df['original_title'].iloc[similar_indices].tolist()
            return recommended_movies
    return []

# Function to display details of a clicked movie
def displaymoviebytitle(clickedmovie):
    st.session_state.clear_page = True
    
    api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={clickedmovie}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            movie = data['results'][0]
            st.header(f"**Title:** {movie['title']}")
            st.write(f"**Release Date:** {movie.get('release_date', 'N/A')}")
            st.write(f"**Overview:** {movie.get('overview', 'No overview available.')}")
            
            if 'genre_ids' in movie:
                genres = [tmdb_genres.get(genre_id, "Unknown Genre") for genre_id in movie['genre_ids']]
                st.write("**Genres:** " + ", ".join(genres))
                
            if movie.get('poster_path'):
                st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", use_column_width=True)
                
            recommended_movies = recommendmovies(clickedmovie)
            if recommended_movies:
                st.write("**Recommended Movies:**")
                for rec_movie in recommended_movies:
                    with st.expander(f"Title: {rec_movie}"):
                        st.write(f"Overview for {rec_movie}.")
        else:
            st.write("No movie details found.")
    else:
        st.write(f"Failed to fetch data for {clickedmovie}. Status code: {response.status_code}")

# Function to display movies with pagination
def display_movies(movies):
    for movie in movies:
        with st.expander(f"Title: {movie['title']}"):
            st.write(f"Release Date: {movie['release_date']}")
            st.write(f"Overview: {movie['overview']}")
            if movie.get('poster_path'):
                st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", use_column_width=True)

            if st.button(f"More details about {movie['title']}", key=f"details_{movie['title']}"):
                st.session_state.clickedmovie = movie['title']
                st.experimental_rerun()

# Pagination control
movies_per_page = 20

if 'page' not in st.session_state:
    st.session_state.page = 1

if 'clickedmovie' in st.session_state:
    displaymoviebytitle(st.session_state.clickedmovie)
else:
    start_index = (st.session_state.page - 1) * movies_per_page
    end_index = start_index + movies_per_page

    movies = fetch_movie(start_index, end_index)

    if movies:
        display_movies(movies)
    else:
        st.write("No movies found.")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.session_state.page > 1:
            if st.button("Previous"):
                st.session_state.page -= 1
                st.experimental_rerun()

    with col2:
        if st.session_state.page * movies_per_page < len(names):
            if st.button("Next"):
                st.session_state.page += 1
                st.experimental_rerun()
