from fyyur import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


# Initialized without explicit app (Flask instance)
# db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


def convert_db_genres_to_list(genres):
    return genres[1:-1].split(',')


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def venue_to_dictionary(self):
        data = {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'address': self.address,
                'phone': self.phone,
                'genres': convert_db_genres_to_list(self.genres),
                'facebook_link': self.facebook_link,
                'image_link': self.image_link,
                'website': self.website,
                'seeking_talent': self.website,
                'seeking_description': self.seeking_description
                }
        return data


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def artist_to_dictionary(self):
        data = {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'phone': self.phone,
            'genres': convert_db_genres_to_list(self.genres),
            'facebook_link': self.facebook_link,
            'image_link': self.image_link,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description
        }
        return data


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())