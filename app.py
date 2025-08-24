import requests
import pandas as pd
import streamlit as st
import gdown
import os
from datetime import datetime
import time

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
    
    .download-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    .download-stats {
        display: flex;
        justify-content: space-around;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    
    .stat-item {
        background: rgba(255,255,255,0.2);
        padding: 10px;
        border-radius: 8px;
        margin: 5px;
        min-width: 120px;
    }
    
    .speed-indicator {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def format_bytes(bytes_value):
    """Convert bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(bytes_value, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_value / p, 2)
    return f"{s} {size_names[i]}"

def calculate_eta(downloaded, total, elapsed_time):
    """Calculate estimated time of arrival"""
    if downloaded == 0 or elapsed_time == 0:
        return "Calculating..."
    
    speed = downloaded / elapsed_time
    if speed == 0:
        return "Unknown"
    
    remaining = total - downloaded
    eta_seconds = remaining / speed
    
    if eta_seconds < 60:
        return f"{int(eta_seconds)}s"
    elif eta_seconds < 3600:
        return f"{int(eta_seconds / 60)}m {int(eta_seconds % 60)}s"
    else:
        hours = int(eta_seconds / 3600)
        minutes = int((eta_seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

@st.cache_data
def download_csv():
    """Download and cache the cosine similarity matrix CSV with enhanced progress tracking"""
    output = 'cosine_similarity_matrix.csv'
    
    if not os.path.exists(output):
        try:
            # Create download UI container
            download_placeholder = st.empty()
            
            with download_placeholder.container():
                st.markdown("""
                <div class="download-container">
                    <h2>🎬 Setting up CinemaScope Database</h2>
                    <p>First time setup: Downloading movie similarity matrix</p>
                    <p><strong>File size:</strong> ~437 MB | <strong>Expected time:</strong> 2-5 minutes</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress tracking elements
                progress_bar = st.progress(0)
                status_container = st.container()
                
                # Google Drive file details
                file_id = '1MSeuaiDdUD5wgamiVTLkWz2u68qfji82'
                expected_size = 437 * 1024 * 1024  # 437 MB in bytes
                
                # Track download start time
                start_time = time.time()
                
                # Try gdown first with enhanced settings
                try:
                    with status_container:
                        st.info("📡 Attempting download via gdown (recommended method)...")
                    
                    progress_bar.progress(0.05)
                    
                    import gdown
                    
                    # Use gdown with fuzzy matching for large files
                    url = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
                    
                    with status_container:
                        st.info("🔄 Initiating secure download from Google Drive...")
                    
                    # Download with gdown - it handles Google Drive authentication automatically
                    success = gdown.download(url, output, quiet=False, fuzzy=True)
                    
                    if success and os.path.exists(output) and os.path.getsize(output) > 50 * 1024 * 1024:
                        progress_bar.progress(1.0)
                        with status_container:
                            st.success("✅ Download completed successfully via gdown!")
                    else:
                        raise Exception("gdown download failed or file is too small")
                
                except Exception as gdown_error:
                    st.warning(f"⚠️ gdown method failed: {str(gdown_error)}")
                    
                    # Clean up failed download
                    if os.path.exists(output):
                        os.remove(output)
                    
                    with status_container:
                        st.info("🔄 Trying advanced Google Drive download method...")
                    
                    progress_bar.progress(0.1)
                    
                    # Enhanced fallback method for Google Drive large files
                    try:
                        session = requests.Session()
                        
                        # Step 1: Get initial response
                        url = f'https://drive.google.com/uc?export=download&id={file_id}'
                        response = session.get(
                            url,
                            timeout=(30, 60),
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                            }
                        )
                        
                        # Step 2: Handle virus scan warning for large files
                        if 'virus scan warning' in response.text.lower() or 'confirm=' in response.text:
                            with status_container:
                                st.info("🔍 Handling Google Drive virus scan confirmation...")
                            
                            # Extract confirmation token
                            confirm_token = None
                            for line in response.text.split('\n'):
                                if 'confirm=' in line:
                                    import re
                                    match = re.search(r'confirm=([^&"\']+)', line)
                                    if match:
                                        confirm_token = match.group(1)
                                        break
                            
                            if not confirm_token:
                                # Alternative method to find confirm token
                                soup_text = response.text
                                if 'confirm=' in soup_text:
                                    start = soup_text.find('confirm=') + 8
                                    end = soup_text.find('&', start)
                                    if end == -1:
                                        end = soup_text.find('"', start)
                                    if end == -1:
                                        end = soup_text.find("'", start)
                                    if end > start:
                                        confirm_token = soup_text[start:end]
                            
                            if confirm_token:
                                # Download with confirmation token
                                download_url = f'https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}'
                                response = session.get(
                                    download_url,
                                    stream=True,
                                    timeout=(30, 900),  # 15 minute timeout for large file
                                    headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                    }
                                )
                            else:
                                raise Exception("Could not extract confirmation token from Google Drive")
                        
                        response.raise_for_status()
                        
                        # Get file size from headers or use expected size
                        total_size = int(response.headers.get('content-length', expected_size))
                        downloaded_size = 0
                        chunk_size = 32768  # 32KB chunks for better performance
                        
                        with status_container:
                            st.info(f"📥 Starting download of {format_bytes(total_size)}...")
                        
                        with open(output, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    file.write(chunk)
                                    downloaded_size += len(chunk)
                                    
                                    # Update progress every 5MB for smoother UI
                                    if downloaded_size % (5 * 1024 * 1024) == 0 or downloaded_size >= total_size:
                                        progress = 0.1 + (downloaded_size / total_size) * 0.85
                                        progress_bar.progress(min(progress, 0.95))
                                        
                                        elapsed_time = time.time() - start_time
                                        speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                                        eta = calculate_eta(downloaded_size, total_size, elapsed_time)
                                        
                                        with status_container:
                                            col1, col2, col3, col4 = st.columns(4)
                                            with col1:
                                                st.metric("Downloaded", format_bytes(downloaded_size))
                                            with col2:
                                                st.metric("Total Size", format_bytes(total_size))
                                            with col3:
                                                st.metric("Speed", f"{format_bytes(speed)}/s" if speed > 0 else "Calculating...")
                                            with col4:
                                                st.metric("ETA", eta)
                                            
                                            # Progress percentage
                                            percentage = (downloaded_size / total_size) * 100
                                            st.markdown(f"""
                                            <div style='text-align: center; margin-top: 10px;'>
                                                <span class="speed-indicator">
                                                    {percentage:.1f}% Complete
                                                </span>
                                            </div>
                                            """, unsafe_allow_html=True)
                        
                        progress_bar.progress(1.0)
                        with status_container:
                            total_time = time.time() - start_time
                            avg_speed = downloaded_size / total_time if total_time > 0 else 0
                            st.success(f"✅ Download completed via advanced method!")
                            st.info(f"📊 Final Stats: {format_bytes(downloaded_size)} in {total_time:.1f}s (avg: {format_bytes(avg_speed)}/s)")
                    
                    except requests.exceptions.Timeout:
                        raise Exception("Download timeout - the file is very large. Please try again with a stable internet connection.")
                    except requests.exceptions.ConnectionError:
                        raise Exception("Connection error - please check your internet connection and try again.")
                    except Exception as fallback_error:
                        raise Exception(f"Advanced download method failed: {str(fallback_error)}")
                
                # File verification
                with status_container:
                    st.info("🔍 Verifying downloaded file...")
                
                # Clear download UI after small delay
                time.sleep(2)
            
            download_placeholder.empty()
            
        except Exception as e:
            st.error(f"❌ Failed to download movie database: {str(e)}")
            st.error("💡 Troubleshooting tips:")
            st.error("• Check your internet connection stability")
            st.error("• Try refreshing the page to retry download")
            st.error("• If using corporate/school network, firewall may block large downloads")
            st.error("• The Google Drive file might be temporarily unavailable")
            st.error("• Try downloading at a different time if network is congested")
            
            if os.path.exists(output):
                os.remove(output)  # Clean up partial download
            
            return None
    
    # Verify and load the file
    if os.path.exists(output):
        try:
            file_size = os.path.getsize(output) / (1024 * 1024)  # Size in MB
            
            if file_size < 50:  # File should be ~437 MB
                st.warning(f"⚠️ Downloaded file appears corrupted (only {file_size:.1f} MB). Retrying...")
                os.remove(output)
                return download_csv()  # Recursive retry
            
            st.success(f"✅ Movie database loaded successfully! ({file_size:.1f} MB)")
            
            # Show loading progress for CSV reading
            with st.spinner("📖 Loading movie similarity matrix into memory..."):
                df = pd.read_csv(output, index_col=0)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Failed to read CSV file: {str(e)}")
            st.info("The file may be corrupted. Try refreshing the page to re-download.")
            if os.path.exists(output):
                os.remove(output)  # Clean up corrupted file
            return None
    else:
        st.error("❌ CSV file not found after download attempt.")
        return None

# Initialize data with error handling
def initialize_data():
    """Initialize the movie data with proper error handling"""
    try:
        df = download_csv()
        if df is not None:
            # Try to get movie names from different possible sources
            if 'original_title' in df.columns:
                names = df['original_title'].tolist()
            elif df.index.name == 'original_title':
                names = df.index.tolist()
            elif len(df.columns) > 1:
                # For cosine similarity matrix, movie names are usually in columns
                names = df.columns.tolist()
            else:
                st.error("Could not determine movie names from CSV structure")
                return None, None
            
            # Remove any non-string entries and clean up
            names = [str(name) for name in names if str(name).strip() and str(name) != 'nan']
            
            st.success(f"✅ Loaded {len(names)} movies from database")
            return df, names
        else:
            return None, None
    except Exception as e:
        st.error(f"Failed to initialize data: {str(e)}")
        return None, None

# Initialize data
with st.spinner("🚀 Initializing CinemaScope..."):
    data_init = initialize_data()

if data_init[0] is not None:
    df, names = data_init
else:
    st.stop()  # Stop execution if data couldn't be loaded

tmdb_genres = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def fetch_movie_data(start, end):
    """Fetch movie data from TMDB API with error handling and timeout"""
    api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
    movies = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_movies = end - start
    failed_requests = 0
    max_failures = 5  # Stop if too many failures
    
    for idx, movie in enumerate(names[start:end]):
        try:
            url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie}'
            response = requests.get(
                url, 
                timeout=(5, 15),  # 5s connection, 15s read timeout
                headers={'User-Agent': 'CinemaScope/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    movies.append(data['results'][0])
                failed_requests = 0  # Reset failure counter on success
            else:
                failed_requests += 1
                if failed_requests > max_failures:
                    st.warning("Too many API failures. Stopping data fetch.")
                    break
            
            # Update progress
            progress = (idx + 1) / total_movies
            progress_bar.progress(progress)
            status_text.text(f'Loading movies... {idx + 1}/{total_movies} (Failures: {failed_requests})')
            
        except requests.exceptions.Timeout:
            failed_requests += 1
            st.warning(f"Timeout fetching data for '{movie}'")
            if failed_requests > max_failures:
                break
        except Exception as e:
            failed_requests += 1
            if failed_requests <= max_failures:
                continue
            else:
                break
    
    progress_bar.empty()
    status_text.empty()
    
    if failed_requests > 0:
        st.info(f"⚠️ Note: {failed_requests} movies failed to load due to API issues")
    
    return movies

def get_movie_recommendations(movie_title):
    """Get movie recommendations based on cosine similarity"""
    if not movie_title or df is None:
        return []
        
    try:
        # Clean the movie title for better matching
        movie_title = str(movie_title).strip()
        
        # Method 1: Check if movie_title is in the columns (typical cosine similarity matrix)
        if movie_title in df.columns:
            # Get similarity scores for this movie
            if movie_title in df.index:
                similarity_scores = df.loc[movie_title]
            else:
                # Try to find the row that best represents this movie
                similarity_scores = df[movie_title]
            
            # Get top similar movies
            if hasattr(similarity_scores, 'sort_values'):
                similar_movies = similarity_scores.sort_values(ascending=False).head(6)
                recommended_movies = [name for name in similar_movies.index 
                                    if name != movie_title and str(name).strip()][:5]
            else:
                import numpy as np
                similar_indices = np.argsort(similarity_scores.values)[-6:][::-1]
                all_movie_names = df.columns.tolist()
                recommended_movies = [all_movie_names[i] for i in similar_indices 
                                    if i < len(all_movie_names) and all_movie_names[i] != movie_title][:5]
            
            return recommended_movies
        
        # Method 2: Check if movie_title is in the index
        elif movie_title in df.index:
            similarity_scores = df.loc[movie_title]
            similar_movies = similarity_scores.sort_values(ascending=False).head(6)
            recommended_movies = [name for name in similar_movies.index 
                                if name != movie_title and str(name).strip()][:5]
            return recommended_movies
        
        # Method 3: Try fuzzy matching for slight name differences
        else:
            # Look for partial matches in columns
            possible_matches = [col for col in df.columns if movie_title.lower() in col.lower()]
            if possible_matches:
                best_match = possible_matches[0]
                return get_movie_recommendations(best_match)
            
            # Look for partial matches in index
            possible_matches = [idx for idx in df.index if movie_title.lower() in str(idx).lower()]
            if possible_matches:
                best_match = possible_matches[0]
                return get_movie_recommendations(best_match)
                
    except Exception as e:
        st.warning(f"Error getting recommendations for '{movie_title}': {str(e)}")
            
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
        
        # Use the movie title to get recommendations
        movie_title_for_search = movie.get('title', movie.get('original_title', ''))
        recommended_movies = get_movie_recommendations(movie_title_for_search)
        
        if recommended_movies:
            for rec_movie in recommended_movies[:5]:  # Limit to top 5
                try:
                    api_key = os.getenv("TMDB_API_KEY", "bba4fededdbeac099653cc18b878503d")
                    rec_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={rec_movie}'
                    rec_response = requests.get(
                        rec_url, 
                        timeout=(5, 10),
                        headers={'User-Agent': 'CinemaScope/1.0'}
                    )
                    
                    if rec_response.status_code == 200:
                        rec_data = rec_response.json()
                        if rec_data['results']:
                            rec_movie_detail = rec_data['results'][0]
                            
                            # Safe string formatting for release date
                            release_info = ""
                            if rec_movie_detail.get('release_date'):
                                try:
                                    release_year = rec_movie_detail['release_date'][:4]
                                    release_info = f" ({release_year})"
                                except:
                                    release_info = ""
                            
                            with st.expander(f"🎬 {rec_movie_detail['title']}{release_info}"):
                                display_movie_card(rec_movie_detail, show_recommendations=False)
                        else:
                            # Show basic recommendation even if TMDB doesn't have details
                            with st.expander(f"🎬 {rec_movie} (Recommended)"):
                                st.write(f"**Movie:** {rec_movie}")
                                st.write("*Details not available from TMDB database*")
                    else:
                        # Show basic recommendation if API call failed
                        with st.expander(f"🎬 {rec_movie} (Recommended)"):
                            st.write(f"**Movie:** {rec_movie}")
                            st.write("*Unable to fetch additional details*")
                            
                except requests.exceptions.Timeout:
                    with st.expander(f"🎬 {rec_movie} (Recommended)"):
                        st.write(f"**Movie:** {rec_movie}")
                        st.write("*Timeout loading details*")
                except Exception as e:
                    # Still show the recommendation even if we can't get details
                    with st.expander(f"🎬 {rec_movie} (Recommended)"):
                        st.write(f"**Movie:** {rec_movie}")
                        st.write(f"*Error loading details: {str(e)}*")
        else:
            st.info("💡 No recommendations found. This movie might not be in our similarity database, or try searching for a different title variation.")
                                                            display_movie_card(rec_movie_detail, show_recommendations=False)
                        else:
                            st.warning(f"No details found for recommended movie: {rec_movie}")
                except requests.exceptions.Timeout:
                    st.warning(f"Timeout loading details for '{rec_movie}'")
                except Exception as e:
                    st.error(f"Failed to fetch details for '{rec_movie}': {str(e)}")
        else:
            st.info("No recommendations found. This might be due to the movie not being in our similarity database.")
            st.write(f"Debug: Searched for '{movie_title_for_search}' in recommendations database")

def main():
    """Main application function"""
    # Check if data is loaded
    if df is None:
        st.error("❌ Movie database could not be loaded. Please refresh the page.")
        st.stop()
    
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
            with st.spinner(f"🔍 Searching for '{search_query}'..."):
                response = requests.get(
                    search_url, 
                    timeout=(5, 15),
                    headers={'User-Agent': 'CinemaScope/1.0'}
                )
                
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    st.success(f"Found movie: {data['results'][0]['title']}")
                    display_movie_card(data['results'][0], show_recommendations=True)
                else:
                    st.warning("No movies found matching your search.")
            else:
                st.error("Failed to search for movies. Please try again.")
        except requests.exceptions.Timeout:
            st.error("Search timed out. Please check your connection and try again.")
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
            response = requests.get(
                url, 
                timeout=(5, 15),
                headers={'User-Agent': 'CinemaScope/1.0'}
            )
            
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
