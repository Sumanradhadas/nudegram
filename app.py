import os
import logging
import requests
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from io import BytesIO
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
    if not name or len(name.strip()) < 2:
        return None
    clean_name = name.strip().title()
    slug = clean_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
    profile_image_url = fetch_profile_picture(clean_name)
    return {
        'name': clean_name,
        'slug': slug,
        'profession': 'Celebrity',
        'bio': f'{clean_name} is a renowned celebrity known for their work in entertainment industry.',
        'followers_count': 1500000,
        'following_count': 250,
        'posts_count': 189,
        'profile_image_url': profile_image_url
    }

def fetch_profile_picture(celebrity_name):
    try:
        profile_query = f"{celebrity_name} site:imdb.com"
        profile_images = google_images_service.search_images(profile_query, num_results=10)
        if profile_images:
            for image in profile_images:
                url = image.get('url', '')
                if 'imdb.com' in url and image_validator._is_valid_image(image):
                    return f"/proxy?url={url}"
    except Exception as e:
        logging.error(f"Error fetching IMDb profile picture for {celebrity_name}: {str(e)}")
    initials = ''.join([word[0] for word in celebrity_name.split()[:2]]).upper()
    return f'https://via.placeholder.com/400x400/4a5568/ffffff?text={initials}'

@app.route('/')
def home():
    search_query = request.args.get('search', '').strip()
    if search_query:
        filtered_celebrities = [
            celeb for celeb in CELEBRITIES_DATA 
            if search_query.lower() in celeb['name'].lower() or 
               search_query.lower() in celeb['profession'].lower()
        ]
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
    celebrity = next((celeb for celeb in CELEBRITIES_DATA if celeb['slug'] == celebrity_slug), None)
    if not celebrity:
        celebrity_name = celebrity_slug.replace('-', ' ').title()
        celebrity = create_dynamic_celebrity(celebrity_name)
    if not celebrity:
        return render_template('404.html'), 404
    return render_template('profile.html', celebrity=celebrity)

@app.route('/api/celebrity/<celebrity_slug>/images')
def get_celebrity_images(celebrity_slug):
    try:
        celebrity = next((celeb for celeb in CELEBRITIES_DATA if celeb['slug'] == celebrity_slug), None)
        if not celebrity:
            celebrity_name = celebrity_slug.replace('-', ' ').title()
            celebrity = create_dynamic_celebrity(celebrity_name)
        if not celebrity:
            return jsonify({'error': 'Celebrity not found'}), 404
        custom_prompt = 'nude+naked+imgfy'
        search_query = f"{celebrity['name']} {custom_prompt}"
        raw_images = google_images_service.search_images(search_query, num_results=100)
        if not raw_images:
            return jsonify({'error': 'No images found'}), 404
        validated_images = []
        for image in raw_images:
            if image_validator._is_valid_image(image):
                url = image.get('url', '')
                domain = image.get('source_domain', '').lower()
                if any(social in domain for social in [
                    'instagram.com', 'facebook.com', 'youtube.com', 
                    'ytimg.com', 'fbcdn.net', 'tiktok.com', 'pinterest.com'
                ]):
                    continue
                validated_images.append({
                    'url': f"/proxy?url={url}",
                    'title': image.get('title', ''),
                    'thumbnail': image.get('thumbnail', ''),
                    'width': image.get('width', 0),
                    'height': image.get('height', 0),
                    'source_domain': domain
                })
        return jsonify({
            'images': validated_images,
            'celebrity': celebrity,
            'total_found': len(validated_images)
        })
    except Exception as e:
        logging.error(f"Error fetching celebrity images: {str(e)}")
        return jsonify({'error': 'Failed to fetch images'}), 500

@app.route('/api/search')
def search_api():
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
    return jsonify(suggestions[:10])

@app.route('/proxy')
def proxy_image():
    """Proxy image to bypass CORS and CORP"""
    image_url = request.args.get('url')
    if not image_url:
        return "Missing image URL", 400
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        return send_file(BytesIO(response.content), mimetype=content_type)
    except Exception as e:
        logging.error(f"Proxy error: {str(e)}")
        return "Failed to load image", 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

@app.template_filter('highlight_search')
def highlight_search(text, search_query):
    if not search_query or not text:
        return text
    import re
    pattern = re.compile(re.escape(search_query), re.IGNORECASE)
    return pattern.sub(f'<mark class="bg-warning text-dark">{search_query}</mark>', text)

with app.app_context():
    import models
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
