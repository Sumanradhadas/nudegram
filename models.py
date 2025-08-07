from app import db
from datetime import datetime

class Celebrity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    profession = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    profile_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Celebrity {self.name}>'

class CelebrityImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    celebrity_id = db.Column(db.Integer, db.ForeignKey('celebrity.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255))
    title = db.Column(db.String(200))
    source_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_validated = db.Column(db.Boolean, default=False)
    
    celebrity = db.relationship('Celebrity', backref=db.backref('images', lazy=True))
    
    def __repr__(self):
        return f'<CelebrityImage {self.id}>'
