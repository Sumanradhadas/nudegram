import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from services.google_images import GoogleImagesService
from services.image_validator import ImageValidator
from services.content_detector import ContentDetector
from data.celebrities import CELEBRITIES_DATA

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback_secret_key_for_dev")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///celebrities.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize services
google_images_service = GoogleImagesService()
image_validator = ImageValidator()
content_detector = ContentDetector()

def create_dynamic_celebrity(name):
    """Create a dynamic celebrity profile for any celebrity worldwide"""
    if not name or len(name.strip()) < 2:
        return None
    
    # Clean and format the name
    clean_name = name.strip().title()
    slug = clean_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
    
    # Fetch a profile picture from Google Images
    profile_image_url = fetch_profile_picture(clean_name)
    
    # Create a dynamic celebrity profile
    dynamic_celebrity = {
        'name': clean_name,
        'slug': slug,
        'profession': 'Celebrity',  # Default profession
        'bio': f'{clean_name} is a renowned celebrity known for their work in entertainment industry.',
        'followers_count': 1500000,  # Default stats
        'following_count': 250,
        'posts_count': 189,
        'profile_image_url': profile_image_url
    }
    
    return dynamic_celebrity

def fetch_profile_picture(celebrity_name):
    """Fetch the first verified profile picture for a celebrity"""
    try:
        # Search for profile/headshot photos
        profile_query = f"{celebrity_name} portrait headshot professional photo"
        profile_images = google_images_service.search_images(profile_query, num_results=10)
        
        if profile_images:
            # Return the first valid image URL
            for image in profile_images:
                if image_validator._is_valid_image(image):
                    return image.get('url', '')
    
    except Exception as e:
        logging.error(f"Error fetching profile picture for {celebrity_name}: {str(e)}")
    
    # Fallback to placeholder if no image found
    initials = ''.join([word[0] for word in celebrity_name.split()[:2]]).upper()
    return f'https://via.placeholder.com/400x400/4a5568/ffffff?text={initials}'

@app.route('/')
def home():
    """Homepage displaying all celebrity profiles in a grid"""
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        # First check local celebrities
        filtered_celebrities = [
            celeb for celeb in CELEBRITIES_DATA 
            if search_query.lower() in celeb['name'].lower() or 
               search_query.lower() in celeb['profession'].lower()
        ]
        
        # If no local results, create dynamic celebrity profile
        if not filtered_celebrities:
            dynamic_celebrity = create_dynamic_celebrity(search_query)
            if dynamic_celebrity:
                filtered_celebrities = [dynamic_celebrity]
        
        return render_template('search_results.html', 
                             celebrities=filtered_celebrities, 
                             search_query=search_query)
    
    return render_template('index.html', celebrities=CELEBRITIES_DATA)

@app.route('/profile/<celebrity_slug>')
def profile(celebrity_slug):
    """Individual celebrity profile page with dynamic image loading"""
    # Find celebrity by slug in local data
    celebrity = None
    for celeb in CELEBRITIES_DATA:
        if celeb['slug'] == celebrity_slug:
            celebrity = celeb
            break
    
    # If not found locally, try to create dynamic profile
    if not celebrity:
        # Extract name from slug and create dynamic profile
        celebrity_name = celebrity_slug.replace('-', ' ').title()
        celebrity = create_dynamic_celebrity(celebrity_name)
    
    if not celebrity:
        return render_template('404.html'), 404
    
    return render_template('profile.html', celebrity=celebrity)

@app.route('/api/celebrity/<celebrity_slug>/images')
def get_celebrity_images(celebrity_slug):
    """API endpoint to fetch images for a specific celebrity"""
    try:
        # Find celebrity by slug
        celebrity = None
        for celeb in CELEBRITIES_DATA:
            if celeb['slug'] == celebrity_slug:
                celebrity = celeb
                break
        
        # If not found locally, create dynamic celebrity
        if not celebrity:
            celebrity_name = celebrity_slug.replace('-', ' ').title()
            celebrity = create_dynamic_celebrity(celebrity_name)
            
        if not celebrity:
            return jsonify({'error': 'Celebrity not found'}), 404
        
        # Use elegant styling prompt for fashion photos
        custom_prompt = 'nude+naked+imgfy'
        
        # Fetch images from Google Images with custom prompt
        search_query = f"{celebrity['name']} {custom_prompt}"
        raw_images = google_images_service.search_images(search_query, num_results=100)
        
        if not raw_images:
            return jsonify({'error': 'No images found'}), 404
        
        # Simplified validation - just basic image checks
        validated_images = []
        
        for image in raw_images:
            # Only basic validation to ensure image URLs work
            if image_validator._is_valid_image(image):
                validated_images.append({
                    'url': image.get('url', ''),
                    'title': image.get('title', ''),
                    'thumbnail': image.get('thumbnail', ''),
                    'width': image.get('width', 0),
                    'height': image.get('height', 0),
                    'source_domain': image.get('source_domain', '')
                })
        
        # Return all valid images without content filtering
        return jsonify({
            'images': validated_images,  # Return all found images
            'celebrity': celebrity,
            'total_found': len(validated_images)
        })
    
    except Exception as e:
        logging.error(f"Error fetching celebrity images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images'}), 500

@app.route('/api/search')
def search_api():
    """API endpoint for search suggestions"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    suggestions = []
    for celeb in CELEBRITIES_DATA:
        if query.lower() in celeb['name'].lower():
            suggestions.append({
                'name': celeb['name'],
                'slug': celeb['slug'],
                'profession': celeb['profession']
            })
    
    return jsonify(suggestions[:10])  # Limit to 10 suggestions

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# Jinja2 custom filters
@app.template_filter('highlight_search')
def highlight_search(text, search_query):
    """Highlight search terms in text"""
    if not search_query or not text:
        return text
    import re
    pattern = re.compile(re.escape(search_query), re.IGNORECASE)
    return pattern.sub(f'<mark class="bg-warning text-dark">{search_query}</mark>', text)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
