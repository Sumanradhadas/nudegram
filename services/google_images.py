"""
Google Images search service for fetching celebrity images
"""
import os
import logging
import requests
from urllib.parse import urlencode

class GoogleImagesService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', 'default_api_key')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', 'default_search_engine_id')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    def search_images(self, query, num_results=10):
        """
        Search for images using Google Custom Search API
        
        Args:
            query (str): Search query for images
            num_results (int): Number of results to return (max 10 per request)
            
        Returns:
            list: List of image dictionaries with url, title, thumbnail, etc.
        """
        try:
            # Parameters for Google Custom Search API - Simplified with fewer restrictions
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'searchType': 'image',
                'num': min(num_results, 10),  # Google API limits to 10 per request
                'safe': 'off',  # Disable safe search for broader results
                'imgSize': 'large',  # Prefer larger images
                'imgColorType': 'color',  # Color images preferred
            }
            
            # For higher limits, make multiple requests
            all_images = []
            start_index = 1
            
            while len(all_images) < num_results and start_index <= 91:  # Google allows up to 100 results
                params['start'] = start_index
                params['num'] = min(10, num_results - len(all_images))
            
                logging.debug(f"Searching Google Images for: {query} (batch {start_index})")
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if 'items' not in data:
                    break  # No more results
                
                # Process and format results for this batch
                batch_images = []
                for item in data['items']:
                    image_data = {
                        'url': item.get('link', ''),
                        'title': item.get('title', ''),
                        'thumbnail': item.get('image', {}).get('thumbnailLink', ''),
                        'width': item.get('image', {}).get('width', 0),
                        'height': item.get('image', {}).get('height', 0),
                        'size': item.get('image', {}).get('byteSize', 0),
                        'context_url': item.get('image', {}).get('contextLink', ''),
                        'source_domain': self._extract_domain(item.get('displayLink', '')),
                        'mime_type': item.get('mime', ''),
                    }
                    
                    # Only include valid images
                    if image_data['url'] and self._is_valid_image_url(image_data['url']):
                        batch_images.append(image_data)
                
                all_images.extend(batch_images)
                start_index += 10  # Move to next batch
                
                # If we got fewer than 10 results, we've reached the end
                if len(data.get('items', [])) < 10:
                    break
            
            logging.info(f"Found {len(all_images)} valid images for query: {query}")
            return all_images
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error searching for images: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error searching for images: {str(e)}")
            return []
    
    def _is_valid_image_url(self, url):
        """Check if URL appears to be a valid image"""
        if not url:
            return False
            
        # Check for common image extensions
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
        url_lower = url.lower()
        
        # Check if URL ends with image extension or contains image format indicators
        return any(ext in url_lower for ext in valid_extensions)
    
    def _extract_domain(self, url):
        """Extract domain from URL for source attribution"""
        if not url:
            return ''
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            return parsed.netloc
        except:
            return url
