"""
Image validation service for content filtering and quality checks
"""
import logging
import requests
from urllib.parse import urlparse
import time

class ImageValidator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def validate_image_content(self, image_url, celebrity_name):
        """
        Validate image content for appropriateness and relevance
        
        Args:
            image_url (str): URL of the image to validate
            celebrity_name (str): Name of the celebrity for relevance checking
            
        Returns:
            dict: Validation results with scores and details
        """
        result = {
            'is_valid': False,
            'is_appropriate': False,
            'is_relevant': False,
            'face_detected': False,
            'content_score': 0.0,
            'validation_details': {},
            'error_message': None
        }
        
        try:
            # Basic URL and accessibility validation
            if not self._is_accessible_url(image_url):
                result['error_message'] = 'Image URL is not accessible'
                return result
            
            # Simulate face detection (would use real API in production)
            face_detection = self._simulate_face_detection(image_url)
            result['face_detected'] = face_detection['detected']
            result['validation_details']['face_confidence'] = face_detection['confidence']
            
            # Content appropriateness check
            content_check = self._check_content_appropriateness(image_url)
            result['is_appropriate'] = content_check['appropriate']
            result['validation_details']['content_safety'] = content_check['safety_score']
            
            # Celebrity relevance check
            relevance_check = self._check_celebrity_relevance(image_url, celebrity_name)
            result['is_relevant'] = relevance_check['relevant']
            result['validation_details']['relevance_score'] = relevance_check['score']
            
            # Calculate overall content score
            result['content_score'] = self._calculate_content_score(
                face_detection['confidence'],
                content_check['safety_score'],
                relevance_check['score']
            )
            
            # Image is valid if it passes all checks
            result['is_valid'] = (
                result['face_detected'] and 
                result['is_appropriate'] and 
                result['is_relevant'] and
                result['content_score'] > 0.6
            )
            
        except Exception as e:
            logging.error(f"Error validating image {image_url}: {str(e)}")
            result['error_message'] = str(e)
            
        return result
    
    def _is_valid_image(self, image_data):
        """Basic validation of image data structure"""
        if not isinstance(image_data, dict):
            return False
            
        url = image_data.get('url', '')
        if not url:
            return False
            
        # Check for reasonable image dimensions
        width = image_data.get('width', 0)
        height = image_data.get('height', 0)
        
        if width < 200 or height < 200:  # Minimum size requirement
            return False
            
        if width > 5000 or height > 5000:  # Maximum size limit
            return False
            
        return True
    
    def _is_accessible_url(self, url):
        """Check if image URL is accessible"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _simulate_face_detection(self, image_url):
        """
        Simulate face detection API call
        In production, this would integrate with Google Vision, AWS Rekognition, or Azure Computer Vision
        """
        try:
            # Simulate API processing time
            time.sleep(0.1)
            
            # Simulate face detection results based on URL characteristics
            # In real implementation, this would analyze the actual image
            url_lower = image_url.lower()
            
            # Higher confidence for URLs that likely contain faces
            confidence = 0.85 if any(keyword in url_lower for keyword in ['face', 'portrait', 'headshot', 'person']) else 0.75
            
            return {
                'detected': confidence > 0.7,
                'confidence': confidence,
                'face_count': 1 if confidence > 0.7 else 0
            }
        except Exception as e:
            logging.error(f"Face detection simulation error: {str(e)}")
            return {'detected': False, 'confidence': 0.0, 'face_count': 0}
    
    def _check_content_appropriateness(self, image_url):
        """
        Check if image content is appropriate
        In production, this would use content moderation APIs
        """
        try:
            # Simulate content safety analysis
            time.sleep(0.05)
            
            # Analyze URL for inappropriate content indicators
            url_lower = image_url.lower()
            inappropriate_keywords = ['adult', 'nsfw', 'explicit', 'nude']
            
            # High safety score if no inappropriate keywords found
            safety_score = 0.95 if not any(keyword in url_lower for keyword in inappropriate_keywords) else 0.3
            
            return {
                'appropriate': safety_score > 0.8,
                'safety_score': safety_score,
                'flags': []
            }
        except Exception as e:
            logging.error(f"Content appropriateness check error: {str(e)}")
            return {'appropriate': True, 'safety_score': 0.8, 'flags': []}
    
    def _check_celebrity_relevance(self, image_url, celebrity_name):
        """
        Check if image is relevant to the celebrity
        In production, this could use image recognition APIs
        """
        try:
            # Simulate relevance scoring
            time.sleep(0.05)
            
            # Simple relevance check based on URL context
            url_lower = image_url.lower()
            name_parts = celebrity_name.lower().split()
            
            # Check if celebrity name appears in URL or context
            relevance_score = 0.8
            if any(part in url_lower for part in name_parts if len(part) > 3):
                relevance_score = 0.9
            
            return {
                'relevant': relevance_score > 0.7,
                'score': relevance_score,
                'matched_terms': name_parts
            }
        except Exception as e:
            logging.error(f"Celebrity relevance check error: {str(e)}")
            return {'relevant': True, 'score': 0.8, 'matched_terms': []}
    
    def _calculate_content_score(self, face_confidence, safety_score, relevance_score):
        """Calculate weighted content score"""
        # Weighted average: face detection (40%), safety (35%), relevance (25%)
        return (face_confidence * 0.4) + (safety_score * 0.35) + (relevance_score * 0.25)
