# Celebrity Discovery Platform

## Overview

A Flask-based web application that allows users to discover and explore celebrity profiles with AI-powered image detection and validation. The platform features a grid-based interface displaying celebrity information with professional photo galleries, real-time search capabilities, and intelligent content detection to ensure high-quality, appropriate celebrity images.

## User Preferences

Preferred communication style: Simple, everyday language.
Search functionality: Global celebrity discovery with unlimited results
Image filtering: Minimal content restrictions, focus on fashion/style images
Gallery layout: Instagram-style vertical feed presentation

## System Architecture

### Web Framework
- **Flask**: Core web framework chosen for its simplicity and flexibility in building small to medium-scale web applications
- **Flask-SQLAlchemy**: ORM integration for database operations, providing a clean abstraction layer over raw SQL queries
- **Jinja2 Templates**: Server-side templating for dynamic HTML generation with template inheritance and custom filters
- **ProxyFix Middleware**: Handles reverse proxy headers for proper request handling in deployment environments

### Frontend Architecture
- **Bootstrap 5**: CSS framework for responsive design and pre-built UI components with dark theme support
- **Font Awesome**: Icon library for consistent iconography across the interface
- **Vanilla JavaScript**: Client-side interactivity without additional framework overhead, focusing on performance
- **CSS Grid/Flexbox**: Modern layout techniques for responsive celebrity profile grids and image galleries

### Database Design
- **SQLite/PostgreSQL**: Flexible database configuration with SQLite for development and PostgreSQL production support
- **Celebrity Model**: Core entity storing name, slug, profession, bio, social metrics, and profile images
- **CelebrityImage Model**: Separate table for managing multiple validated images per celebrity with metadata
- **Relationship Design**: One-to-many relationship between celebrities and their associated images with proper foreign key constraints

### Content Management
- **Static Data Integration**: Celebrity information stored in Python dictionaries for quick access without database queries
- **Hybrid Data Strategy**: Static celebrity profiles combined with dynamic image galleries for optimal performance
- **Image URL Management**: External image hosting via Unsplash for profile pictures with face-cropped optimization

### Search and Discovery
- **Global Celebrity Search**: Dynamic search system that can find any celebrity worldwide, not limited to preset database
- **Real-time Profile Creation**: Automatically creates celebrity profiles for any searched name with dynamic image fetching
- **Search Suggestions**: Dynamic suggestion system with keyboard navigation support and autocomplete
- **Query Optimization**: Search across both celebrity names and professions for comprehensive results
- **Responsive Grid Layout**: Adaptive celebrity card layout that works across all device sizes

### AI-Powered Image Services
- **Google Custom Search Integration**: Primary image discovery mechanism with batch processing for up to 100 images per celebrity
- **Simplified Image Validation**: Basic validation system focusing on image accessibility and URL validity
- **Dynamic Profile Pictures**: Automatic fetching of verified profile pictures for any celebrity using portrait/headshot searches
- **Fashion-Focused Search**: Specialized search using "black dress elegant style fashion" terms for targeted image discovery
- **Instagram-Style Gallery**: Vertical feed layout displaying images in social media post format with headers and metadata

### Error Handling and User Experience
- **Custom Error Pages**: Dedicated 404 and 500 error templates with helpful navigation and suggestions
- **Progressive Image Loading**: Lazy loading implementation for optimal page performance
- **Loading States**: Visual feedback during image fetching and processing operations
- **Graceful Degradation**: Fallback mechanisms for when external services are unavailable

## External Dependencies

### API Integrations
- **Google Custom Search API**: Primary service for discovering celebrity images with advanced search parameters and usage rights filtering
- **Computer Vision APIs**: Ready integration points for Google Vision AI, AWS Rekognition, and Azure Computer Vision for face detection and content analysis
- **Unsplash API**: Fallback image service providing high-quality, face-cropped profile pictures with proper attribution

### CDN and Static Assets
- **Bootstrap CDN**: CSS framework delivery with custom agent dark theme for consistent UI
- **Font Awesome CDN**: Icon library for scalable vector icons across the interface
- **Image Hosting Services**: External image URLs from various sources with validation and accessibility checks

### Development and Deployment
- **Environment Configuration**: Support for multiple deployment environments with configurable database URLs and API keys
- **Session Management**: Secure session handling with configurable secret keys for user state management
- **Database Migration Support**: SQLAlchemy integration ready for database schema evolution and deployment scaling