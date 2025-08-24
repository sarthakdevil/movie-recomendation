import requests
import pandas as pd
import streamlit as st
import gdown
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="🎬 CinemaScope - Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .movie-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 4px solid #ff6b6b;
    }
    
    .genre-tag {
        display: inline-block;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
        font-weight: 500;
    }
    
    .rating-badge {
        background: #ffd700;
        color: #333;
        padding: 4px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .recommendation-header {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 15px;
        border-radius: 10px;
        color: #333;
        text-align: center;
        margin: 20px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def download_csv():
    """Download and cache the cosine similarity matrix CSV"""
    output = 'cosine_similarity_matrix.csv'
    
    if not os.path.exists(output):
        with st.spinner('🎬 Loading movie database...'):
            url = 'https://drive.google.com/file/d/13N5MEn8yRkbHqnYYrdn1jXq4XGZewrir'
            gdown.download(url, output, quiet=False)
    
    return pd.read_csv(output)

# Initialize data
df = download_csv()
names = df["original_title"]

tmdb_genres = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def fetch_movie_data(start, end):
    """Fetch movie data from TMDB API with error handling"""
    api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
    movies = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_movies = end - start
    
    for idx, movie in enumerate(names[start:end]):
        try:
            url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    movies.append(data['results'][0])
            
            # Update progress
            progress = (idx + 1) / total_movies
            progress_bar.progress(progress)
            status_text.text(f'Loading movies... {idx + 1}/{total_movies}')
            
        except Exception as e:
            st.warning(f"Failed to fetch data for '{movie}': {str(e)}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    return movies

def get_movie_recommendations(movie_title):
    """Get movie recommendations based on cosine similarity"""
    if movie_title:
        movie_row = df[df['original_title'] == movie_title]
        
        if not movie_row.empty:
            similarity_scores = movie_row.iloc[0, 1:].values
            similar_indices = similarity_scores.argsort()[-6:][::-1][1:]  # Top 5 similar movies (excluding self)
            recommended_movies = df['original_title'].iloc[similar_indices].tolist()
            return recommended_movies
    return []

def display_movie_card(movie, show_recommendations=False):
    """Display a beautifully formatted movie card"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if movie.get('poster_path'):
            st.image(
                f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", 
                use_container_width=True,
                caption=movie['title']
            )
        else:
            st.markdown(
                f"""
                <div style='background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                           height: 300px; display: flex; align-items: center; 
                           justify-content: center; border-radius: 10px; color: white; 
                           font-weight: bold; text-align: center;'>
                    🎬<br>{movie['title']}
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown(f"### 🎬 {movie['title']}")
        
        # Rating and release date
        col2a, col2b = st.columns(2)
        with col2a:
            if movie.get('vote_average'):
                rating = movie['vote_average']
                st.markdown(
                    f'<span class="rating-badge">⭐ {rating:.1f}/10</span>', 
                    unsafe_allow_html=True
                )
        with col2b:
            if movie.get('release_date'):
                try:
                    release_year = datetime.strptime(movie['release_date'], '%Y-%m-%d').year
                    st.markdown(f"**📅 Released:** {release_year}")
                except:
                    st.markdown(f"**📅 Released:** {movie.get('release_date', 'N/A')}")
        
        # Genres
        if 'genre_ids' in movie and movie['genre_ids']:
            genres = [tmdb_genres.get(genre_id, "Unknown") for genre_id in movie['genre_ids']]
            genres_html = "".join([f'<span class="genre-tag">{genre}</span>' for genre in genres])
            st.markdown(f"**🎭 Genres:** {genres_html}", unsafe_allow_html=True)
        
        # Overview
        if movie.get('overview'):
            st.markdown(f"**📖 Overview:** {movie['overview']}")
        
        # Popularity score
        if movie.get('popularity'):
            st.markdown(f"**🔥 Popularity Score:** {movie['popularity']:.1f}")
    
    # Recommendations section
    if show_recommendations:
        st.markdown('<div class="recommendation-header">🎯 Recommended Movies Based on This Selection</div>', unsafe_allow_html=True)
        
        recommended_movies = get_movie_recommendations(movie['title'])
        if recommended_movies:
            for rec_movie in recommended_movies[:5]:  # Limit to top 5
                try:
                    api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
                    rec_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={rec_movie}'
                    rec_response = requests.get(rec_url, timeout=10)
                    
                    if rec_response.status_code == 200:
                        rec_data = rec_response.json()
                        if rec_data['results']:
                            rec_movie_detail = rec_data['results'][0]
                            
                            with st.expander(f"🎬 {rec_movie_detail['title']} ({rec_movie_detail.get('release_date', 'N/A')[:4] if rec_movie_detail.get('release_date') else 'N/A'})"):
                                display_movie_card(rec_movie_detail, show_recommendations=False)
                except Exception as e:
                    st.error(f"Failed to fetch details for '{rec_movie}': {str(e)}")

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">🎬 CinemaScope</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover your next favorite movie with AI-powered recommendations</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## 🎛️ Controls")
    st.sidebar.markdown("---")
    
    # Search functionality
    search_query = st.sidebar.text_input("🔍 Search for a movie:", placeholder="Enter movie title...")
    
    if search_query:
        # Search for specific movie
        api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
        search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={search_query}'
        
        try:
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    st.success(f"Found movie: {data['results'][0]['title']}")
                    display_movie_card(data['results'][0], show_recommendations=True)
                else:
                    st.warning("No movies found matching your search.")
            else:
                st.error("Failed to search for movies. Please try again.")
        except Exception as e:
            st.error(f"Search error: {str(e)}")
        
        return
    
    # Statistics
    total_movies = len(names)
    st.markdown(
        f"""
        <div class="stats-container">
            <h3>📊 Database Statistics</h3>
            <p><strong>{total_movies:,}</strong> movies available for recommendations</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Pagination settings
    movies_per_page = st.sidebar.slider("🎬 Movies per page:", min_value=5, max_value=50, value=20, step=5)
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    if 'clicked_movie' in st.session_state and st.session_state.clicked_movie:
        # Display selected movie details with recommendations
        api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={st.session_state.clicked_movie}'
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    movie = data['results'][0]
                    display_movie_card(movie, show_recommendations=True)
                    
                    # Back button
                    if st.button("🔙 Back to Browse", type="primary"):
                        st.session_state.clicked_movie = None
                        st.rerun()
                else:
                    st.error("Movie details not found.")
        except Exception as e:
            st.error(f"Error loading movie details: {str(e)}")
        
        return
    
    # Browse movies with pagination
    start_index = (st.session_state.page - 1) * movies_per_page
    end_index = start_index + movies_per_page
    
    st.markdown(f"### 🎭 Browse Movies (Page {st.session_state.page})")
    
    movies = fetch_movie_data(start_index, end_index)
    
    if movies:
        # Display movies in a grid
        for i in range(0, len(movies), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(movies):
                    movie = movies[i]
                    with st.container():
                        display_movie_card(movie, show_recommendations=False)
                        
                        if st.button(f"🎯 Get Recommendations for {movie['title']}", 
                                   key=f"rec_{movie['title']}_{i}", 
                                   type="secondary"):
                            st.session_state.clicked_movie = movie['title']
                            st.rerun()
            
            with col2:
                if i + 1 < len(movies):
                    movie = movies[i + 1]
                    with st.container():
                        display_movie_card(movie, show_recommendations=False)
                        
                        if st.button(f"🎯 Get Recommendations for {movie['title']}", 
                                   key=f"rec_{movie['title']}_{i+1}", 
                                   type="secondary"):
                            st.session_state.clicked_movie = movie['title']
                            st.rerun()
    else:
        st.warning("No movies found for this page.")
    
    # Pagination controls
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col2:
        if st.session_state.page > 1:
            if st.button("⬅️ Previous", type="secondary", use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
    
    with col3:
        total_pages = (total_movies + movies_per_page - 1) // movies_per_page
        st.markdown(f"<div style='text-align: center; padding: 10px;'>Page {st.session_state.page} of {total_pages}</div>", unsafe_allow_html=True)
    
    with col4:
        if st.session_state.page * movies_per_page < total_movies:
            if st.button("Next ➡️", type="secondary", use_container_width=True):
                st.session_state.page += 1
                st.rerun()
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 How it works")
    st.sidebar.markdown("""
    1. **Browse** through our curated movie collection
    2. **Search** for specific movies using the search bar
    3. **Click** 'Get Recommendations' to discover similar movies
    4. **Explore** AI-powered suggestions based on movie similarity
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Powered by TMDB API & AI*")

if __name__ == "__main__":
    main()