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

@app.route('/')
def home():
    """Homepage displaying all celebrity profiles in a grid"""
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        # Filter celebrities based on search query
        filtered_celebrities = [
            celeb for celeb in CELEBRITIES_DATA 
            if search_query.lower() in celeb['name'].lower() or 
               search_query.lower() in celeb['profession'].lower()
        ]
        return render_template('search_results.html', 
                             celebrities=filtered_celebrities, 
                             search_query=search_query)
    
    return render_template('index.html', celebrities=CELEBRITIES_DATA)

@app.route('/profile/<celebrity_slug>')
def profile(celebrity_slug):
    """Individual celebrity profile page with dynamic image loading"""
    # Find celebrity by slug
    celebrity = None
    for celeb in CELEBRITIES_DATA:
        if celeb['slug'] == celebrity_slug:
            celebrity = celeb
            break
    
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
        
        if not celebrity:
            return jsonify({'error': 'Celebrity not found'}), 404
        
        # Use default prompt for high-quality professional photos
        custom_prompt = 'professional photos high quality'
        
        # Fetch images from Google Images with custom prompt
        search_query = f"{celebrity['name']} actress {custom_prompt}"
        raw_images = google_images_service.search_images(search_query, num_results=20)
        
        if not raw_images:
            return jsonify({'error': 'No images found'}), 404
        
        # Validate and filter images with enhanced detection
        validated_images = []
        detection_stats = {
            'total_checked': len(raw_images),
            'face_detected': 0,
            'content_appropriate': 0,
            'content_matched': 0,
            'relevant': 0,
            'final_approved': 0
        }
        
        for image in raw_images:
            # Basic validation first
            if image_validator._is_valid_image(image):
                # Advanced content validation with detection
                validation_result = image_validator.validate_image_content(
                    image.get('url', ''), 
                    celebrity['name']
                )
                
                # Content detection for specific prompt
                content_result = content_detector.detect_content(
                    image.get('url', ''), 
                    custom_prompt
                )
                
                # Update stats
                if validation_result['face_detected']:
                    detection_stats['face_detected'] += 1
                if validation_result['is_appropriate']:
                    detection_stats['content_appropriate'] += 1
                if validation_result['is_relevant']:
                    detection_stats['relevant'] += 1
                if content_result['content_detected']:
                    detection_stats['content_matched'] += 1
                    
                # Only include images that pass all detection checks including content matching
                if (validation_result['is_valid'] and content_result['content_detected']):
                    image['detection_score'] = validation_result['content_score']
                    image['validation_details'] = validation_result['validation_details']
                    image['content_details'] = content_result
                    image['final_score'] = (validation_result['content_score'] + content_result['confidence']) / 2
                    validated_images.append(image)
                    detection_stats['final_approved'] += 1
        
        # Sort by final score (combination of quality and content matching)
        validated_images.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return jsonify({
            'celebrity': celebrity['name'],
            'search_prompt': custom_prompt,
            'search_query': search_query,
            'images': validated_images[:12],  # Limit to 12 best images
            'total_found': len(raw_images),
            'detection_stats': detection_stats,
            'validation_summary': f"Found {detection_stats['final_approved']} images matching '{custom_prompt}' with detected faces from {detection_stats['total_checked']} total images"
        })
        
    except Exception as e:
        logging.error(f"Error fetching images for {celebrity_slug}: {str(e)}")
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

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
