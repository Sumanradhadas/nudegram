"""
Content detection service for matching images to specific prompts
"""
import logging
import time
import requests

class ContentDetector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def detect_content(self, image_url, content_prompt):
        """
        Detect if image matches the specified content prompt
        
        Args:
            image_url (str): URL of the image to analyze
            content_prompt (str): Content description to match against
            
        Returns:
            dict: Detection results with confidence and details
        """
        result = {
            'content_detected': False,
            'confidence': 0.0,
            'matched_elements': [],
            'analysis_details': {},
            'error_message': None
        }
        
        try:
            # Simulate content detection API call
            # In production, this would use computer vision APIs like Google Vision AI,
            # AWS Rekognition, or Azure Computer Vision
            
            detection_result = self._simulate_content_detection(image_url, content_prompt)
            
            result.update(detection_result)
            
        except Exception as e:
            logging.error(f"Error detecting content in image {image_url}: {str(e)}")
            result['error_message'] = str(e)
            
        return result
    
    def _simulate_content_detection(self, image_url, content_prompt):
        """
        Simulate content detection API
        In production, this would analyze the actual image content
        """
        try:
            # Simulate API processing time
            time.sleep(0.1)
            
            # Parse content prompt for key elements
            prompt_lower = content_prompt.lower()
            prompt_keywords = prompt_lower.split()
            
            # Analyze URL for content indicators
            url_lower = image_url.lower()
            
            matched_elements = []
            confidence_scores = []
            
            # Check for professional/quality indicators
            if 'professional' in prompt_lower:
                if any(term in url_lower for term in ['photoshoot', 'portrait', 'professional', 'studio']):
                    matched_elements.append('professional_quality')
                    confidence_scores.append(0.9)
                else:
                    confidence_scores.append(0.7)  # Default professional score
            
            # Check for photo-specific terms
            if 'photo' in prompt_lower:
                if any(term in url_lower for term in ['photo', 'image', 'pic', 'jpg', 'jpeg', 'png']):
                    matched_elements.append('photo_format')
                    confidence_scores.append(0.95)
                else:
                    confidence_scores.append(0.8)
            
            # Check for quality indicators
            if 'high quality' in prompt_lower or 'quality' in prompt_lower:
                # Assume higher quality for certain domains/contexts
                if any(domain in url_lower for domain in ['getty', 'shutterstock', 'unsplash', 'pexels']):
                    matched_elements.append('high_quality')
                    confidence_scores.append(0.9)
                else:
                    confidence_scores.append(0.75)
            
            # Calculate overall confidence
            if confidence_scores:
                overall_confidence = sum(confidence_scores) / len(confidence_scores)
            else:
                overall_confidence = 0.7  # Default confidence
            
            # Content is detected if confidence is above threshold
            content_detected = overall_confidence > 0.65
            
            return {
                'content_detected': content_detected,
                'confidence': overall_confidence,
                'matched_elements': matched_elements,
                'analysis_details': {
                    'prompt_keywords': prompt_keywords,
                    'confidence_breakdown': dict(zip(matched_elements, confidence_scores)),
                    'url_indicators': self._extract_url_indicators(url_lower)
                }
            }
            
        except Exception as e:
            logging.error(f"Content detection simulation error: {str(e)}")
            return {
                'content_detected': False,
                'confidence': 0.0,
                'matched_elements': [],
                'analysis_details': {'error': str(e)}
            }
    
    def _extract_url_indicators(self, url_lower):
        """Extract indicators from URL that suggest content type"""
        indicators = []
        
        # Quality indicators
        quality_terms = ['hd', 'high-res', 'professional', 'studio', 'photoshoot']
        for term in quality_terms:
            if term in url_lower:
                indicators.append(f'quality_{term}')
        
        # Format indicators
        format_terms = ['jpg', 'jpeg', 'png', 'webp']
        for term in format_terms:
            if term in url_lower:
                indicators.append(f'format_{term}')
        
        # Source indicators
        source_terms = ['getty', 'shutterstock', 'unsplash', 'pexels', 'pixabay']
        for term in source_terms:
            if term in url_lower:
                indicators.append(f'source_{term}')
        
        return indicators
