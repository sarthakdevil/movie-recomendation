import requests
import pandas as pd
import streamlit as st
import gdown
import os

@st.cache_data
def download_csv():
    output = 'cosine_similarity_matrix.csv'
    
    if not os.path.exists(output):
        url = 'https://drive.google.com/file/d/13N5MEn8yRkbHqnYYrdn1jXq4XGZewrir'
        gdown.download(url, output, quiet=False)
    
    return pd.read_csv(output)

df = download_csv()
names = df["original_title"]

tmdb_genres = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def fetch_movie(start, end):
    api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
    movies = []
    
    for movie in names[start:end]:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                movies.append(data['results'][0])
    return movies

def recommendmovies(movie):
    if movie:
        movie_row = df[df['original_title'] == movie]
        
        if not movie_row.empty:
            similarity_scores = movie_row.iloc[0, 1:].values
            similar_indices = similarity_scores.argsort()[-6:][::-1]  # Top 5 similar movies
            recommended_movies = df['original_title'].iloc[similar_indices].tolist()
            return recommended_movies
    return []

def display_movie_details(movie):
    st.write(f"**Release Date:** {movie.get('release_date', 'N/A')}")
    st.write(f"**Overview:** {movie.get('overview', 'No overview available.')}")
    
    if 'genre_ids' in movie:
        genres = [tmdb_genres.get(genre_id, "Unknown Genre") for genre_id in movie['genre_ids']]
        st.write("**Genres:** " + ", ".join(genres))
        
    if movie.get('poster_path'):
        st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", use_column_width=True)

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
            display_movie_details(movie)
            
            recommended_movies = recommendmovies(clickedmovie)
            if recommended_movies:
                st.write("**Recommended Movies:**")
                for rec_movie in recommended_movies:
                    rec_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={rec_movie}'
                    rec_response = requests.get(rec_url)
                    if rec_response.status_code == 200:
                        rec_data = rec_response.json()
                        if rec_data['results']:
                            rec_movie_detail = rec_data['results'][0]
                            with st.expander(f"Title: {rec_movie_detail['title']}"):
                                display_movie_details(rec_movie_detail)
                    else:
                        st.write(f"Failed to fetch data for {rec_movie}. Status code: {rec_response.status_code}")
        else:
            st.write("No movie details found.")
    else:
        st.write(f"Failed to fetch data for {clickedmovie}. Status code: {response.status_code}")

def display_movies(movies):
    for movie in movies:
        with st.expander(f"Title: {movie['title']}"):
            display_movie_details(movie)

            if st.button(f"More details about {movie['title']}", key=f"details_{movie['title']}"):
                st.session_state.clickedmovie = movie['title']
                st.experimental_rerun()

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
